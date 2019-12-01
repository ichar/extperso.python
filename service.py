# -*- coding: cp1251 -*-

#from __future__ import _pout_function

import datetime
import sys
import os
import time
import threading

from functools import wraps
from imp import reload

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket

sys.path.append('C:/apps/perso')

import config
#from config import errorlog
from app.settings import *
from app.utils import normpath, getToday, getTime, getDate, getDateOnly, checkDate, spent_time

from app.modules import Console, BaseService

is_v3 = sys.version_info[0] > 2 and True or False

_DEFAULT_PROCESS_TIMEOUT = 1
_DEFAULT_CONSUMER_SLEEP = 1
_EOL = '\r\n'

_config = {}

##  =========================================================  ##

def delay(delay=0.):
    """
        Decorator delaying the execution of a function for a while
    """
    def wrap(f):
        @wraps(f)
        def delayed(*args, **kwargs):
            timer = threading.Timer(delay, f, args=args, kwargs=kwargs)
            timer.start()
        return delayed
    return wrap

def _pout(s, **kw):
    if not is_v3:
        print(s, end='end' in kw and kw.get('end') or None)
        if 'flush' in kw and kw['flush'] == True:
            sys.stdout.flush()
    else:
        print(s, **kw)

##  =========================================================  ##

class Logger(object):
    """
        Helper Logger Class
    """
    def __init__(self, service):
        self._service = service

        self._filename = None
        self._format = None
        self._datefmt = None

    def _init_state(self, **kw):
        self._filename = kw.get('filename')
        self._format = kw.get('format')
        self._datefmt = kw.get('datefmt')

    def out(self, message, levelname='INFO', mode='a'):
        if not self._filename:
            return
        with open(self._filename, mode, newline='') as fo:
            fo.write(self._format % {
                'asctime'   : getDate(getToday(), self._datefmt),
                'levelname' : levelname,
                'message'   : message or '',
            } + _EOL)

    def error(self, line):
        self.out(line, 'ERROR')

    def warning(self, line):
        self.out(line, 'WARNING')

    def ok(self, line):
        self.out(line, 'OK')

    def info(self, line):
        self.out(line, 'INFO')

    def message(self, line, force=None, is_error=False, is_warning=False, is_ok=False):
        if config.IsDisableOutput:
            return
        if is_error:
            self.error(line)
        elif is_warning:
            self.warning(line)
        elif is_ok:
            self.ok(line)
        elif config.IsTrace or force:
            self.info(line)


