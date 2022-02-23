#!/usr/bin/env python

import datetime
import sys
import os
import types
import logging

from app.settings import *

is_v3 = sys.version_info[0] > 2 and True or False

basedir = ''

argv = sys.argv

_config = {}

##  =========================================================  ##

def _imports():
    for name, val in globals().items():
        if isinstance(val, types.ModuleType):
            yield val.__name__

def _pout(s, **kw):
    if not is_v3:
        print(s, end='end' in kw and kw.get('end') or None)
        if 'flush' in kw and kw['flush'] == True:
            sys.stdout.flush()
    else:
        print(s, **kw)

##  =========================================================  ##

def show_imported_modules():
    return [x for x in _imports()]

def info(line, force=None, is_error=False, is_warning=False, is_ok=False):
    if IsDisableOutput:
        return
    if is_error:
        logging.error(line)
    elif is_warning:
        logging.warning(line)
    elif IsTrace or force:
        logging.info(line)

def setup():
    sys.path.append(basedir)

def get_config_param(key):
    return _config.get(key)

def run(command):
    info('--> Started with ExtFolder: %s' % basedir)
    info('>>> now: %s' % getDate(getToday(), UTC_FULL_TIMESTAMP))

    code, errors = 0, []

    try:
        process(basedir=basedir, logger=info, service=get_config_param, command=command)

    except Exception as ex:
        response = hasattr(ex, 'response') and ex.response or None

        if response is not None:
            errors.append('%s: %s' % (str(ex), response.text))
        else:
            errors.append(str(ex))

        if IsPrintExceptions:
            print_exception()

        code = -1

    errors += get_errors()

    info('--> Finished')
    
    return code, errors

# ----
# HELP
# ----

if len(argv) == 1 or argv[1].lower() in ('/h', '/help', '-h', 'help', '--help', '/?'):
    _pout('--> Rosan Finance Inc.')
    _pout('--> BankPerso Python-Ext Application.')
    _pout('--> ')
    _pout('--> Format: perso.py <basedir>')
    _pout('--> ')
    _pout('--> Parameters:')
    _pout('--> ')
    _pout('-->   <basedir>:  path to the App extentions folder')
    _pout('--> ')
    _pout('--> Version %s' % product_version)
    
    sys.exit(0)

# ===================
# APPLICATION STARTER
# ===================

basedir = argv[1]
        
assert basedir, "Path to the App extentions folder is not present!"

is_default_config = len(argv) < 3
config_file = 'perso.config' if is_default_config else argv[2]

command = len(argv) > 3 and argv[3] or None

# -----------------
# Setup environment
# -----------------

setup()

from config import *
from app.utils import normpath, getToday, getTime, getDate, getDateOnly, checkDate, spent_time
from app.modules import process, get_errors, get_stdout

def make_config(source, encoding=default_encoding):
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
                value = normpath(os.path.join(basedir, value))

            _config[key] = value

    _config['now'] = getDate(getToday(), format=DATE_STAMP)

    return _config

today = getDate(getToday(), DATE_STAMP)

setErrorlog('traceback-%s-bankperso-default.log' % today)

# ----------------------------------------
# Service Events log (just console stdout)
# ----------------------------------------

log = normpath(os.path.join(LOG_PATH, '%s_%s.log' % (today, LOG_NAME)))

logging.basicConfig(
    filename=log,
    level=logging.DEBUG, 
    format='%(asctime)s\t%(levelname)-7.7s\t%(message)s',
    datefmt=UTC_FULL_TIMESTAMP
)

# -------------------
# Execute App Process
# -------------------

make_config(config_file)

code, errors = run(command)

if command:
    for x in errors:
        sys.stderr.write("%s\n" % x)

    stdout = get_stdout()

    if stdout:
        sys.stdout.write(stdout)

    if not code:
        code = len(errors)

sys.exit(code or 0)
