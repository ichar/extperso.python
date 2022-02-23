# -*- coding: utf-8 -*-

__all__ = [
    'DEFAULT_OUTGOING_ROOT',
    'DEFAULT_OUTGOING_TYPE',
]

from app.types import *

##  ===========================
##  Default FileType Attributes
##  ===========================

DEFAULT_OUTGOING_ROOT = '//172.19.12.110'

DEFAULT_OUTGOING_TYPE = {
    'object_type' : FILE_TYPE_OUTGOING_ORDER,
    'format'      : FILE_FORMAT_CSV,
    'field_type'  : DATA_TYPE_FIELD,
    'encoding'    : ENCODING_WINDOWS,
}
