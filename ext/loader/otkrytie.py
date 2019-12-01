# -*- coding: cp1251 -*-

# ------------------- #
#   otkrytie.loader   #
# ------------------- #

__all__ = ['incoming', 'validator', 'custom']

import re
from copy import deepcopy

from config import (
    IsDebug, IsDeepDebug, IsDisableOutput, IsPrintExceptions,
    default_print_encoding, default_unicode, default_encoding, default_iso, cr,
    LOCAL_EASY_DATESTAMP, UTC_FULL_TIMESTAMP, DATE_STAMP,
    print_to, print_exception
)

from app.modules.loader import BaseIncomingLoader
from app.types.errors import *
from app.srvlib import *
from app.utils import normpath

from ..defaults import *
from ..filetypes.otkrytie import *
from ..xmllib import *

# ------------------------- #

"""
    Модуль Загрузки входящих данных.

    = LOADER =

    Назначение модуля:
        1. Загрузка входящего файла заказа.
        2. Загрузка входящего файла справочника.
"""

# ------------------------- #

incoming = deepcopy(FILETYPE_OTKRYTIE_V1)

encoding = DEFAULT_INCOMING_TYPE.get('encoding')
eol = DEFAULT_EOL

incoming.update({
    'class'     : BaseIncomingLoader,
    'filetype'  : 'Otkrytie_v1',
    'location'  : '%s/%s/%s' % (DEFAULT_INCOMING_ROOT, FILETYPE_FOLDER, DEFAULT_FROMBANK), # DEFAULT_FROMSDC
    'mask'      : r'PM_PRS_0001_.*\.xml', # r'PM_PRS_.*\.txt'
    'encoding'  : DEFAULT_INCOMING_TYPE['encoding'],
})

# ========================= #

def accept(filename):
    return normpath('%s/%s/%s/%s.ACCEPT' % (DEFAULT_INCOMING_ROOT, FILETYPE_FOLDER, DEFAULT_TOBANK, filename))

def error(filename):
    return normpath('%s/%s/%s/%s.ERROR' % (DEFAULT_INCOMING_ROOT, FILETYPE_FOLDER, DEFAULT_TOBANK, filename))

# ========================= #

def validator(value):
    return value

def custom(n, node, logger, saveback, **kw):
    """
        Загрузчик записи входящего файла заказа
    """
    pass
