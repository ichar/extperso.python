# -*- coding: cp1251 -*-

# ------------------ #
#   otkrytie.check   #
# ------------------ #

__all__ = ['accept', 'error', 'outgoing', 'check_parameters', 'check_data']

import re

from config import (
    IsDebug, IsDeepDebug, IsDisableOutput, IsPrintExceptions,
    default_print_encoding, default_unicode, default_encoding, default_iso, cr,
    LOCAL_EASY_DATESTAMP, UTC_FULL_TIMESTAMP, DATE_STAMP,
    print_to, print_exception
)

from app.types.errors import *
from app.srvlib import *
from app.utils import normpath

from ..defaults import *
from ..filetypes.otkrytie import *
from ..xmllib import *

# ------------------------- #

"""
    Модуль Контроля входящего файла-заказа (автоконтроллер).

    = CHECK =

    Назначение модуля:
        1. Контроль параметров входящего файла.
        2. Контроль данных.
        3. Формирование исходящего файла-квитанции.
        4. Генерация дополнительных данных.
"""

# ------------------------- #

incoming = FILETYPE_OTKRYTIE_V1

encoding = DEFAULT_OUTGOING_TYPE.get('encoding')
eol = DEFAULT_EOL

# ========================= #

def accept(filename):
    return normpath('%s/%s/%s/%s.ACCEPT' % (DEFAULT_INCOMING_ROOT, FILETYPE_FOLDER, DEFAULT_TOBANK, filename))

def error(filename):
    return normpath('%s/%s/%s/%s.ERROR' % (DEFAULT_INCOMING_ROOT, FILETYPE_FOLDER, DEFAULT_TOBANK, filename))

# ========================= #

def _add_error(n, node, id, error, errors, saveback):
    errors.append(error)
    saveback['errors'].append((n, id, errors))
    FMT_XMLErrorRecord(node, errors)

def _check(node, logger, saveback, checker=None):
    """
        Базовый контроль параметров/данных
    """
    recno = getTag(node, 'FileRecNo')
    id = getTag(node, LOCAL_ID_TAG)

    res, errors = FMT_UnpackChecker(checker)

    if errors:
        saveback['errors'].append((recno, id, errors))
        FMT_XMLErrorRecord(node, errors)

    logger('--> Node: %s, codes[%s]' % (node.tag, res))

    return res, errors

# ------------------------- #

def check_parameters(n, node, logger, saveback, **kw):
    """
        Контроль параметров
    """
    if node.tag != 'FileBody_Record':
        return

    checker = kw.get('checker')

    res, errors = _check(node, logger, saveback, checker=checker)

def check_data(n, node, logger, saveback, **kw):
    """
        Контроль данных
    """
    if node.tag != 'FileBody_Record':
        return

    checker = kw.get('checker')

    res, errors = _check(node, logger, saveback, checker=checker)

    # --------------
    # Особые условия
    # --------------

    order = kw.get('order')

    # PAN
    PAN = re.sub(r'\s', '', getTag(node, 'PAN'))
    # Имя входящего файла
    orderfile = order.ordername

    # -------------------------------
    # Генерация дополнительных данных
    # -------------------------------

    return HANDLER_CODE_UNDEFINED

def outgoing(logger, saveback, is_error, **kw):
    """
        Файл-квитанция
    """
    makeOutgoing(logger, saveback, is_error, 
        accept=accept, 
        error=error, 
        get_error_code=local_GetErrorCode, 
        encoding=encoding, 
        eol=eol, 
        no_ext=False, 
        with_full_reject=False, 
        **kw
        )
