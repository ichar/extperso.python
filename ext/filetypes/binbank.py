# -*- coding: cp1251 -*-

# ---------------------- #
#   postbank filetypes   #
# ---------------------- #

__all__ = ['FILETYPE_FOLDER']

from app.core import AbstractIncomingLoaderClass, AbstractReferenceLoaderClass
from app.types import *
from app.srvlib import makeFileTypeIndex

from ..defaults import *

# ------------------------- #

FILETYPE_FOLDER = 'BIN_BANK'
