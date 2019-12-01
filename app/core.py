# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

import os
import sys, codecs
import re
import pymssql
import zlib
import json
import requests
import base64

from collections import OrderedDict

import xml.etree.ElementTree as ET

from config import (
     CONNECTION, IsDebug, IsDeepDebug, IsTrace, IsTmpClean, IsSourceClean, IsDisableOutput, IsPrintExceptions,
     default_print_encoding, default_unicode, default_encoding, default_iso, cr,
     LOCAL_EASY_DATESTAMP, UTC_FULL_TIMESTAMP, DATE_STAMP,
     print_to, print_exception
     )

from .types import *
from .checker import *
from .mails import *
from .srvlib import *
from .xmllib import *
from .utils import del_file, move_file, copy_file, normpath, getToday, getTime, getDate, getDateOnly, isIterable

from ext.xmllib import *

default_view = 'orders'

_SQL = {
    'OrderFilesBody' : {
        'get_body'    : 'SELECT TID, IBody FROM [BankDB].[dbo].[OrderFilesBody_tb] WHERE FileID=%d and FileStatusID=%d',
        'seek_body'   : 'SELECT TOP 1 TID, IBody FROM [BankDB].[dbo].[OrderFilesBody_tb] WHERE FileID=%d ORDER BY TID DESC',
        'add_body'    : 'INSERT INTO [BankDB].[dbo].[OrderFilesBody_tb] VALUES(%d, NULL, %s, %d, %s)',
        'update_body' : 'UPDATE [BankDB].[dbo].[OrderFilesBody_tb] SET IBody=%s WHERE TID=%d',
    },
    'OrderFiles' : {
        'check'       : 'SELECT 1 FROM [BankDB].[dbo].[OrderFiles_tb] WHERE FName=%s',
        'add'         : 'INSERT INTO [BankDB].[dbo].[OrderFiles_tb] VALUES(%d, %s, %d, %d, %s, %s, %d, %s, NULL)',
        'ready'       : 'UPDATE [BankDB].[dbo].[OrderFiles_tb] SET ReadyDate=%s WHERE TID=%d',
    },
    'OrderFilesBodyImage' : {
        'add'         : 'INSERT INTO [BankDB].[dbo].[OrderFilesBodyImage_tb] VALUES(%d, %s, NULL)'
    },
    'DIC_FileType' : {
        'filetype'    : 'SELECT TID FROM [BankDB].[dbo].[DIC_FileType_tb] WHERE CName=%s',
    },
}

BUFSIZE = 4096
BOMLEN = len(codecs.BOM_UTF8)

## ==========================
## CORE: ABSTRACT ORDER CLASS
## ==========================

class ProcessException(Exception):

    def __init__(self, message, errors=None):
        super().__init__(message)


class CustomException(ProcessException):

    def __init__(self, message, errors=None, recipients=None):
        super().__init__(message, errors)

        self._recipients = recipients


class LoaderException(Exception):

    def __init__(self, message, errors=None):
        super().__init__(message)


class Actions:
    """
        Actions List class to execute in finish stage
    """

    def __init__(self):
        self._items = []

    def add(self, module, command, data, info=None):
        """
            Available commands:
                'copy'    -- copy from `source` to `destination`
                'move'    -- move from `source` to `destination`
                'remove'  -- delete file
        """
        self._items.append((module, command, data, info))

    @property
    def items(self):
        return self._items

    @property
    def is_empty(self):
        return len(self._items) == 0

    def get_next(self):
        return self._items.pop(0)

    def remove(self, filename):
        del_file(filename)
        return True

    def move(self, source, destination):
        move_file(source, destination)
        return True

    def copy(self, source, destination):
        copy_file(source, destination)
        return True


class Order:
    """
        BankPerso File Order class
    """

    def __init__(self, name, status_ids=None, row=None):
        self.name = name
        self.status_ids = status_ids

        self._id = None
        self._filename = None
        self._filetype = None
        self._fqty = None
        self._status = None
        self._status_id = None
        self._client = None
        self._date = None
        self._ready_date = None

        self._status_to = None
        self._status_error = None
        self._status_from_index = 0

        self._init_state(row)

    def _init_state(self, row):
        if not (row and isinstance(row, dict)):
            return

        self._id = row.get('FileID')
        self._filename = row.get('FName')
        self._filetype = row.get('FileType')
        self._fqty = row.get('FQty')
        self._status = row.get('FileStatus')
        self._status_id = row.get('FileStatusID')
        self._client = row.get('BankName')
        self._date = row.get('RegisterDate')
        self._ready_date = row.get('ReadyDate')

    def __repr__(self):
        return '%s:%s' % (self.id, self.filename)

    def reset(self):
        self._status_from_index = 1

    def get_item(self, engine, view, columns, file_id):
        if not file_id:
            return

        where = 'FileID=%s' % file_id
        encode_columns = ('BankName', 'FileStatus',)
        cursor = engine.runQuery(view, columns=columns, top=1, where=where, as_dict=True, encode_columns=encode_columns)

        self._init_state(cursor and cursor[0] or None)

    def get_original(self, engine, encode_columns=None):
        if engine is None:
            return

        where = "FName='%s'" % self.name
        cursor = engine.runQuery(default_view, top=1, where=where, as_dict=True, encode_columns=encode_columns)

        self._init_state(cursor and cursor[0] or None)

    @property
    def id(self):
        return self._id
    @property
    def filename(self):
        return self._filename
    @property
    def filetype(self):
        return self._filetype
    @property
    def fqty(self):
        return self._fqty
    @property
    def status(self):
        return self._status
    @property
    def status_id(self):
        return self._status_id
    @property
    def date(self):
        return self._date
    @property
    def ready_date(self):
        return self._ready_date
    @property
    def client(self):
        return self._client
    @property
    def ordername(self):
        return self._filename.split('.')[0]

    @property
    def status_from(self):
        if not self.status_ids:
            return None
        status = self.status_ids[self._status_from_index]
        return callable(status) and status(self) or status
    @property
    def status_to(self):
        if self._status_to is not None:
            return self._status_to
        if not self.status_ids:
            return None
        status = self.status_ids[1]
        return callable(status) and status(self) or status
    @status_to.setter
    def status_to(self, value):
        self._status_to = value
    @property
    def status_error(self):
        if self._status_error is not None:
            return self._status_error
        if not self.status_ids:
            return None
        status = len(self.status_ids) > 2 and self.status_ids[2] or None
        return callable(status) and status(self) or status
    @status_error.setter
    def status_error(self, value):
        self._status_error = value


