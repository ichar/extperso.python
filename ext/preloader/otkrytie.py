# -*- coding: cp1251 -*-

# ---------------------- #
#   otkrytie.preloader   #
# ---------------------- #

__all__ = ['incoming', 'custom', 'outgoing']

import re
from copy import deepcopy

from config import (
    IsDebug, IsDeepDebug, IsDisableOutput, IsPrintExceptions,
    default_print_encoding, default_unicode, default_encoding, default_iso, cr,
    LOCAL_EASY_DATESTAMP, UTC_FULL_TIMESTAMP, DATE_STAMP,
    print_to, print_exception
)

from app.modules.preloader import BaseOpenwayPreloaderClass
from app.types.errors import *
from app.srvlib import *
from app.utils import normpath

from ..defaults import *
from ..filetypes.otkrytie import *
from ..xmllib import *

# ------------------------- #

"""
    Модуль Предобработки входящих данных.

    = PRELOADER =

    Назначение модуля:
        1. Предварительная обработка входящего персофайла.
"""

# ------------------------- #

incoming = deepcopy(PRELOADER)

encoding = DEFAULT_INCOMING_TYPE.get('encoding')
eol = DEFAULT_EOL

incoming.update({
    'class'     : BaseOpenwayPreloaderClass,
    'filetype'  : 'Otkrytie_v1',
    'location'  : '%s/%s/%s' % (DEFAULT_INCOMING_ROOT, FILETYPE_FOLDER, DEFAULT_FROMBANK),
    'mask'      : r'PM_PRS_.*\.xml',
    'encoding'  : encoding,
})

# ========================= #

def ToArchive():
    return '%s/%s/%s' % (DEFAULT_INCOMING_ROOT, FILETYPE_FOLDER, DEFAULT_ARCHIVE)

def ToBank():
    return '%s/%s/%s' % (DEFAULT_OUTGOING_ROOT, FILETYPE_FOLDER, DEFAULT_TOBANK)

def ToSDC():
    return '%s/%s/%s' % (DEFAULT_INCOMING_ROOT, FILETYPE_FOLDER, DEFAULT_FROMBANK_PACKAGE)

def ok(filename):
    return normpath('%s/%s.OK' % (ToBank(), filename)) # .split('.')[0]

# ========================= #

def custom(root, logger, saveback, **kw):
    """
        Предобработка файла заказа
    """
    filename = kw.get('filename')

    namespaces = {'ns':'http://namespaces.globalplatform.org/systems-messaging/1.0.0'}
    n = 0

    try:
        jobs = root.find('PMJobs')
        obs = jobs.findall(".//ns:DataSet[@Name='ADDI']/ns:Data[@DataElement='ADD3']", namespaces)

        values = FMT_GetChildren(obs, 'ADD3')
        n = values and len(values) or 0
    except:
        print_to(None, ['', 'preloader.otkrytie cannot read incoming file: [%s], root: %s' % (filename, root)])
        if IsPrintExceptions:
            print_exception()

    actions = kw.get('actions')

    if not n:
        return 0

    if actions is not None:
        info = '%s, rows=%s' % (filename, n)
        actions.add('preloader.otkrytie', 'copy', (filename, ToArchive()), info)
        actions.add('preloader.otkrytie', 'move', (filename, ToSDC()), info)

    return n

def outgoing(logger, saveback, is_error, **kw):
    """
        Файл-квитанция
    """
    if is_error:
        return

    makeOutgoing(logger, saveback, is_error, 
        ok=ok, 
        encoding=encoding, 
        eol=eol, 
        no_ext=False, 
        empty_file=True, 
        **kw
        )