class ExtPersoWindowsService(win32serviceutil.ServiceFramework):
    """
        ExtPerso Windows Service Class
    """
    _svc_name_ = "default.config"
    _svc_display_name_ = "Default Perso Service"
    _svc_description_ = "Default Service Description"

    def __init__(self, args):
        self.__class__._svc_name_ = args[0]
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        #socket.setdefaulttimeout(60)

        # Just `_svc_name_` class attribute !!!
        self.config_source = normpath(os.path.join(config.basedir, args[0]))
        # Stop flag
        self.stop_requested = False
        # Restart flag
        self.restart_requested = False
        # Current date
        self.today = None
        # Daily Errorlog name
        self.errorlog = ''

        self._started = None
        self._finished = None

        self.is_evalute_date = False

        # Application logger instance
        self._logger = None
        # Service Config
        self._config = None
        #
        # Init/Reset state
        #
        self.reset()

    @staticmethod
    def _current_date():
        return getDate(getToday(), config.DATE_STAMP)

    @property
    def process_timeout(self):
        return float(self._config.get('timeout') or _DEFAULT_PROCESS_TIMEOUT)

    def _stop_logger(self):
        if not (hasattr(self, '_logger') and self._logger):
            return
        del self._logger

    def _start_logger(self):
        self._stop_logger()
        self._logger = Logger(self)

    def _out(self, line, force=None, is_error=False, is_warning=False):
        """
            Output Log to ExtPerso_*.log
        """
        if self._config.get('disableoutput'):
            return
        if is_error:
            self._logger.error(line)
        elif is_warning:
            self._logger.warning(line)
        elif self._config.get('trace') or force:
            self._logger.info(line)

    def _update_config(self):
        """
            Read Config
        """
        self._config = make_config(self.config_source)

    def _evolute_log(self):
        """
            Init Application Event Log
        """
        self._start_logger()

        # Service Events log (just console stdout)
        self.today = self._current_date()
        log = normpath(os.path.join(config.LOG_PATH, '%s_%s.log' % (self.today, config.LOG_NAME)))

        self._logger._init_state(
            filename=log,
            format='%(asctime)s\t%(levelname)-7.7s\t%(message)s',
            datefmt=config.UTC_FULL_TIMESTAMP
        )

    def _set_errorlog(self):
        """
            Set Daily Error Log
        """
        self.errorlog = (self._config.get('errorlog') % self._config).lower()
        config.setErrorlog(self.errorlog)

    def reset(self):
        # Application config, can be updated(freshed) every time on start
        self._update_config()
        # Make Application current date Event Log
        self._evolute_log()
        # Set Daily Error Log
        self._set_errorlog()

    def refresh(self):
        self._update_config()

        msg = 'Service refreshed'
        self._out('>>> %s' % msg, force=True)

        return msg

    def stop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.SvcStop()

    def SvcStop(self):
        # ====
        # Stop
        # ====
        self.stop_requested = True

        self._finished = getToday()
        self._out('==> Stopping of service at %s' % getDate(self._finished, config.UTC_FULL_TIMESTAMP))
        self._out('==> Spent time: %s sec' % spent_time(self._started, self._finished))

        win32event.SetEvent(self.stop_event)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_,'')
        )
        # =====
        # Start
        # =====
        self._started = getToday()
        self._out('==> Starting of service at %s' % getDate(self._started, config.UTC_FULL_TIMESTAMP))
        #
        # Try to start the service
        #
        self.main()

    def main(self, **kw):
        """
            Starter
        """
        self.stop_requested = False

        self.ReportServiceStatus(win32service.SERVICE_RUNNING)

        if self._config.get('trace'):
            self._out('>>> config: %s' % self.config_source)
            self._out('>>> errorlog: %s' % self.errorlog)

        try:
            self.run()
        except:
            config.print_exception()
            self._out('main thread exception (look at traceback.log)', is_error=True)

        self._stop_logger()

        if self.restart_requested:
            self.restart_requested = False

            reload(config)
            self.reset()

            self._out('==> Restart...', force=True)

            self.main()

    def run(self):
        """
            Run service
        """
        self._lock = threading.Lock()

        self._out('>>> ExtPerso Started, basedir: %s' % config.basedir)

        console = Console(args=(config.basedir, self._logger.message, self._config, 3, self, self._lock))

        try:
            console.start()

            while not self.stop_requested:
                self.is_evalute_date = False

                with self._lock:
                    if self.restart_requested:
                        break
                    if self.today != self._current_date():
                        self.is_evalute_date = True

                if self.is_evalute_date:
                    self.reset()

                process = BaseService(args=(config.basedir, self._logger.message, self._config, self._lock))
                process.start()
                process.join()

                time.sleep(self.process_timeout)

        finally:
            if console.is_running():
                console.should_be_stop()
                console.join()

        self._out('>>> ExtPerso Finished')


def make_config(source, encoding=config.default_encoding):
    global _config
    with open(source, 'r', encoding=encoding) as fin:
        for line in fin:
            s = line
            if line.startswith(';') or line.startswith('#'):
                continue
            x = line.split('::')
            if len(x) < 2:
                continue

            key = x[0].strip()
            value = x[1].strip()

            if not key:
                continue
            elif '|' in value:
                value = value.split('|')
            elif value.lower() in 'false:true':
                value = True if value.lower() == 'true' else False
            elif value.isdigit():
                value = int(value)
            elif key in ':console:':
                value = normpath(os.path.join(config.basedir, value))

            _config[key] = value

    _config['now'] = getDate(getToday(), format=config.DATE_STAMP)

    return _config