class Base:

    def __init__(self, basedir, logger, *args, **kwargs):
        if IsDeepDebug:
            print('Base init')

        super().__init__(*args, **kwargs)

        self._basedir = basedir
        self._logger = logger

        self._factory = None
        self._saveback = None
        self._actions = None
        self._params = None
        self._service = None
        self._engine = None
        self._autocommit = None
        self._set_error = None

        self._order = None
        self._checker = None
        self._filename = ''

        self._location = None
        self._original = ''
        self._code = HANDLER_CODE_UNDEFINED
        self._total = 0
        self._tmp_folder = ''
        self._tmp = '%s'

        self._fieldset = None
        self._defaults = None

        self.mod_activate = None
        self.mod_deactivate = None
        self.mod_auto = None
        self.mod_custom = None
        self.mod_outgoing = None

        self.phase = 0

    def _init_state(self, attrs, service, *args, **kwargs):
        if IsDeepDebug:
            print('Base initstate')

        super().__init__(*args, **kwargs)

        # Root service
        self._service = service

        # FSO actions
        self._actions = attrs.get('actions')
        # Custom params
        self._params = attrs.get('params')
        # DB engine
        self._engine = attrs.get('engine')
        # Autocommit
        self._autocommit = attrs.get('autocommit')

        # Tmp folder
        self._tmp_folder = normpath(os.path.join(self._basedir, 'tmp'))

    def class_info(self):
        return self.__class__.__bases__[0].__name__

    def stdout(self):
        return self._saveback and self._saveback.get('stdout') or None

    def service_config(self, key):
        return key and self._service is not None and callable(self._service) and self._service(key) or None

    service = service_config

    @staticmethod
    def set_mod(key, attrs):
        x = attrs.get(key)
        if x is not None and callable(x):
            return x
        return None

    def mod_tmp(self, name=None):
        if name:
            self.original = name
        return normpath(os.path.join(self.tmp_folder, self.original.split('.')[0])) + '%s'

    def mod_source(self, name=None):
        return normpath(os.path.join(self._location, name or self.original))

    def _decompress(self, xml, body):
        ##open(xml, 'wb').write(zlib.decompress(body))
        Base.file_setter(xml, zlib.decompress(body))

    def _compress(self, comp, gen):
        # Compress large data:
        # https://www.programcreek.com/python/example/1511/zlib.compressobj
        # ***
        ##open(comp, 'wb').write(zlib.compress(open(gen, 'rb').read()))
        Base.file_setter(comp, zlib.compress(Base.file_getter(gen)))

    @property
    def actions(self):
        return self._actions

    @property
    def original(self):
        return self._original
    @original.setter
    def original(self, value):
        self._original = value

    @property
    def tmp_folder(self):
        return self._tmp_folder
    @property
    def tmp_body(self):
        return self._tmp % '_body.dump'
    @property
    def tmp_comp(self):
        return self._tmp % '_comp.dump'
    @property
    def tmp_source(self):
        return '%s/%s' % (self.tmp_folder, self.original)
    @property
    def tmp_image(self):
        return self._tmp % '_image.dump'
    @property
    def tmp_xml(self):
        return self._tmp % '.xml'
    @property
    def tmp_gen(self):
        return self._tmp % '_gen.xml'

    def clean(self, original=None):
        if not IsTmpClean:
            return

        if original:
            self._tmp = self.mod_tmp(original)

        if not (self._tmp and self.tmp_folder in self._tmp):
            return

        check = True

        try:
            del_file(self.tmp_body, check=check)
            del_file(self.tmp_comp, check=check)
            del_file(self.tmp_xml, check=check)
            del_file(self.tmp_gen, check=check)
            del_file(self.tmp_image, check=check)

            if IsSourceClean and self.original:
                del_file(self.tmp_source, check=check)

        except Exception as ex:
            print_to(None, 'Base.clean Error: [%s] %s' % (self.tmp_folder, str(ex)))
            if IsPrintExceptions:
                print_exception()

    @property
    def fieldset(self):
        return self._fieldset
    @fieldset.setter
    def fieldset(self, value):
        self._fieldset = value
    @property
    def defaults(self):
        return self._defaults
    @defaults.setter
    def defaults(self, value):
        self._defaults = value

    @property
    def code(self):
        """
            Exit code: 
                1 - successfully
                0 - errors
        """
        return self._code
    @code.setter
    def code(self, value):
        self._code = value

    @property
    def filename(self):
        """
            Name of the resulting file: String. Should be set before start
        """
        return self._filename
    @filename.setter
    def filename(self, value):
        self._filename = value

    @property
    def total(self):
        """
            Total performed records: int.
        """
        return self._total
    @total.setter
    def total(self, value):
        self._total = value

    @staticmethod
    def readnodes(filename, fo, begins, ends, record_iter, **kw):
        if record_iter is None or not callable(record_iter):
            return 0

        is_output = kw.get('is_output') and True or False
        total = kw.get('total') or 0
        eol = kw.get('eol') or cr

        def match_tag(tags, line, **kw):
            data = kw.get('data')
            for tag in tags:
                if tag in line:
                    if kw.get('begin'):
                        p = line.find(tag)
                        data['line'] = line[p:]
                        data['before'] = line[:p]
                    else:
                        p = line.find(tag) + len(tag)
                        data['line'] = line[:p]
                        data['after'] = line[p:].strip()
                    return True
            return False

        is_multifiles = fo is None and True or False
        n = total

        with open(filename, 'rb') as fi:
            append = False

            s = b''
            before = after = b''

            for line in fi:
                data = {}
                if not append and match_tag(begins, line, data=data, begin=True):
                    s = data.get('line')
                    before = data.get('before')
                    append = True
                elif append and match_tag(ends, line, data=data):
                    s += data.get('line')
                    after = data.get('after')
                    append = False
                    n += 1

                    if is_output and before:
                        fo.write(before)

                    out = record_iter(n, s, option=None, **kw)

                    if out is None:
                        pass
                    elif is_multifiles:
                        out, fo = out

                    if out:
                        fo.write(out+eol.encode())

                    if is_output and after:
                        fo.write(after)

                    before = after = b''
                    s = None
                    del s
                elif append:
                    s += line
                elif is_output:
                    fo.write(line)

        return n

    def ordered_fieldset(self):
        return self._fieldset and isinstance(self._fieldset, dict) and \
            OrderedDict(sorted(self._fieldset.items(), key=lambda x: x[1][0])) or {}

    def ordered_keys(self, fieldset=None):
        if not fieldset:
            fieldset = self.ordered_fieldset()
        return [fieldset[key][1] or key for key in list(fieldset.keys())]

    def get_field(self, key, value):
        number, name, field_type, data_type, perso_type, encoding, size, is_obligatory, comment = value

        if not name:
            name = key
        if not field_type:
            field_type = self._defaults.get('field_type') or DATA_TYPE_FIELD
        if not data_type:
            data_type = self._defaults.get('data_type') or DATA_TYPE_TEXT
        if not perso_type:
            perso_type = self._defaults.get('perso_type') or DATA_PERSO_TYPE_DEFAULT
        if not encoding:
            encoding = self._defaults.get('encoding') or ENCODING_ASCII
        if not size:
            size = (0, 9999)

        is_obligatory = is_obligatory and True or False

        if not comment:
            comment = key

        return number, name, field_type, data_type, perso_type, encoding, size, is_obligatory, comment

    def decode_input(self, s, encoding, option=None):
        # Returns input data as a decoded string (str)
        # ***
        if s and isinstance(s, bytes):
            return option and s.decode(encoding, option) or s.decode(encoding)
        return not s and '' or s

    @staticmethod
    def file_setter(source, data, mode='wb'):
        with open(source, mode) as fo:
            fo.write(data)

    @staticmethod
    def file_getter(source, mode='rb'):
        with open(source, mode) as fi:
            return fi.read()

    def record_iter(self, n, data, **kw):
        """
            Custom output node iterator.

            Arguments:
                n        -- Int, record number
                data     -- bytes or str, line's data

            Keyword arguments:
                encoding -- String, data encoding type
                option   -- String, decoder option {ignore|...}
                fieldset -- Dict, filetype fields descriptor [fieldset]
                keys     -- Tuple, line fields list

            Returns:
                output[value or node]: value encoded with the given `encoding` (bytes) or node as str (unicode).
        """
        encoding = kw.get('encoding') or default_encoding
        option = kw.get('option') or 'ignore'

        line = self.decode_input(data, encoding, option)
        node = ET.fromstring(line)

        self._logger('--> Record[%s] len:%s' % (n, len(line)), True)

        line = None
        del line

        value = self.custom(n, node, **kw)

        if value is not None:
            return value.encode(encoding, option)

        return re.sub(r'<\?xml.*?\?>', '', ET.tostring(node, 'unicode'))

    def dumpBody(self, body):
        Base.file_setter(self.tmp_body, body)

        if IsDeepDebug:
            print_to(None, '>>> %s' % self.tmp_body)

    def makeXml(self, body):
        self._decompress(self.tmp_xml, body)

        if IsDeepDebug:
            print_to(None, '>>> %s' % self.tmp_xml)

    def compBody(self, comp=None, gen=None):
        self._compress(self.tmp_comp, self.tmp_gen)

        if IsDeepDebug:
            print_to(None, '>>> %s' % self.tmp_comp)

    def compImage(self):
        self._compress(self.tmp_image, self.tmp_source)

        if IsDeepDebug:
            print_to(None, '>>> %s' % self.tmp_image)

    def activate(self, by_default=None):
        """
            Check params before start and activate process
        """
        if not (self.mod_activate is not None and callable(self.mod_activate)):
            return by_default

        # Check activation
        return self.mod_activate(self._logger, self._saveback, 
                actions=self.actions,
                connect=getattr(self, 'connect'),
                filename=self.filename,
                order=self._order,
                service=self.service,
                tmp=self.tmp_folder,
                engine=self._engine,
            )

    def custom(self, n, node, **kw):
        """
            Run custom
        """
        code = None
        if self.mod_custom is not None and callable(self.mod_custom):
            code = self.mod_custom(n, node, self._logger, self._saveback, 
                actions=self.actions,
                checker=self._checker,
                connect=getattr(self, 'connect'),
                filename=self.filename,
                fieldset=kw.get('fieldset'), 
                keys=kw.get('keys'), 
                order=self._order,
                phase=self.phase,
                service=self.service,
                tmp=self.tmp_folder,
                total=self.total,
                params=self._params,
                engine=self._engine,
            )

        return code

    def outgoing(self, is_error=False, **kw):
        """
            Create outgoing
        """
        if not (self.mod_outgoing is not None and callable(self.mod_outgoing)):
            return

        self.mod_outgoing(self._logger, self._saveback, is_error,
            actions=self.actions,
            fieldset=kw.get('fieldset'),
            filename=kw.get('filename') or self._order and self._order.ordername,
            keys=kw.get('keys'),
            order=self._order,
            saveback_errors=self._saveback.get('errors'),
            service=self.service,
            tmp=self.tmp_folder,
            total=self.total,
            engine=self._engine,
        )


