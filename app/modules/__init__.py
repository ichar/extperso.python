# -*- coding: utf-8 -*-

import sys
import os
import re
import time
import threading
from imp import reload
from functools import wraps

from config import (
     CONNECTION, IsDebug, IsDeepDebug, IsTrace, IsDisableOutput, IsPrintExceptions,
     default_print_encoding, default_unicode, default_encoding, default_iso, cr,
     LOCAL_EASY_DATESTAMP, UTC_FULL_TIMESTAMP, DATE_STAMP,
     print_to, print_exception
     )

from app.database import database_config, BankPersoEngine
from app.utils import normpath, getToday, getTime, getDate, getDateOnly, checkDate, spent_time, isIterable
from app.core import Actions, Order
from app.types import *

from .preloader import BaseOpenwayPreloaderClass
from .loader import BaseIncomingLoader
from .order_check import BaseProcess as OrderCheck
from .order_generate import BaseProcess as OrderGenerate
from .order_merge import BaseProcess as OrderMerge
from .order_report import BaseProcess as OrderReport
from .unloader import BaseProcess as Unloader

from ext import global_scenario, filetypes_modules, ext_modules, command_scenario
from ext.defaults import *
from ext.filetypes import *
from ext.filetypes import registered_order_filetypes

import ext.loader
import ext.order_check
import ext.order_generate
import ext.order_merge
import ext.order_report
import ext.preloader
import ext.unloader

engines = {}

_database = 'bankperso'

connection = CONNECTION[_database]

default_template = 'orders'
default_change_filestatus = 'changefilestatus'

MOD_PRELOADER = 'preloader'
MOD_LOADER = 'loader'
MOD_ORDER_CHECK = 'order_check'
MOD_ORDER_GENERATE = 'order_generate'
MOD_ORDER_MERGE = 'order_merge'
MOD_ORDER_REPORT = 'order_report'
MOD_UNLOADER = 'unloader'

PROCESS_LOGGER_PREFIX = ''
CHECK_LOGGER_PREFIX = ''

basedir = ''

engine = None
logger = None
service = None
stdout = None

_messages = []
_errors = []

## =============
## MODULES: MAIN
## =============

def before(name):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kw):
            global engine
            if engine is not None:
                engine.close()
            engine = BankPersoEngine(name=name, user=None, connection=CONNECTION[name])
            return f(*args, **kw)
        return wrapper
    return decorator

def set_message(mid, msg, force=None):
    global _messages

    _messages.append((mid, getToday(), msg,))

    logger(msg, force=force)

def get_stdout():
    return stdout

def set_error(mid, msg, force=None):
    global _errors

    _errors.append((mid, getToday(), str(msg),))

    logger(msg, force=force)

def get_errors():
    return ['%s module[%s]: %s' % (getDate(t), m, s) for m, t, s in _errors]

def func_name(f, empty=None):
    return f is not None and callable(f) and f.__name__ or empty and ''

def mod_change_status(file_id, check_status, new_status, keep_history=None):
    engine.runProcedure(default_change_filestatus,
                        file_id=file_id,
                        check_file_status=check_status,
                        new_file_status=new_status,
                        keep_history=keep_history and 1 or 0,
                        no_cursor=True,
                        )
    return engine.engine_error

def sql_prop_filetype(filetype):
    return filetype == '*' and "FileType like '%%'" or "FileType='%s'" % filetype

def get_statuses(status_ids):
    status_from = len(status_ids) > 0 and status_ids[0] or None
    status_to = len(status_ids) > 1 and status_ids[1] or None
    status_error = len(status_ids) > 2 and status_ids[2] or None

    return status_from, status_to, status_error

def changeStatus(code, order, status_to, status_error, change_status=False, keep_history=False):
    #
    # Note! We should use `status_from` (check) equal with `status_to` (new) in order to
    # prevent removing of currently created record.
    #
    # See [dbo].[WEB_ChangeOrderState_sp]
    #
    status = STATUS_EMPTY
    error = False

    if code is None:
        pass

    elif code == HANDLER_CODE_SUCCESS and change_status:
        if status_to is not None:
            status = callable(status_to) and status_to(order) or status_to
            error = mod_change_status(order.id, status, status, keep_history=keep_history)

    elif code == HANDLER_CODE_ERROR and change_status:
        if status_error is not None:
            status = callable(status_error) and status_error(order) or status_error
            error = mod_change_status(order.id, status, status, keep_history=True)

    return status, error

