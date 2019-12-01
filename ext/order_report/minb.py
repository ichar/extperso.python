# -*- coding: cp1251 -*-

__all__ = ['custom', 'output', 'tags']

from config import (
    IsDebug, IsDeepDebug, IsDisableOutput, IsPrintExceptions,
    default_print_encoding, default_unicode, default_encoding, default_iso, cr,
    LOCAL_EASY_DATESTAMP, UTC_FULL_TIMESTAMP, DATE_STAMP,
    print_to, print_exception
)

from ..defaults import *
from ..filetypes.minb import *

from ..xmllib import *

# ========================= #

def accept(order, logger):
    return r'%s/%s/ToBank/%s.ACCEPT' % (DEFAULT_OUTGOING_ROOT, FILETYPE_FOLDER, order.filename)

# ========================= #

def tags():
    return ('FileInfo', 'ProcessInfo',)

def custom(n, node, logger, saveback, **kw):
    value = \
        node.tag == 'FileInfo' and getTag(node, 'InputFileName') or \
        node.tag == 'ProcessInfo' and getTag(node, 'ProcessedRecordQty') or \
        ''
    return value and '%s' % value

# ------------------------- #