class Connection(Base):
    """
        DBMS Connection class
    """

    def __init__(self, connection, *args, **kwargs):
        if IsDeepDebug:
            print('Connection init')

        super().__init__(*args, **kwargs)

        self._connection = connection

        self.conn = None
        self.is_error = False

        self.TID = None

    def reset(self):
        self.is_error = False

        if not hasattr(self, 'cursor'):
            return

        del self.cursor

    def open(self, autocommit=None):
        server = self._connection['server']
        user = self._connection['user']
        password = self._connection['password']
        database = self._connection['database']

        self.conn = pymssql.connect(server, user, password, database)

        if autocommit is None:
            return

        self.conn.autocommit(autocommit and True or False)
        self.cursor = self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self, is_error=None):
        if is_error is not None:
            if is_error:
                self.rollback()
            else:
                self.commit()

        self.conn.close()

    def connect(self, sql, params, **kw):
        """
            Parameterized query.

            Arguments:
                sql     -- String, SQL query with params scheme
                params  -- List, query parameters

            Keyword arguments:
                with_commit -- Boolean, use transaction or not
                with_result -- Boolean, should be returned recodset
                callproc    -- Boolean, run stored procedure

            Returns:
                cursor      -- List, cursor or query results recordset
                _is_error   -- Boolean, executes with error or not.
        """
        if kw.get('check_error') and self.is_error:
            return None, True

        _with_commit = kw.get('with_commit')
        _with_result = kw.get('with_result')
        _raise_error = kw.get('raise_error')
        _callproc = kw.get('callproc')

        _is_error = False

        if not (hasattr(self, 'conn') and self.conn is not None and hasattr(self, 'cursor')):
            self.open(0)

        conn = self.conn

        # ------------------
        # Check `autocommit`
        # ------------------

        if _with_commit is not None:
            if _with_commit: # and conn.autocommit_state:
                conn.autocommit(False)
            else:
                conn.autocommit(True)

        cursor = self.cursor

        if IsDeepDebug:
            print_to(None, 'with_commit: %s' % _with_commit)
            print_to(None, 'sql: %s' % sql)

        res = None

        try:
            if _callproc:
                res = cursor.callproc(sql, params)
            else:
                cursor.execute(sql, params)
        except:
            if IsPrintExceptions:
                print_exception(1)
            print_to(None, 'ERROR SQL:[%s]' % sql)

            if _raise_error:
                raise

            _is_error = True

        # ------------------------------------------------
        # Manage transaction if `autocommit` is turned off
        # ------------------------------------------------

        if _with_commit is not None:
            if _with_commit and not conn.autocommit_state:
                if _is_error:
                    conn.rollback()
                else:
                    conn.commit()

        self.conn, self.is_error = conn, _is_error

        if _with_result:
            if _callproc:
                return res, _is_error
            else:
                res = list(cursor.fetchall())
                return self.encode_columns(res, kw.get('encode_columns')), _is_error

        return cursor, _is_error

    @staticmethod
    def encode_columns(cursor, columns):
        if not (cursor and columns):
            return cursor
        rows = []
        for n, line in enumerate(cursor):
            row = [x for x in line]
            for column in columns:
                if column in row or isinstance(column, int):
                    row[column] = row[column] and row[column].encode(default_iso).decode(default_encoding) or ''
            rows.append(row)        
        return rows

    @staticmethod
    def get_body(cursor, index=0):
        rows = []
        for n, row in enumerate(cursor):
            rows.append(row)
        return rows and rows[0][index] or None

    @staticmethod
    def get_data(cursor, index=0):
        rows = []
        for n, row in enumerate(cursor):
            rows.append(row)
        return rows and rows[index]

    @staticmethod
    def get_value(x):
        return x and len(x) > 0 and x[0][0] or None

    def checkFileExists(self, filename):
        cursor, is_error = self.connect(_SQL['OrderFiles']['check'], (
                filename, 
            ),
            with_result=True
        )
        return not is_error and self.get_body(cursor) and True or False

    def getBody(self, id, status, **kw):
        def _get_body(x):
            body = None
            cursor, is_error = x
            data = not is_error and self.get_data(cursor)

            if data is not None and len(data) == 2:
                self.TID, body = data
            return body

        body = _get_body(self.connect(_SQL['OrderFilesBody']['get_body'], (
                id, 
                status,
            ),
            with_result=True
        ))

        if body is not None:
            return body

        body = _get_body(self.connect(_SQL['OrderFilesBody']['seek_body'], (
                id, 
            ),
            with_result=True
        ))

        return body

    def setBody(self, id, status, with_commit=False):
        cursor, is_error = self.connect(_SQL['OrderFilesBody']['add_body'], (
                id, 
                getDate(getToday()), 
                status, 
                open(self.tmp_comp, 'rb').read(),
            ), 
            with_commit=with_commit
        )
        lastrowid = not is_error and cursor.lastrowid or None

        self.TID = lastrowid

        return lastrowid

    def updateBody(self, with_commit=False):
        cursor, is_error = self.connect(_SQL['OrderFilesBody']['update_body'], (
                open(self.tmp_comp, 'rb').read(),
                self.TID, 
            ), 
            with_commit=with_commit
        )

        if is_error:
            self.TID = None

    def updateReadyDate(self, attrs, with_commit=False):
        ready_date = attrs['ReadyDate']
        tid = attrs['TID']

        cursor, is_error = self.connect(_SQL['OrderFiles']['ready'], (
                ready_date, 
                tid, 
            ),
            with_commit=with_commit
        )
        
        return is_error

    def addNewOrder(self, attrs, no_image=False, with_commit=False):
        fname = attrs['FName']
        filetype = attrs['FileType']
        fqty = attrs['FQty']
        status = attrs['FileStatusID']
        ready_date = attrs['ReadyDate']

        now = getDate(getToday())

        cursor, is_error = self.connect(_SQL['DIC_FileType']['filetype'], (
                filetype,
            ), 
            with_result=True
        )
        filetype_id = not is_error and self.get_value(cursor) or None

        if not filetype_id:
            return

        cursor, is_error = self.connect(_SQL['OrderFiles']['add'], (
                filetype_id, 
                fname, 
                fqty, 
                status, 
                now, 
                now, 
                0,
                ready_date,
            ),
            with_commit=with_commit
        )
        file_id = cursor.lastrowid

        if not file_id:
            return

        attrs['FileID'] = file_id

        image = b'' # no image

        if not no_image:
            image = open(self.tmp_image, 'rb').read()

        cursor, is_error = self.connect(_SQL['OrderFilesBodyImage']['add'], (
                file_id, 
                image,
            ),
            with_commit=with_commit
        )
        lastrowid = not is_error and cursor.lastrowid or None