def get_data_by_filetype(filetype, status_from):
    columns = database_config[default_template]['export']
    where = "%s and FileStatusID=%s" % (sql_prop_filetype(filetype), status_from)
    order = 'FileID'

    return engine.runQuery(default_template, columns=columns, where=where, order=order, as_dict=True,
                           encode_columns=('BankName','FileStatus'))

def get_data_by_id(id):
    columns = database_config[default_template]['export']
    where = "FileID=%s" % id

    return engine.runQuery(default_template, columns=columns, where=where, as_dict=True,
                           encode_columns=('BankName','FileStatus'))

## ============================
## Base Process Threading Class
## ============================

class Console(threading.Thread):
    
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, daemon=None):
        threading.Thread.__init__(self, group=group, target=target, name=name, daemon=daemon)

        self._basedir = len(args) > 0 and args[0] or kwargs and kwargs.get('basedir')
        self._logger = len(args) > 1 and args[1] or kwargs and kwargs.get('logger')
        self._config = len(args) > 2 and args[2] or kwargs and kwargs.get('config') or {}
        self._timeout = len(args) > 3 and args[3] or kwargs and kwargs.get('timeout') or 3
        self._service = len(args) > 4 and args[4] or kwargs and kwargs.get('service')
        self._lock = len(args) > 5 and args[5] or kwargs and kwargs.get('lock')

        self._deepdebug = self._config.get('deepdebug') and self._logger is not None and True or False

        self._should_be_stop = False
        self._running = False

        self._console = normpath(os.path.join(self._basedir, self._config.get('console')))

    def stop(self):
        pass

    def should_be_stop(self):
        self._should_be_stop = True

    def is_running(self):
        return self._running

    def is_finished(self):
        pass

    def get_size(self):
        if not (os.path.exists(self._console) and os.path.isfile(self._console)):
            c = open(self._console, 'w')
            c.close()

        return os.path.getsize(self._console)

    def check(self):
        return self._service is None and 'Service is not available!' or None

    def refresh(self):
        return self.check() or self._service.refresh()

    def restart(self):
        if self._service is None:
            return

        with self._lock:
            self._service.restart_requested = True

    def stop(self):
        if self._service is None:
            return

        self._service.stop()

    def run(self):
        global _messages
        
        line = ''
        output = True
        p = self.get_size()

        attrs = {'cr':cr, 'separator':'$', 'prompt':'-->', 'newline':cr, 'eol':cr}

        while not self._should_be_stop:
            if not output:
                time.sleep(self._timeout)

            self._running = True

            try:
                with open(self._console, 'r+') as c:
                    c.seek(p, 0)
                    command = line.strip()
                    line = ''

                    attrs['datetime'] = getDate(getToday(), UTC_FULL_TIMESTAMP)
                    attrs['msg'] = ''

                    if command:
                        if command == 'q':
                            c.write('%(newline)s%(datetime)s %(separator)s Quit%(eol)s' % attrs)
                            break
                        elif command[0] in 'm:e:a':
                            if command.startswith('m'):
                                messages = _messages
                                attrs['type'] = 'Message'
                            elif command.startswith('e'):
                                messages = _errors
                                attrs['type'] = 'Error'
                            else:
                                messages = _messages + _errors
                                attrs['type'] = 'Event'
                            n = len(command) > 1 and int(command[1:]) or 10
                            message = None
                            for message in messages[-n:]:
                                try:
                                    mid, timestamp, msg = message
                                    attrs['mid'] = mid
                                    attrs['datetime'] = getDate(timestamp, UTC_FULL_TIMESTAMP)
                                    attrs['msg'] = msg.strip()
                                    c.write('%(newline)s%(datetime)s %(separator)s %(type)s: %(msg)s' % attrs)
                                except Exception as ex:
                                    c.write('Unexpected Error: %s' % str(ex))
                            if message:
                                c.write(cr)
                        elif command == 's':
                            c.write('%(newline)s%(datetime)s %(separator)s Status: running...%(eol)s' % attrs)
                        elif command == 'u':
                            attrs['msg'] = self.refresh()
                            c.write('%(newline)s%(datetime)s %(separator)s Update: %(msg)s%(eol)s' % attrs)
                        elif command == 'r':
                            break

                    if output:
                        c.write('%(cr)sCommand: {{a|m|e}[N]|r|s|u|q} %(prompt)s ' % attrs)
                        p = c.tell()
                        output = False
                        continue

                    e = c.tell()
                    size = self.get_size() - p

                    if size > 0:
                        line = c.read(size)
                        p += size
                        output = True
            except:
                pass

        self._running = False

        if command == 'r':
            self.restart()

        elif command == 'q':
            self.stop()


