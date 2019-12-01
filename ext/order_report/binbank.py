# -*- coding: cp1251 -*-

__all__ = ['custom', 'output', 'tags']

from config import (
    IsDebug, IsDeepDebug, IsDisableOutput, IsPrintExceptions,
    default_print_encoding, default_unicode, default_encoding, default_iso, cr,
    LOCAL_EASY_DATESTAMP, UTC_FULL_TIMESTAMP, DATE_STAMP,
    print_to, print_exception
)

from ..defaults import *
from ..filetypes.binbank import *

from ..xmllib import *

# ========================= #

def accept(order, logger):
    return r'%s/%s/ToBank/%s.ACCEPT' % (DEFAULT_OUTGOING_ROOT, FILETYPE_FOLDER, order.filename)

# ========================= #

def tags():
    return ('FileBody_Record',)

def custom(n, node, logger, saveback, **kw):
    if node.tag != 'FileBody_Record':
        return None

    return '%s:%s:%s:%s' % (
        getTag(node, 'ProcessSortID'), getTag(node, 'FileRecNo'), getTag(node, 'PAN'), getTag(node, 'EMBNAME1'), 
        )

# ------------------------- #