def isStandAlone(argv):
    return len(argv) > 0 and argv[0].endswith('.exe')

def base(argv):
    return isStandAlone(argv) and os.path.abspath(os.path.dirname(servicemanager.__file__)) or config.basedir

def setup(name, source):
    title, description = _config.get('service_name')

    if name:
        ExtPersoWindowsService._svc_name_ = name
    if title:
        ExtPersoWindowsService._svc_display_name_ = title
    if description:
        ExtPersoWindowsService._svc_description_ = '%s, basedir: %s. Version %s' % (description, config.basedir, product_version)
    
    win32serviceutil.HandleCommandLine(ExtPersoWindowsService, customInstallOptions='s:')


if __name__ == '__main__':
    argv = sys.argv

    if len(argv) == 1 and isStandAlone(argv):
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(ExtPersoWindowsService)
        servicemanager.Initialize(ExtPersoWindowsService._svc_name_, os.path.abspath(servicemanager.__file__))
        servicemanager.StartServiceCtrlDispatcher()

    elif len(argv) == 1 or argv[1].lower() in ('/h', '/help', '-h', 'help', '--help', '/?'):
        _pout('--> Rosan Finance Inc.')
        _pout('--> ExtPerso Windows service.')
        _pout('--> ')
        _pout('--> Format: service.py [-s <config>] [options] install|update|remove|start [...]|stop|restart [...]|debug [...]')
        _pout('--> ')
        _pout('--> Parameters:')
        _pout('--> ')
        _pout('-->   <config>              :')
        _pout('-->         Name of the script config-file from current directory, by default: `default.config`,')
        _pout('-->         where should be defined `service_name` parameter')
        _pout('-->         such as <Service Name|Description>:')
        _pout('--> ')
        _pout('-->         ExtPerso Default Service|ExtPerso Default Windows Service Description')
        _pout('--> ')
        _pout('--> Service options:')
        _pout('--> ')
        _pout('-->   --username <name>     : ')
        _pout('-->         Domain and Username, name: `domain\\username` the service is to run under')
        _pout('--> ')
        _pout('-->   --password <password> :')
        _pout('-->         The password for the username')
        _pout('--> ')
        _pout('-->   --startup <mode>      :')
        _pout('-->         How the service starts, mode: [manual|auto|disabled|delayed], default = manual')
        _pout('--> ')
        _pout('-->   --interactive         :')
        _pout('-->         Allow the service to interact with the desktop')
        _pout('--> ')
        _pout('-->   --perfmonini <file>   :')
        _pout('-->         Path to .ini file to use for registering performance monitor data')
        _pout('--> ')
        _pout('-->   --perfmondll <file>   :')
        _pout('-->         Path to .dll file to use when querying the service for')
        _pout('-->         performance data, default = perfmondata.dll')
        _pout('--> ')
        _pout('--> Options for `start` and `stop` commands only:')
        _pout('--> ')
        _pout('-->   --wait <seconds>      :')
        _pout('-->         Wait for the service to actually start or stop.')
        _pout('-->         If you specify `--wait` with the `stop` option, the service')
        _pout('-->         and all dependent services will be stopped, each waiting')
        _pout('-->         the specified period.')
        _pout('--> ')
        _pout('--> Version %s' % product_version)

    elif len(argv) > 1 and argv[1]:

        # -----------
        # Config path
        # -----------
        
        is_default_config = len(argv) < 4 and argv[1] != '-s'
        config_file = 'perso.config' if is_default_config else argv[2]
        
        assert config_file, "Config file name is not present!"

        # --------------
        # Make `_config`
        # --------------

        make_config(config_file)

        # -------------
        # Source folder
        # -------------
        
        source = normpath(_config.get('root') or './')

        # ===============
        # Install Service
        # ===============

        setup(config_file, source)