class BaseService(threading.Thread):
    
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, daemon=None):
        threading.Thread.__init__(self, group=group, target=target, name=name, daemon=daemon)

        self._basedir = len(args) > 0 and args[0] or kwargs and kwargs.get('basedir')
        self._logger = len(args) > 1 and args[1] or kwargs and kwargs.get('logger')
        self._config = len(args) > 2 and args[2] or kwargs and kwargs.get('config') or {}
        self._lock = len(args) > 3 and args[3] or kwargs and kwargs.get('lock')

        self._debug = self._config.get('debug') and self._logger is not None and True or False
        self._deepdebug = self._config.get('deepdebug') and self._logger is not None and True or False
        self._printexceptions = self._config.get('printexceptions') and self._logger is not None and True or False

        if self._deepdebug:
            self._logger('>>> process init')

    def stop(self):
        if self._deepdebug:
            self._logger('>>> process stop')

    def should_be_stop(self):
        pass

    def is_finished(self):
        pass

    def get_config_param(self, key):
        value = None

        if self._deepdebug:
            self._logger('>>> get_config_param[%s], locked: %s' % (key, self._lock.locked()), force=True)
        
        with self._lock:
            value = self._config.get(key)

        if self._deepdebug:
            self._logger('>>> value[%s], locked: %s' % (value, self._lock.locked()), force=True)

        return value

    config = get_config_param

    def set_error(self, info, force=None):
        mid, msg, traceback = info
        set_error(re.sub(r'(\<class \')(.*)(\'\>)', r'\2', str(mid)), msg, force=force)

    def run(self):
        if self._deepdebug:
            self._logger('>>> process run[%s]' % self.ident)

        try:
            process(basedir=self._basedir, logger=self._logger, service=self.get_config_param, set_error=self.set_error)

        except Exception as ex:
            self.set_error(sys.exc_info(), force=True)

            if self._printexceptions:
                print_exception(1)

            self._logger('unexpected process exception (look at traceback.log)', is_error=True)


## ============
## STARTER ROOT
## ============

def command_parser(line):
    #
    #   Note: PochtaRuOnline, changePostOnline
    #
    #       id_config, filetype, status_ids, attrs
    #
    #   attrs:
    #   -----
    #       tags          : everything,
    #       custom        : postbank.change_delivery_date,
    #       forced        : 220666,
    #       attrs         : Dict, command specified
    #       change_status : 0,
    #
    if not line:
        return None

    scenario = []

    mid, item = '', []

    items = line.split('::')

    if len(items) != 4:
        return None

    def _add(command, mid, item):
        scenario.append((mid, item,))

        logger('--> command:%s[%s], item: %s' % (command, mid, item))

    command, filetype, statuses, attrs = items
    
    command = command.upper()
    statuses = statuses.split('-')
    attrs = eval(attrs)
    #
    #   <command>:<filetype>:<status_from>-<status_to>:<attrs>
    #
    if not attrs:
        command = None
    
    elif command == 'RUR':
        #
        #   Command: RepeatUnloadedReport.
        #
        #       id: command_scenario ID
        #
        #   debug mode:  
        #       RUR::PostBank_v1::198-0-0::['postbank_report',218288]
        #
        id, forced = attrs

        statuses = [int(x) for x in statuses]

        for mid, attrs, params in command_scenario.get(id) or []:
            if mid and attrs:
                attrs = eval(attrs)
                attrs.update({
                    'params': params,
                    'forced': forced,
                })
            else:
                continue

            _add(command, mid, [service('ID'), filetype, statuses, attrs])
    
    elif command == 'CSD':
        #
        #   Command: ChangeSendingDate.
        #
        #       params: {'date' : '23.10.2019', 'auto' : 1},
        #
        #   debug mode:  
        #       CSD::PostBank_v1::21-0-0::[everything,ext.order_generate.postbank.change_delivery_date,'23.10.2019',220666]
        #
        mid = MOD_ORDER_GENERATE

        if isinstance(attrs, list):
            tags, custom, date, forced = attrs
            attrs = {
                'tags'  : tags,
                'custom': custom,
                'params': {'date':date},
                'forced': forced,
                'phases': 2,
            }

        if not callable(attrs['custom']) or not isinstance(attrs.get('params'), dict) or not attrs.get('forced'):
            mid = None
        else:
            statuses = [int(x) for x in statuses]
            attrs['params']['auto'] = 1
            attrs['change_status'] = 0
            attrs['forced'] = int(attrs['forced'])

        _add(command, mid, [service('ID'), filetype, statuses, attrs])
    
    elif command == 'CDA':
        #
        #   Command: ChangeDeliveryAddress.
        #
        #       params: {'address' : '<text>', 'recno' : <FileRecNo>, 'branch' : <BRANCHDELIVERY>},
        #
        #   debug mode:  
        #       CDA::PostBank_v1::21-0-0::[everything,ext.order_generate.postbank.change_delivery_address,'357538,КРАЙ,СТАВРОПОЛЬСКИЙ,Г,ПЯТИГОРСК,УЛ УКРАИНСКАЯ,48А',None,'202001658',221690]
        #
        mid = MOD_ORDER_GENERATE

        if isinstance(attrs, list):
            tags, custom, address, recno, branch, forced = attrs
            attrs = {
                'tags'  : tags,
                'custom': custom,
                'params': {'address':address, 'recno':recno, 'branch':branch},
                'forced': forced,
            }

        if not callable(attrs['custom']) or not isinstance(attrs.get('params'), dict) or not attrs.get('forced'):
            mid = None
        else:
            statuses = [int(x) for x in statuses]
            attrs['change_status'] = 0
            attrs['forced'] = int(attrs['forced'])

        _add(command, mid, [service('ID'), filetype, statuses, attrs])

    return scenario