class AbstractOrderClass(Connection, Base):
    """
        Abstract Order Generator class.
        Used for evolute - extend, update, transform of the existed Order IBody content.

        Supplied to Modules:
        - order_check
        - order_generate
        - order_report
    """

    _default_tags = ('FileInfo', 'FileBody_Record', 'ProcessInfo',)

    def __init__(self, connection, basedir, logger):
        if IsDeepDebug:
            print('AbstractOrderClass init')

        super().__init__(connection, basedir, logger)

        # Default IBody tags 1-st level structure
        self._tags = self.__class__._default_tags
        # Default encoding for output
        self._encoding = default_encoding
        self._mode = None
        self._eol = None

        self.mod_output = None
        self.mod_tags = None

    def _init_state(self, order, attrs=None, factory=None, service=None):
        if IsDeepDebug:
            print('AbstractOrderClass initstate')

        super()._init_state(attrs, service)

        # Selected Order info
        self._order = order
        # Filetype factory
        self._factory = factory.get(order.filetype)

        if isinstance(self._factory, dict):
            self.fieldset = self._factory.get('fieldset')
            self.defaults = self._factory.get('defaults')

        # Default actions (auto)
        auto = attrs.get('auto')

        if not auto:
            self.mod_auto = None
        elif auto == ACTION_ORDER_PRELOAD:
            self.mod_auto = self.auto_preload
        elif auto == ACTION_ORDER_CHECK_PARAMETERS:
            self.mod_auto = self.auto_check_parameters
        elif auto == ACTION_ORDER_CHECK_DATA:
            self.mod_auto = self.auto_check_data

        # Ext Module members
        self.mod_activate = Base.set_mod('activate', attrs)
        self.mod_custom = Base.set_mod('custom', attrs)
        self.mod_outgoing = Base.set_mod('outgoing', attrs)
        self.mod_output = Base.set_mod('output', attrs)
        self.mod_tags = Base.set_mod('tags', attrs)

        # Mode and EOL for output
        self._mode = attrs.get('mode') or 'wb'
        self._eol = attrs.get('EOL') or cr

        # Temp
        self._tmp = self.mod_tmp(order.filename)

        # custom's saveback area
        self._saveback = {
            'base'   : Base,
            'errors' : [],
        }

        self._code = HANDLER_CODE_UNDEFINED

    @property
    def order(self):
        return self._order

    def reset(self):
        super().reset()
        # Load order from the next state with phase more 0
        self._order.reset()

    def auto_preload(self, node):
        if IsDeepDebug and IsTrace:
            print('>>> core.AbstractOrderClass.auto_preload, factory: %s' % repr(self._factory))

    def auto_check_parameters(self, node):
        if IsDeepDebug and IsTrace:
            print('>>> core.AbstractOrderClass.auto_check_parameters, factory: %s' % repr(self._factory))

        fieldset = self.ordered_fieldset()
        keys = list(fieldset.keys())

        codes = dict([(key, checkTagParameters(
                    i, 
                    key, 
                    self.get_field(key, fieldset.get(key)), 
                    getTag(node, key)
                )
            ) for i, key in enumerate(keys)])

        self._checker = (keys, codes,)

    def auto_check_data(self, node):
        if IsDeepDebug and IsTrace:
            print('>>> core.AbstractOrderClass.auto_check_data, factory: %s' % repr(self._factory))

        fieldset = self.ordered_fieldset()
        keys = list(fieldset.keys())

        codes = dict([(key, checkTagData(
                    i, 
                    key, 
                    self.get_field(key, fieldset.get(key)), 
                    getTag(node, key)
                )
            ) for i, key in enumerate(keys)])

        self._checker = (keys, codes,)

    def on_before(self):
        """
            On Before Run Handler
        """
        self.open(self._autocommit)

        id = self._order.id
        status = self._order.status_from

        body = self.getBody(id, status)

        if body is None:
            self._logger('>>> No body: %s %s' % (id, status), is_error=True)
            self.code = HANDLER_CODE_ERROR
            return

        self.dumpBody(body)
        self.makeXml(body)

        body = None
        del body

    def on_after(self, with_body_update=False, is_error=False):
        """
            On After Run custom
        """
        if not (self._autocommit is None or self._autocommit):
            self.close(is_error)
            self.reset()

        if with_body_update:
            self.compBody()

            status = is_error and self._order.status_error or self._order.status_to
            if self.phase == 0 and status:
                lastrowid = self.setBody(self._order.id, status, with_commit=True)
            else:
                self.updateBody(with_commit=True)
                lastrowid = self.TID

            if lastrowid:
                self._logger('--> lastrowid:%s' % lastrowid, True)
                self._logger('>>> OK', True)
            else:
                self._logger('>>> Error', True)

            if not is_error:
                is_error = not lastrowid and True or False
        else:
            if not is_error:
                self._logger('>>> OK', True)
            else:
                self._logger('>>> Error', True)

        self.close()

        # Finished with result
        self.code = not is_error and HANDLER_CODE_SUCCESS or HANDLER_CODE_ERROR

    def generate(self, gen=None, is_output=False):
        filename, destination, tags = self.tmp_xml, gen or self.tmp_gen, self._tags

        begins = [('<%s>' % x).encode(default_encoding) for x in tags]
        ends = [('</%s>' % x).encode(default_encoding) for x in tags]

        fo = open(destination, self._mode)

        n = Base.readnodes(filename, fo, begins, ends, self.record_iter, is_output=is_output, eol=self._eol)

        fo.close()

        self.total = n

        self._logger('--> Total records:%s' % n, True)

    def setOrder(self, order):
        self._order = order

    def genXml(self):
        if self.code != HANDLER_CODE_ERROR:
            self.generate(is_output=True)

        if self._saveback and READY_DATE in self._saveback:
            attrs = {
                'ReadyDate' : self._saveback[READY_DATE],
                'TID'       : self.order.id,
            }
            is_error = self.updateReadyDate(attrs)

        if IsDeepDebug:
            print_to(None, '>>> %s' % self.tmp_gen)

    def outgoing(self, is_error=False):
        """
            Create outgoing
        """
        if not is_error and self.mod_auto == self.auto_check_parameters:
            return

        fieldset = self.ordered_fieldset()
        keys = list(fieldset.keys())

        super().outgoing(is_error=is_error, fieldset=fieldset, keys=keys)

    main = genXml


