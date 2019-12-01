# -*- coding: cp1251 -*-

# ------------ #
#   defaults   #
# ------------ #

from .incoming import *
from .outgoing import *

DEFAULT_ARCHIVE          = 'Archive'
DEFAULT_FROMBANK         = 'FromBank'
DEFAULT_FROMBANK_PACKAGE = 'FromBank_Package'
DEFAULT_TOBANK           = 'ToBank'
DEFAULT_FROMSDC          = 'FromSDC'

DEFAULT_PACKAGE_LIMIT    = 500


def everything():
    return ('FileInfo', 'FileBody_Record', 'ProcessInfo',)

def fileinfo():
    return ('FileInfo',)

def processinfo():
    return ('ProcessInfo',)