@before(_database)
def process(**kw):
    global basedir, logger, service

    basedir = kw.get('basedir')
    logger = kw.get('logger')
    service = kw.get('service')

    start = getToday()

    if IsDeepDebug:
        print(repr(sorted(connection.items(), key=lambda t: t[0])))

    logger('>>> engine: %s' % engine)

    # ---------------------------
    # Build Global Order Scenario
    # ---------------------------

    scenario = []

    def _reload_module(mid):
        _module = None

        # -----------------------------------
        # Reload module for sync code changes
        # -----------------------------------

        if mid:
            try:
                name = 'ext.%s' % mid

                if service is not None and service('reload') and name in sys.modules:
                    reload(sys.modules[name])
                    for m in ext_modules.get(mid):
                        reload(sys.modules['%s.%s' % (name, m)])

                _module = __import__(name, fromlist=['app', 'ext', 'scenario'] + (ext_modules.get(mid) or []))

            except:
                if IsPrintExceptions:
                    print_exception()

        return _module

    if service is not None and service('reload'):
        for f in filetypes_modules:
            name = 'ext.filetypes.%s' % f
            if name in sys.modules:
                reload(sys.modules[name])

    with_error = False

    if kw.get('command'):

        # ------------
        # Command Line
        # ------------

        command = command_parser(kw['command'])

        if command:
            scenario += command
    
        with_error = True
    
    else:

        # --------------------
        # Global Scenario Line
        # --------------------

        for mid in global_scenario:
            _module = _reload_module(mid)
        
            if _module is not None and hasattr(_module, 'scenario'):
                for item in _module.scenario:
                    if not isIterable(item):
                        continue
                    scenario.append((mid, item,))

    # ----------------------
    # Execute Scenario Items
    # ----------------------

    actions = Actions()
    
    done = False

    for mid, item in scenario:
        id_config, filetype, status_ids, attrs = item

        if service is not None and service('ID') != id_config:
            continue

        attrs['actions'] = actions
        attrs['engine'] = engine

        if not mid or not attrs or not isinstance(attrs, dict) or not filetype in registered_order_filetypes:
            continue

        logger('--> %s[%s], statuses: %s, attrs: %s' % (mid, filetype, status_ids, list(attrs.keys())))

        if mid == MOD_PRELOADER:
            done = process_preloader(mid, filetype, attrs)

        elif mid == MOD_LOADER:
            if not status_ids or status_ids[0] == STATUS_ON_INCOMING:
                done = process_reference(mid, filetype, attrs)
            else:
                done = process_incoming(mid, filetype, status_ids, attrs)

        elif mid == MOD_ORDER_MERGE:
            done = process_merge(mid, filetype, status_ids, attrs)

        elif mid == MOD_UNLOADER:
            done = process_exists(mid, filetype, status_ids, attrs)

        elif (len(status_ids) >= 2 and status_ids[0] > 0) or attrs.get('forced'):
            done = process_exists(mid, filetype, status_ids, attrs)

    run_actions(actions)

    finish = getToday()
    logger('>>> Spent time: %s sec' % spent_time(start, finish))