class Preloader(Base):
    """
        Base Preloader class
    """

    def __init__(self, basedir, logger):
        if IsDeepDebug:
            print('Preloader init')

        super().__init__(basedir, logger)

        self._location = None
        self._encoding = None
        self._format = None

        self.mod_output = None

    def _init_state(self, attrs=None, service=None):
        if IsDeepDebug:
            print('Preloader initstate')

        super()._init_state(attrs, service)

        # Ext Module members
        self.mod_activate = Base.set_mod('activate', attrs)
        self.mod_deactivate = Base.set_mod('deactivate', attrs)
        self.mod_custom = Base.set_mod('custom', attrs)
        self.mod_outgoing = Base.set_mod('outgoing', attrs)
        self.mod_validator = Base.set_mod('validator', attrs)
        self.mod_output = Base.set_mod('output', attrs)

        # custom's saveback area
        self._saveback = {
            'base'   : Base,
            'errors' : [],
        }

    def reset(self):
        self.is_error = False
        self._total = 0
        self._tmp = None

    def in_processing(self):
        return self._filename

    def listdir(self):
        return self._location and os.listdir(self._location) or []

    def exists(self):
        obs = self.listdir()
        if len(obs) == 0:
            return False
        return self.in_processing() != obs[0]

    def _get_next(self):
        obs = self.listdir()
        return obs and obs[0] or None

    next = _get_next

    def _move_source(self, filename=None):
        move_file(filename or self.mod_source(self.in_processing()), self.tmp_folder)

    def outgoing(self, is_error=False):
        """
            Create outgoing
        """
        filename = self.in_processing()

        super().outgoing(is_error=is_error, filename=filename)


class AbstractPreloaderClass(Preloader):

    def __init__(self, basedir, logger):
        if IsDeepDebug:
            print('AbstractPreloaderClass init')

        super().__init__(basedir, logger)

        self.incoming = None

    def _init_state(self, attrs=None, service=None):
        if IsDeepDebug:
            print('AbstractPreloaderClass initstate')

        super()._init_state(attrs, service)

        # Preloader descriptor
        self.incoming = attrs.get('incoming')

        self.validate()

    def validate(self):
        if not self.incoming:
            return

        self._location = self.incoming.get('location')
        self._encoding = self.incoming.get('encoding') or ENCODING_WINDOWS

    def listdir(self):
        mask = self.incoming.get('mask') and re.compile(self.incoming['mask'], re.I+re.DOTALL) or None
        return self._location and [x for x in os.listdir(self._location) if not mask or mask.match(x)] or []

    def on_before(self):
        """
            On Before Run custom
        """
        pass

    def on_after(self, is_error=False):
        """
            On After Run custom
        """
        self.outgoing(is_error=is_error)

    def generate(self):
        filename = self._get_next()

        if filename == self.in_processing():
            return

        self._filename = filename
        self._total = 0

        # Set source original name
        self.original = self._filename
        # Set Temp
        self._tmp = self.mod_tmp()
        # Move source to Temp
        self._move_source()

        source = self.tmp_source

        n = self.custom(source)

        self._total = n

        self._logger('--> Total records:%s' % n, True)

    def main(self):
        try:
            self.generate()
        except Exception as ex:
            self.code = HANDLER_CODE_ERROR
            print_to(None, 'AbstractPreloaderClass.main: %s[%s]' % (ex, self.in_processing()))
            if IsPrintExceptions:
                print_exception()


