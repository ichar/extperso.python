# -*- coding: utf-8 -*-

__all__ = [
    'DEFAULT_INCOMING_ROOT',
    'DEFAULT_INCOMING_TYPE',
    'DEFAULT_REFERENCE_ROOT',
    'DEFAULT_REFERENCE_TYPE',
    'DEFAULT_LOYALTY_ROOT',
    'DEFAULT_LOYALTY_TYPE',
]

from app.core import AbstractIncomingLoaderClass, AbstractReferenceLoaderClass
from app.types import *

##  ===========================
##  Default FileType Attributes
##  ===========================

DEFAULT_INCOMING_ROOT = 'C:/USER/CLIENTDATA'

DEFAULT_INCOMING_TYPE = {
    'class'       : AbstractIncomingLoaderClass,
    'object_type' : FILE_TYPE_INCOMING_ORDER,
    'format'      : FILE_FORMAT_CSV,
    'field_type'  : DATA_TYPE_FIELD,
    'encoding'    : ENCODING_WINDOWS,
}

DEFAULT_REFERENCE_ROOT = 'C:/USER/CLIENTDATA'

DEFAULT_REFERENCE_TYPE = {
    'class'       : AbstractReferenceLoaderClass,
    'object_type' : FILE_TYPE_INCOMING_REFERENCE,
    'format'      : FILE_FORMAT_CSV,
    'field_type'  : DATA_TYPE_FIELD,
    'encoding'    : ENCODING_WINDOWS,
}

DEFAULT_LOYALTY_ROOT = 'C:/USER/CLIENTDATA'

DEFAULT_LOYALTY_TYPE = {
    'class'       : AbstractReferenceLoaderClass,
    'object_type' : FILE_TYPE_INCOMING_LOYALTY,
    'format'      : FILE_FORMAT_CSV,
    'field_type'  : DATA_TYPE_FIELD,
    'encoding'    : ENCODING_WINDOWS,
}