def process_preloader(mid, filetype, attrs):
    done = False

    if IsDebug and IsTrace:
        print('--> process_preloader: %s, filetype: %s' % (mid, filetype))

    if mid == MOD_PRELOADER:
        incoming = attrs.get('incoming')

        if incoming and isinstance(incoming, dict) and 'class' in incoming:
            preloader_class = incoming['class']

            if IsDeepDebug:
                print('preloader_class: %s' % preloader_class)

            ob = preloader_class(basedir, logger)
            ob._init_state(attrs=attrs, service=service, set_error=set_error)

            while ob.exists():
                logger('incoming: %s, filetype: %s' % (ob.next(), filetype), True)

                done = run_preloader(ob, filetype)

                set_message(mid, '%s%s[%s]: %s, total produced %s records, code: %s. Preloader was%sdone.' % ( 
                        PROCESS_LOGGER_PREFIX, 
                        mid, 
                        func_name(attrs.get('custom'), 'preloader'), 
                        ob.in_processing(), 
                        ob.total, 
                        ob.code == HANDLER_CODE_SUCCESS and 'successfully' or 'with errors', 
                        not done and ' not ' or ' ', 
                    ),
                    True)

                ob.reset()

            ob.clean()

    return done

def process_exists(mid, filetype, status_ids, attrs):
    done = False
    change_status = True
    keep_history = False

    if IsDebug and IsTrace:
        print('--> process_exists: %s, filetype: %s' % (mid, filetype))

    if mid:
        status_from, status_to, status_error = get_statuses(status_ids)
        #
        # attr.change_status: Change status or not, default: True
        #
        if 'change_status' in attrs:
            change_status = attrs['change_status'] and True or False
        #
        # attr.keep_history: Keep state of previous statuses
        #
        if 'keep_history' in attrs:
            keep_history = attrs['keep_history'] and True or False
        #
        # attr.forced: Forced run for given FileID
        #
        file_id = attrs.get('forced')

        if file_id:
            cursor = get_data_by_id(file_id)
        else:
            cursor = get_data_by_filetype(filetype, status_from)

        if cursor:
            for n, row in enumerate(cursor):
                order = Order(filetype, status_ids, row)

                logger('%s%s [%s]: %s' % (PROCESS_LOGGER_PREFIX, order.client, order.status, order.filename))

                error = False
                ob = None

                if not (mid and order.id):
                    continue

                elif mid == MOD_ORDER_CHECK:
                    ob, done = run_order_check(order, attrs)

                elif mid == MOD_ORDER_GENERATE:
                    ob, done = run_order_generate(order, attrs)

                elif mid == MOD_ORDER_REPORT:
                    ob, done = run_order_report(order, attrs)

                elif mid == MOD_UNLOADER:
                    ob, done = unload_order(order, attrs)

                else:
                    continue

                status, error = changeStatus(ob.code, order, status_to, status_error, change_status=change_status, keep_history=keep_history)

                if done:
                    set_message(mid, '%s%s[%s]: %s, total produced %s records, code: %s. Status was%schanged to [%s].' % ( 
                            PROCESS_LOGGER_PREFIX, 
                            mid, 
                            func_name(attrs.get('custom')), 
                            order.filename, 
                            ob.total, 
                            ob.code == HANDLER_CODE_SUCCESS and 'successfully' or 'with errors',
                            not (change_status and status and not error) and ' not ' or ' ',
                            status,
                        ), 
                        True)

                if ob is not None:
                    ob.clean()

    return done