class Loader(Connection, Base):
    """
        Base Loader class
    """

    def __init__(self, connection, basedir, logger):
        if IsDeepDebug:
            print('Loader init')

        super().__init__(connection, basedir, logger)

        self._location = None
        self._encoding = None
        self._format = None
        self._forced_status = None

        self.mod_output = None

    def _init_state(self, attrs=None, service=None):
        if IsDeepDebug:
            print('Loader initstate')

        super()._init_state(attrs, service)

        # Ext Module members
        self.mod_custom = Base.set_mod('custom', attrs)
        self.mod_outgoing = Base.set_mod('outgoing', attrs)
        self.mod_validator = Base.set_mod('validator', attrs)
        self.mod_output = Base.set_mod('output', attrs)

        # custom's saveback area
        self._saveback = {
            'base'   : Base,
            'errors' : [],
        }

    def reset(self):
        super().reset()
        self._forced_status = None

    @property
    def forced_status(self):
        return self._forced_status

    @property
    def with_header(self):
        return False

    @property
    def is_trancate(self):
        return False

    def get_status(self, status, is_error=False):
        if isIterable(status) and len(status) >= 2:
            status_success = status[0]
            status_error = status[1]
        else:
            status_success = status_error = status

        return self.forced_status or not is_error and status_success or status_error

    def in_processing(self):
        return self._filename

    def listdir(self):
        return self._location and os.listdir(self._location) or []

    def exists(self):
        obs = self.listdir()
        if len(obs) == 0:
            return False
        return self.in_processing() != obs[0]

    def _get_next(self):
        obs = self.listdir()
        return obs and obs[0] or None

    next = _get_next

    def _move_source(self, filename=None):
        move_file(filename or self.mod_source(self.in_processing()), self.tmp_folder)

    def _write(self, fo, s):
        if fo is None or s is None:
            return
        fo.write(s.encode(self._encoding))

    def _set_header(self, location, filename):
        return ''

    def _set_footer(self, n):
        return ''

    def _split(self, line, splitter=None):
        return line.strip().split(splitter or '')

    def _set_content(self, n, keys=None, fieldset=None, values=None):
        return None

    @staticmethod
    def _truncate(source):
        with open(source, "r+b") as fp:
            chunk = fp.read(BUFSIZE)
            if chunk.startswith(codecs.BOM_UTF8):
                i = 0
                chunk = chunk[BOMLEN:]
                while chunk:
                    fp.seek(i)
                    fp.write(chunk)
                    i += len(chunk)
                    fp.seek(BOMLEN, os.SEEK_CUR)
                    chunk = fp.read(BUFSIZE)
                fp.seek(-BOMLEN, os.SEEK_CUR)
                fp.truncate()

    def generate(self, gen=None, is_output=False):
        filename = self._get_next()

        if filename == self.in_processing():
            return

        self._filename = filename
        self._total = 0

        # Set source original name
        self.original = self._filename
        # Set Temp
        self._tmp = self.mod_tmp()
        # Move source to Temp
        self._move_source()

        source = self.tmp_source
        destination = gen or self.tmp_gen

        if self.is_trancate:
            Loader._truncate(source)

        fieldset = self.ordered_fieldset()
        keys = list(fieldset.keys())

        nodes = None
        tags = None

        # Incoming source
        fo = is_output and open(destination, 'wb') or None

        # Record data for multiple lines
        buffer = {'level' : 0, 'record' : b''}

        def gen_default(n, line, **kw):
            """
                Плоский файл с фиксированным разделителем: 
                AAA|BBB|...|CCC
            """
            n += 1
            values = self._split(line)
            return n, self._set_content(n, values=values, **kw)

        def gen_json(n, line, **kw):
            """
                JSON-формат
            """
            level = buffer['level'] + sum(list(filter(None, map(lambda x: x==123 and 1 or x==125 and -1 or None, 
                list(line)))))
            buffer['record'] += line
            buffer['level'] = level
            if level == 0:
                try:
                    values = json.loads(buffer['record'].decode(self._encoding))
                    values = [values.get(key) for key in kw.get('keys')]
                except:
                    raise LoaderException('JSONLoadsError:00:recno[%d]' % n)
                buffer['record'] = b''
                n += 1
                return n, self._set_content(n, values=values, **kw)
            return n, None

        def gen_dat(n, line, **kw):
            """
                Плоский файл с именами полей и фиксированным разделителем: 
                RECID#00000002#;PAN#4059910016908313#;MTrack1#B4059910016908313^MATIUSHENKO/ALEKSEI^23082011936100880000000#;...
            """
            n += 1
            values = []
            items = self._split(line)
            keys = self.ordered_keys(kw.get('fieldset'))
            for i, key in enumerate(keys):
                if i >= len(items):
                    raise LoaderException('ValueError:00:LineSize[%s]:recno[%d]' % (key, n))
                x = items[i].decode(self._encoding).split('#')
                name, value = x[0], x[1]
                if name != key:
                    raise LoaderException('ValueError:00:Key[%s]:recno[%d]' % (key, n))
                else:
                    values.append(value)
            return n, self._set_content(n, values=values, **kw)

        def gen_tlv(n, line, **kw):
            """
                TLV-формат:
                ~ELN1#00000194058 7031 0287 6333~ELN2#0000016           11/22~ELN3#0000026TEST           KONA2 D2320~ELN4#0000000
            """
            n += 1
            values = []
            items = list(filter(None, self._split(line)))
            is_stripped = self.incoming.get('is_stripped') and True or False
            keys = self.ordered_keys(kw.get('fieldset'))
            for i, key in enumerate(keys):
                if i >= len(items):
                    raise LoaderException('ValueError:00:LineSize[%s]:recno[%d]' % (key, n))
                x = items[i].decode(self._encoding).split('#')
                name, value = x[0], x[1]
                length, value = int(value[0:7]), value[7:]
                if key and name != key:
                    raise LoaderException('ValueError:00:Key[%s]:recno[%d]' % (key, n))
                elif len(value) != length:
                    raise LoaderException('ValueError:00:Length[%s]:recno[%d]' % (key, n))
                else:
                    if is_stripped:
                        value = value.strip()
                    values.append(value)
            return n, self._set_content(n, values=values, **kw)

        def gen_pm_prs(n, node, **kw):
            """
                Формат PM_PRS (OpenWay)
            """
            n += 1
            values = []
            keys = self.ordered_keys(kw.get('fieldset'))
            for i, key in enumerate(keys):
                tag = tags.get(key)
                if not tag:
                    value = None
                else:
                    query = tag[0]
                    obs = node.findall(query, namespaces)
                    value = FMT_GetChildren(obs, key)
                # Tag's value with override (last list item: -1)
                values.append(value and isIterable(value) and value[-1] or value or None)
            return n, self._set_content(n, values=values, **kw)

        # Type of content
        content_generator, mode, fi = gen_default, 'rb', None

        if not self._format:
            pass
        elif self._format == FILE_FORMAT_JSON:
            content_generator = gen_json
        elif self._format == FILE_FORMAT_DAT:
            content_generator = gen_dat
        elif self._format == FILE_FORMAT_TLV:
            content_generator = gen_tlv
        elif self._format == FILE_FORMAT_PM_PRS:
            fi = ET.parse(source)
            root = fi.getroot()
            namespaces = self.incoming.get('namespaces')
            data = self.incoming.get('data')
            nodes = namespaces and data and root.findall(data, namespaces) or None
            tags = self.incoming.get('tags')
            content_generator = gen_pm_prs

        n = 0
        header_skipped = False

        if fi is None:
            with open(source, mode) as fi:
                self._write(fo, self._set_header(self._location, self._filename))

                for line in fi:
                    if not line or len(line) == 0:
                        continue

                    if self.with_header and not header_skipped:
                        header_skipped = True
                        continue

                    n, data = content_generator(n, line, fieldset=fieldset, keys=keys)
                    if data is None:
                        continue

                    record = self.record_iter(n, data, encoding=self._encoding, fieldset=fieldset, keys=keys)
                    if record:
                        self._write(fo, '%(cr)s%(record)s' % {
                            'record' : record,
                            'cr'     : cr,
                        })

                self._write(fo, self._set_footer(n))
        
        else:
            if nodes:
                self._write(fo, self._set_header(self._location, self._filename))

                for node in nodes:
                    n, data = content_generator(n, node, keys=keys, fieldset=fieldset)
                    if data is None:
                        continue

                    record = self.record_iter(n, data, encoding=self._encoding, keys=keys, fieldset=fieldset)
                    if record:
                        self._write(fo, '%(cr)s%(record)s' % {
                            'record' : record,
                            'cr'     : cr,
                        })

                self._write(fo, self._set_footer(n))

        if fo is not None:
            fo.close()

        self.total = n
        
        # Check existance of the loading filename
        if self.checkFileExists(filename):
            self._forced_status = STATUS_REJECTED_DUBLICATE
        
        # Check file is empty
        elif not self.total:
            self._forced_status = STATUS_REJECTED_EMPTY

        self._logger('--> Total records:%s' % n, True)

    def outgoing(self, is_error=False):
        """
            Create outgoing
        """
        filename = self.in_processing()
        fieldset = self.ordered_fieldset()
        keys = list(fieldset.keys())

        super().outgoing(is_error=is_error, fieldset=fieldset, keys=keys, filename=filename)


class AbstractIncomingLoaderClass(Loader):
    """
        Abstract Order Data Loader class.
        Used for upload incoming data into Order objects.

        Supplied to Modules:
        - loader
    """

    def __init__(self, connection, basedir, logger):
        if IsDeepDebug:
            print('AbstractIncomingLoaderClass init')

        super().__init__(connection, basedir, logger)

        self._filetype = ''
        self._id = None

        self.incoming = None

    def _init_state(self, attrs=None, service=None):
        if IsDeepDebug:
            print('AbstractIncomingLoaderClass initstate')

        super()._init_state(attrs, service)

        # Incoming filetype descriptor
        self.incoming = attrs.get('incoming')

        self.validate()

    @property
    def id(self):
        """
            A new Order FileID: int.
        """
        return self._id
    @id.setter
    def id(self, value):
        self._id = value

    @property
    def filetype(self):
        return self._filetype

    @property
    def is_trancate(self):
        return self.incoming.get('is_trancate') and True or False

    def validate(self):
        if not self.incoming:
            return

        self._format = self.incoming.get('format') or FILE_FORMAT_CSV

        self._filetype = self.incoming.get('filetype')
        self._location = self.incoming.get('location')
        self._encoding = self.incoming.get('encoding') or ENCODING_WINDOWS

        self.fieldset = self.incoming.get('fieldset')
        self.defaults = self.incoming.get('defaults')

    def listdir(self):
        mask = self.incoming.get('mask') and re.compile(self.incoming['mask'], re.I+re.DOTALL) or None
        return self._location and [x for x in os.listdir(self._location) if not mask or mask.match(x)] or []

    def _set_header(self, location, filename):
        return '<?xml version="1.0" encoding="%(encoding)s"?>' \
               '%(cr)s<FileData>' \
               '%(cr)s<FileInfo>' \
               '%(cr)s<InputFolder>%(location)s</InputFolder>' \
               '%(cr)s<InputFileName>%(filename)s</InputFileName></FileInfo>' \
               '%(cr)s<FileBody>' % {
                    'encoding'  : self._encoding,
                    'location'  : location.replace('/', '\\'),
                    'filename'  : filename,
                    'cr'        : cr,
                }

    def _set_footer(self, n):
        return '%(cr)s</FileBody>' \
               '%(cr)s<ProcessInfo>' \
               '%(cr)s<ProcessedRecordQty>%(processed)d</ProcessedRecordQty>' \
               '%(cr)s<ProcessDateTime>%(now)s</ProcessDateTime></ProcessInfo>%(cr)s</FileData>' % {
                    'processed' : n, 
                    'now'       : getDate(getToday(), UTC_FULL_TIMESTAMP),
                    'cr'        : cr,
                }

    def _split(self, line, splitter=None):
        return line.strip().split(self.incoming['field_delimeter'])

    def _set_content(self, n, keys=None, fieldset=None, values=None):
        tags = []

        if len(values) != len(keys):
            raise LoaderException('ValueError:00:recno[%d]' % n)

        for i, key in enumerate(keys):
            number, name, field_type, data_type, perso_type, encoding, size, is_obligatory, comment = \
                self.get_field(key, fieldset[key])

            if i < len(values):
                if not isinstance(values[i], bytes):
                    value = str(values[i] or '')
                else:
                    value = (values[i] or b'').decode(encoding)
            else:
                raise LoaderException('IndexError:00:recno[%d]' % n)

            if encoding != self._encoding:
                value = value.encode(self._encoding).decode(self._encoding)

            if self.mod_validator is not None:
                value = self.mod_validator(value)

            tags.append('%(cr)s<%(key)s>%(value)s</%(key)s>' % {
                'key'    : key, 
                'value'  : value,
                'cr'     : cr,
            })

        s = '<FileBody_Record>%(cr)s<FileRecNo>%(rowno)08d</FileRecNo>%(tags)s%(cr)s</FileBody_Record>' % {
                'rowno'  : n, 
                'tags'   : ''.join(tags),
                'cr'     : cr,
        }
        return s

    def on_before(self):
        """
            On Before Run custom
        """
        self.open()

    def on_after(self, statuses, with_body_update=False, is_error=False):
        """
            On After Run custom
        """
        self.compImage()

        status = self.get_status(statuses, is_error=is_error)
        lastrowid = None

        if not self.uploadOrder(status):
            is_error = True
            self._logger('>>> Cannot upload a new Order!', force=True, is_error=is_error)
        else:
            self.compBody()
            lastrowid = self.setBody(self.id, status, with_commit=True)

        self.close()

        # Finished with result
        self.code = not is_error and lastrowid and HANDLER_CODE_SUCCESS or HANDLER_CODE_ERROR

    def uploadOrder(self, status):
        attrs = {
            'FName'        : self.in_processing(),
            'FileType'     : self.filetype,
            'FQty'         : self.total,
            'FileStatusID' : status,
            'ReadyDate'    : None,
        }

        file_id = None
        is_error = False

        try:
            self.addNewOrder(attrs) #, with_commit=True
            file_id = attrs.get('FileID')

            if not file_id:
                return

            self.id = file_id
        except:
            if IsPrintExceptions:
                print_exception()
            is_error = True

        return not is_error and file_id and True or False

    def genXml(self):
        try:
            self.generate(is_output=True)
        except UnicodeError as ex:
            self.code = HANDLER_CODE_ERROR
            print_to(None, 'AbstractIncomingLoaderClass.genXml: UnicodeError[%s]' % self.in_processing())
            if IsPrintExceptions:
                print_exception()
        except LoaderException as ex:
            self.code = HANDLER_CODE_ERROR
            print_to(None, 'AbstractIncomingLoaderClass.genXml: %s[%s]' % (ex, self.in_processing()))
            if IsPrintExceptions:
                print_exception()
        except:
            raise

        if IsDeepDebug:
            print_to(None, '>>> %s' % self.tmp_gen)

    main = genXml


class AbstractReferenceLoaderClass(Loader):
    """
        Abstract Reference Loader class.
        Used for upload data into linked Dictionaries SQL objects.

        Supplied to Modules:
        - loader
    """

    def __init__(self, connection, basedir, logger):
        if IsDeepDebug:
            print('AbstractReferenceLoaderClass init')

        super().__init__(connection, basedir, logger)

        self.reference = None

    def _init_state(self, attrs=None, service=None):
        if IsDeepDebug:
            print('AbstractReferenceLoaderClass initstate')

        super()._init_state(attrs, service)

        # Reference filetype descriptor
        self.reference = attrs.get('reference')

        self.validate()

    @property
    def with_header(self):
        return self.reference.get('with_header') and True or False

    def validate(self):
        if not self.reference:
            return

        self._filetype = self.reference.get('filetype')
        self._location = self.reference.get('location')
        self._encoding = self.reference.get('encoding') or ENCODING_WINDOWS

        self.fieldset = self.reference.get('fieldset')
        self.defaults = self.reference.get('defaults')

    def auto_check_parameters(self, data):
        if IsDeepDebug and IsTrace:
            print('>>> core.AbstractReferenceLoaderClass.auto_check_parameters')

        fieldset = self.ordered_fieldset()
        keys = list(fieldset.keys())

        codes = dict([(key, checkTagParameters(
                    i, 
                    key, 
                    self.get_field(key, fieldset.get(key)), 
                    data.get(key)
                )
            ) for i, key in enumerate(keys)])

        self._checker = (keys, codes,)

    def listdir(self):
        mask = self.reference.get('mask') and re.compile(self.reference['mask'], re.I+re.DOTALL) or None
        return self._location and [x for x in os.listdir(self._location) if not mask or mask.match(x)] or []

    def _split(self, line, splitter=None):
        return line.strip().split(self.reference['field_delimeter'])

    def _set_content(self, n, keys=None, fieldset=None, values=None):
        """
            Content line generator.

            Arguments:
                n        -- Int, record number
                keys     -- Tuple, line fields list
                fieldset -- Dict, filetype fields descriptor
                values   -- List, line's data

            Returns:
                data: Dict, line's decoded data.
        """
        data = {}

        if len(values) != len(keys):
            raise LoaderException('ValueError:00:recno[%d]' % n)

        for i, key in enumerate(keys):
            number, name, field_type, data_type, perso_type, encoding, size, is_obligatory, comment = \
                self.get_field(key, fieldset[key])

            if i < len(values):
                value = (values[i] or b'').decode(encoding)
            else:
                raise LoaderException('IndexError:00:recno[%d]' % n)

            if encoding != self._encoding:
                value = value.encode(self._encoding).decode(self._encoding)

            if self.mod_validator is not None:
                value = self.mod_validator(value)

            data[key] = value != '-' and value or ''

        self.auto_check_parameters(data)

        return data

    def on_before(self):
        """
            On Before Run custom
        """
        self.open(0)

    def on_after(self, with_body_update=False, is_error=False):
        """
            On After Run custom
        """
        self.close(is_error=is_error)

        # Finished with result
        self.code = not is_error and self.total > 0 and HANDLER_CODE_SUCCESS or HANDLER_CODE_ERROR

    def genReference(self):
        try:
            self.generate(is_output=False)
        except UnicodeError as ex:
            self.code = HANDLER_CODE_ERROR
            print_to(None, 'AbstractReferenceLoaderClass.genReference: UnicodeError[%s]' % self.in_processing())
            if IsPrintExceptions:
                print_exception()
        except LoaderException as ex:
            self.code = HANDLER_CODE_ERROR
            print_to(None, 'AbstractReferenceLoaderClass.genReference: %s[%s]' % (ex, self.in_processing()))
            if IsPrintExceptions:
                print_exception()
        except:
            raise

        if IsDeepDebug:
            print_to(None, '>>> %s' % self.tmp_gen)

    main = genReference