def process_incoming(mid, filetype, status_ids, attrs):
    done = False

    if IsDebug and IsTrace:
        print('--> process_incoming: %s, filetype: %s' % (mid, filetype))

    if mid == MOD_LOADER:
        status_from, status_to, status_error = get_statuses(status_ids)
        incoming = attrs.get('incoming')

        if incoming and isinstance(incoming, dict) and 'class' in incoming:
            incoming_class = incoming['class']

            if IsDeepDebug:
                print('incoming_class: %s' % incoming_class)

            ob = incoming_class(connection, basedir, logger)
            ob._init_state(attrs=attrs, service=service, set_error=set_error)

            while ob.exists():
                logger('incoming: %s, filetype: %s' % (ob.next(), filetype), True)

                order = load_incoming_order(ob, filetype, status_ids)

                if order is not None:
                    done = order.id and True or False

                    set_message(mid, '%s%s[%s]: %s, total produced %s records, code: %s. A new file order was%sgenerated%s.' % ( 
                            PROCESS_LOGGER_PREFIX, 
                            mid, 
                            func_name(attrs.get('custom'), 'incoming'), 
                            order.filename, 
                            ob.total, 
                            ob.code == HANDLER_CODE_SUCCESS and 'successfully' or 'with errors', 
                            not done and ' not ' or ' ', 
                            done and (', FileID: %s' % order.id) or '', 
                        ),
                        True)

                ob.reset()

            ob.clean()

    return done

def process_reference(mid, filetype, attrs):
    done = False

    if IsDebug and IsTrace:
        print('--> process_reference: %s, filetype: %s' % (mid, filetype))

    if mid == MOD_LOADER:
        reference = attrs.get('reference')

        if reference and isinstance(reference, dict) and 'class' in reference:
            reference_class = reference['class']

            if IsDeepDebug:
                print('reference_class: %s' % reference_class)

            ob = reference_class(connection, basedir, logger)
            ob._init_state(attrs=attrs, service=service, set_error=set_error)

            while ob.exists():
                logger('reference: %s, filetype: %s' % (ob.next(), filetype), True)

                load_reference(ob, filetype)

                done = ob.total > 0 and ob.code == HANDLER_CODE_SUCCESS and True or False

                set_message(mid, '%s%s[%s]: %s, total produced %s records, code: %s. A new reference was%sreceived.' % ( 
                        PROCESS_LOGGER_PREFIX, 
                        mid, 
                        func_name(attrs.get('custom'), 'reference'), 
                        ob.in_processing(), 
                        ob.total, 
                        ob.code == HANDLER_CODE_SUCCESS and 'successfully' or 'with errors', 
                        not done and ' not ' or ' ', 
                    ),
                    True)

            ob.clean()

    return done

def process_merge(mid, filetype, status_ids, attrs):
    done = False
    change_status = False

    if IsDebug and IsTrace:
        print('--> process_merge: %s, filetype: %s' % (mid, filetype))

    if mid == MOD_ORDER_MERGE:
        status_from, status_to, status_error = get_statuses(status_ids)
        cursor = get_data_by_filetype(filetype, status_from)

        if not cursor:
            return False

        orders = [Order(filetype, status_ids, row) for n, row in enumerate(cursor)]

        if orders:
            ob = run_order_merge(filetype, orders, status_to, status_error, attrs)

            done = ob.done

            if not done:
                return False

            for id in ob.ids:
                row = get_data_by_id(id)
                order = Order(filetype, [ob._status,], row[0])

                ob.setOrder(order)

                if change_status:
                    status, error = changeStatus(ob.code, order, status_to, status_error, change_status=change_status)
                else:
                    status, error = order.status_id, ob.code == HANDLER_CODE_ERROR

                set_message(mid, '%s%s[%s]: %s, total produced %s records, code: %s. Order was created with status [%s].' % ( 
                        PROCESS_LOGGER_PREFIX, 
                        mid, 
                        func_name(attrs.get('custom')), 
                        order.filename, 
                        order.fqty, 
                        ob.code == HANDLER_CODE_SUCCESS and 'successfully' or 'with errors',
                        status,
                    ), 
                    True)

            ob.clean()

    return done

## ==========================
## MODULES: BUILTING HANDLERS
## ==========================

def run_preloader(ob, filetype):
    """
        Preload incoming file
    """
    ob.run()

    if IsDeepDebug:
        print('>>> Preloader: %s, Total: %s, Code: %s' % (ob.original, ob.total, ob.code))

    return ob.code

def load_incoming_order(ob, filetype, status_ids):
    """
        Load incoming file & create a new order
    """
    statuses = status_ids[1:]
    order = None

    ob.run(statuses)

    if ob.code:
        order = Order(filetype, status_ids)
        order.get_item(engine, default_template, database_config[default_template]['export'], ob.id)

    if IsDeepDebug:
        print('>>> Incoming: %s, Total: %s, FileID: %s, Code: %s' % (ob.original, ob.total, ob.id, ob.code))

    return order