class AbstractMergeClass(Connection, Base):
    """
        Abstract Order Merge class.
        Used for merging of the existed Order IBody content.

        Supplied to Modules:
        - order_merge
    """

    _default_tags = ('FileInfo', 'FileBody_Record', 'ProcessInfo',)

    def __init__(self, connection, basedir, logger):
        if IsDeepDebug:
            print('AbstractMergeClass init')

        super().__init__(connection, basedir, logger)

        # A new order attributes
        self._base_filename = ''
        self._id = None
        self._filetype = None
        self._status = None
        self._destination = ''
        self._count = 0
        self._fo = None

        # Default IBody tags 1-st level structure
        self._tags = self.__class__._default_tags
        # Default encoding for output
        self._encoding = default_encoding

        # Resulting file descriptor
        self._files = {}
        # List of orders to merge
        self._orders = None

        self.mod_clock = None
        self.mod_tags = None

        self.done = False

    def _init_state(self, filetype, orders, attrs=None, factory=None, service=None):
        if IsDeepDebug:
            print('AbstractReferenceLoaderClass initstate')

        super()._init_state(attrs, service)

        # Filetype
        self._filetype = filetype
        # Filetype factory
        self._factory = factory.get(self._filetype)
        # Merged order list
        self._orders = orders

        if isinstance(self._factory, dict):
            self.fieldset = self._factory.get('fieldset')
            self.defaults = self._factory.get('defaults')

        # Ext Module members
        self.mod_clock = Base.set_mod('clock', attrs)
        self.mod_activate = Base.set_mod('activate', attrs)
        self.mod_deactivate = Base.set_mod('deactivate', attrs)
        self.mod_custom = Base.set_mod('custom', attrs)
        self.mod_filename = Base.set_mod('filename', attrs)
        self.mod_tags = Base.set_mod('tags', attrs)

        # Temp
        self._tmp = self.mod_tmp()

        # Total records written
        self._total = 0

        # custom's saveback area
        self._saveback = {
            'base'   : Base,
            'errors' : [],
        }

        self._code = HANDLER_CODE_UNDEFINED

    @property
    def order(self):
        return self._order
    @property
    def id(self):
        """
            A new Order FileID: int.
        """
        return self._id
    @id.setter
    def id(self, value):
        self._id = value
    @property
    def filetype(self):
        return self._filetype
    @property
    def count(self):
        return self._count
    @property
    def ids(self):
        """
            Collection of the created order files ids
        """
        return [self._files[key]['id'] for key in self._files]
    @property
    def keys(self):
        """
            String of the created order files keys: 'S:P:D'
        """
        return ':'.join(self._files.keys())

    def ready(self):
        return len(self._orders) > 0 and True or False

    def _set_header(self, location, filename):
        return '<?xml version="1.0" encoding="%(encoding)s"?>' \
               '%(cr)s<FileData>' \
               '%(cr)s<FileInfo>' \
               '%(cr)s<InputFolder>%(location)s</InputFolder>' \
               '%(cr)s<InputFileName>%(filename)s</InputFileName></FileInfo>' \
               '%(cr)s<FileBody>' % {
                    'encoding'  : self._encoding,
                    'location'  : location.replace('/', '\\'),
                    'filename'  : filename,
                    'cr'        : cr,
                }

    def _set_footer(self, n):
        return '</FileBody>' \
               '%(cr)s<ProcessInfo>' \
               '%(cr)s<ProcessedRecordQty>%(processed)d</ProcessedRecordQty>' \
               '%(cr)s<ProcessDateTime>%(now)s</ProcessDateTime></ProcessInfo>%(cr)s</FileData>' % {
                    'processed' : n, 
                    'now'       : getDate(getToday(), UTC_FULL_TIMESTAMP),
                    'cr'        : cr,
                }

    def _get_next(self):
        return self._orders.pop(0)

    next = _get_next

    def _write(self, s):
        if s is None:
            return
        self._fo.write(s.encode(self._encoding))

    def on_activate(self):
        """
            On Activate Run custom
        """
        self.open()

    def on_create(self, key):
        """
            On Create a new order file with the given key
        """
        # Open the output resulting file
        self._fo = open(self._destination, 'wb')

        # Set file header
        self._write(self._set_header(self._tmp % '', self._filename))

        # Register
        self._files[key]['fo'] = self._fo

    def switch_file(self, key, inc=False):
        ob = self._files.get(key)

        if ob is None:
            # ----------------------------------------
            # Create and register a new order filename
            # ----------------------------------------

            # Filename
            filename = self.mod_filename(self._base_filename, key, self._filetype)
            # Temp
            self._tmp = self.mod_tmp(filename)
            # Destination full filename
            destination = self.tmp_gen

            ob = {
                'fo'          : None,
                'count'       : 0,
                'filename'    : filename,
                'tmp'         : self._tmp,
                'destination' : destination,
                'id'          : None,
                'lastrowid'   : None,
            }
            self._files[key] = ob
        
        if inc:
            # Increment records count
            ob['count'] += 1

        # ----------------------------------
        # Switch to the given order filename
        # ----------------------------------

        self._fo = ob['fo']
        self._count = ob['count']
        self._filename = ob['filename']
        self._tmp = ob['tmp']
        self._destination = ob['destination']

        if self._fo is None:
            self.on_create(key)

        return self._fo

    def on_close(self, key):
        """
            On Close
        """
        # Set file footer
        self._write(self._set_footer(self._count))

        # Close the output resulting file
        self._fo.close()

    def on_deactivate(self):
        """
            On Deactivate Run custom
        """
        is_error = self.code == HANDLER_CODE_ERROR and True or False

        # Add a new order with the given status
        status = self._status

        for key in self._files:
            self.switch_file(key)

            self.on_close(key)

            if self._count == 0:
                continue

            lastrowid = None

            if not self.uploadOrder(status):
                is_error = True
                self._logger('>>> Cannot upload a new Order!', force=True, is_error=is_error)
            else:
                self._files[key]['id'] = self._id

                self.compBody()
                lastrowid = self.setBody(self._id, status)

                if not lastrowid:
                    raise Exception('Core.AbstractMergeClass[on_deactivate], key:%s' % key)

                self._files[key]['lastrowid'] = lastrowid

            self.clean()

        self.close(is_error=is_error)

        # Merging done
        self.done = True

        # Finished with result
        self.code = not is_error and HANDLER_CODE_SUCCESS or HANDLER_CODE_ERROR

    def on_before(self):
        """
            On Before Run custom
        """
        id = self._order.id
        filename = self._order.filename
        status = self._order.status_from

        # Temp
        self._tmp = self.mod_tmp(filename)

        body = self.getBody(id, status)

        if body is None:
            self._logger('>>> No body: %s %s' % (id, status), is_error=True)
            self.code = HANDLER_CODE_ERROR
            return

        self.dumpBody(body)
        self.makeXml(body)

        body = None
        del body

    def on_after(self, is_error=False):
        """
            On After Run custom
        """
        if not is_error:
            self._logger('>>> OK', True)
        else:
            self._logger('>>> Error', True)

        # Finished with result
        self.code = not is_error and HANDLER_CODE_SUCCESS or HANDLER_CODE_ERROR

    def generate(self, gen=None, is_output=False):
        filename, tags = self.tmp_xml, self._tags

        begins = [('<%s>' % x).encode(default_encoding) for x in tags]
        ends = [('</%s>' % x).encode(default_encoding) for x in tags]

        total = self.total

        self.total = Base.readnodes(filename, None, begins, ends, self.record_iter, is_output=is_output, total=total)

        n = self.total - total

        self._logger('--> Records output:%s' % n, True)

    def setOrder(self, order):
        self._order = order

    def uploadOrder(self, status):
        attrs = {
            'FName'        : self.filename,
            'FileType'     : self.filetype,
            'FQty'         : self.count,
            'FileStatusID' : status,
            'ReadyDate'    : None,
        }

        file_id = None
        is_error = False

        try:
            self.addNewOrder(attrs, no_image=True) #, with_commit=True
            file_id = attrs.get('FileID')

            if not file_id:
                return

            self._id = file_id
        except:
            if IsPrintExceptions:
                print_exception()
            is_error = True

        return not is_error and file_id and True or False

    def genXml(self):
        if self.code != HANDLER_CODE_ERROR:
            self.generate(is_output=False)

        if IsDeepDebug:
            print_to(None, '>>> %s' % self.tmp_gen)

    main = genXml


def send_exception_info(subject, ex):
    if not ex.hasattr('_recipients'):
        return

    subject = subject
    message = str(ex)
    addr_to = ';'.join(ex['_recipients'])

    send_simple_mail(subject, message, addr_to)