def load_reference(ob, filetype):
    """
        Load reference file
    """
    ob.run()

    if IsDeepDebug:
        print('>>> Reference: %s, Total: %s, Code: %s' % (ob.original, ob.total, ob.code))

def run_order_check(order, attrs):
    """
        Check content of body
    """
    ob = OrderCheck(connection, basedir, logger)
    ob._init_state(order, attrs=attrs, factory=registered_order_filetypes, service=service, set_error=set_error)

    auto = attrs.get('auto')
    action = \
        auto == ACTION_ORDER_CHECK_PARAMETERS and 'ACTION_ORDER_CHECK_PARAMETERS' or \
        auto == ACTION_ORDER_CHECK_DATA and 'ACTION_ORDER_CHECK_DATA' or \
        ''

    logger('%s%s: %s' % (CHECK_LOGGER_PREFIX, action, order.filename))

    ob.run()

    if IsDeepDebug:
        print('>>> Check[%s]: %s, Total: %s, Code: %s' % (action, order.filename, ob.total, ob.code))

    return ob, True

def run_order_generate(order, attrs):
    """
        Generate or change content of body
    """
    global stdout

    ob = OrderGenerate(connection, basedir, logger)
    ob._init_state(order, attrs=attrs, factory=registered_order_filetypes, service=service, set_error=set_error)

    for phase in range(0, attrs.get('phases') or 1):
        if phase > 0:
            ob.reset()

        ob.run(phase)

        if ob.code == HANDLER_CODE_ERROR:
            break

    if IsDeepDebug:
        print('>>> Generate: %s, Total: %s, Code: %s' % (order.filename, ob.total, ob.code))

    stdout = ob.stdout()

    return ob, True

def run_order_report(order, attrs):
    """
        Report of body
    """
    ob = OrderReport(connection, basedir, logger)
    ob._init_state(order, attrs=attrs, factory=registered_order_filetypes, service=service, set_error=set_error)

    if not ob.activate(by_default=True):
        return ob, False

    ob.run()

    if IsDeepDebug:
        print('>>> Report: %s, Total: %s, Code: %s' % (order.filename, ob.total, ob.code))

    return ob, True

def run_order_merge(filetype, orders, status_to, status_error, attrs):
    """
        Merge of file orders body
    """
    ob = OrderMerge(connection, basedir, logger)
    ob._init_state(filetype, orders, attrs=attrs, factory=registered_order_filetypes, service=service, set_error=set_error)

    if not ob.activate():
        return ob

    logger('%smerge orders: %s' % (PROCESS_LOGGER_PREFIX, ', '.join([repr(order) for order in orders])))

    while ob.ready():
        order = ob._get_next()

        ob.setOrder(order)

        ob.run()

        status, error = changeStatus(ob.code, order, status_to, status_error, change_status=True)

        ob.clean(original=order.filename)

    ob.deactivate()

    # ---------
    # New order
    # ---------

    if ob.code != HANDLER_CODE_SUCCESS:
        return ob

    if IsDeepDebug:
        print('>>> Merge: %s[%s], Total: %s, Code: %s' % (ob._base_filename, ob.keys, ob.total, ob.code))

    return ob

def unload_order(order, attrs):
    """
        Unload body of order
    """
    ob = Unloader(connection, basedir, logger)
    ob._init_state(order, attrs=attrs, factory=registered_order_filetypes, service=service, set_error=set_error)

    if not ob.activate(by_default=True):
        return ob, False

    ob.run()

    if IsDeepDebug:
        print('>>> Unloader: %s, Total: %s, Code: %s' % (order.filename, ob.total, ob.code))

    return ob, True

def run_actions(ob):
    if ob is None:
        return

    while not ob.is_empty:
        module, command, data, info = ob.get_next()
        n = isIterable(data) and len(data) or 0

        done = False

        try:
            if not command:
                continue
            elif command == 'copy' and n == 2:
                done = ob.copy(data[0], data[1])
            elif command == 'move' and n == 2:
                done = ob.move(data[0], data[1])
            elif command == 'remove' and n == 1:
                done = ob.remove(data[0])

        except Exception as ex:
            set_error('run_actions', ex, True)
            raise

        if not done:
            continue

        logger('%saction[%s]: %s, data:%s' % (info and ('%s ' % info.strip()) or '', module, command, repr(data)), force=True)
