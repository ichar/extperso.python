# -*- coding: cp1251 -*-

import re

from .types import *
from .utils import isIterable

## ===================================
## CORE: DATA CHECKER PUBLIC FUNCTIONS
## ===================================

def checkFieldHeaders(index, key, field, value):
    """
        Проверить заголовки поля входящего файла.
        
        Аргументы:
            index  -- Int, порядковый номер поля
            key    -- String, имя поля
            field  -- Tuple, дескриптор поля <filetypes>.fieldset item
            value  -- String, значение поля

        Возврат:
            String, OK или код ошибки <app.errors>.
    """
    code = CHECKER_OK

    number, name, field_type, data_type, perso_type, encoding, size, is_obligatory, comment = field

    return code

def is_valid_integer(value):
    return value and value.isdigit() and True or False

def is_valid_number(value):
    return value and re.sub(r'[\s\-\+]+', '', value).isdigit() and True or False

def is_valid_text(value, mode=None):
    if not mode:
        return True
    elif mode == DATA_TYPE_TEXT:
        return True
    elif mode == DATA_TYPE_TEXT_A:
        return not re.sub(r'[\w\/\\\,\;]+', '', value) and True or False
    elif mode == DATA_TYPE_TEXT_N:
        return not re.sub(r'[\d]+', '', value) and True or False
    elif mode == DATA_TYPE_TEXT_NS:
        return not re.sub(r'[\d\s\/\\\,\;]+', '', value) and True or False
    elif mode == DATA_TYPE_TEXT_AN:
        return not re.sub(r'[\d\w]+', '', value) and True or False
    elif mode == DATA_TYPE_TEXT_AS:
        return not re.sub(r'[\w\s]+', '', value) and True or False
    elif mode == DATA_TYPE_TEXT_ANS:
        return not re.sub(r'[\d\w\s\/\\\.\,\;\&\-\+\'\"]+', '', value) and True or False
    elif mode == DATA_TYPE_TEXT_ANC:
        return not re.sub(r'[\d\w\s\/\\\,\;]+', '', value) and True or False
    else:
        return False

def is_valid_size(value, size):
    min = size[0]
    max = len(size) > 1 and size[1] or min
    l = len(value)
    return l >= min and (not max or l <= max) and True or False

def is_empty(value):
    return not (value and re.sub(r'\s', '', value)) and True or False

def checkTagParameters(index, key, field, value):
    """
        Проверить параметры тега контента файла.
        
        Аргументы:
            index  -- Int, порядковый номер поля
            key    -- String, имя поля
            field  -- Tuple, дескриптор поля <filetypes>.fieldset item
            value  -- String, значение поля

        Возврат:
            String, OK или код ошибки <app.errors>.
    """
    code = None

    number, name, field_type, data_type, perso_type, encoding, size, is_obligatory, comment = field

    if not number:
        pass
    elif not is_obligatory and is_empty(value):
        code = CHECKER_OK
    elif is_obligatory and is_empty(value):
        code = ERROR_CHECKER_IS_EMPTY
    elif data_type in (DATA_TYPE_INT, DATA_TYPE_INTEGER) and not is_valid_integer(value):
        code = ERROR_CHECKER_BAD_INTEGER
    elif data_type == DATA_TYPE_NUMBER and not is_valid_number(value):
        code = ERROR_CHECKER_BAD_NUMBER
    elif data_type in DATA_TYPE_VALID_TEXT and not is_valid_text(value, data_type):
        code = ERROR_CHECKER_BAD_TEXT
    elif size and isIterable(size) and not is_valid_size(value, size):
        code = ERROR_CHECKER_BAD_SIZE
    else:
        code = CHECKER_OK

    return code

def is_valid_pan16(value):
    return value and not re.sub(DATA_PERSO_TYPE_PAN16, '', value) and True or False

def is_valid_pan19(value):
    return value and not re.sub(DATA_PERSO_TYPE_PAN19, '', value) and True or False

def is_valid_panwide16(value):
    return value and not re.sub(DATA_PERSO_TYPE_PANWIDE16, '', value) and True or False

def is_valid_panwide19(value):
    return value and not re.sub(DATA_PERSO_TYPE_PANWIDE19, '', value) and True or False

def is_valid_expiredate(value):
    return value and not re.sub(DATA_PERSO_TYPE_EXPIREDATE, '', value) and True or False

def is_valid_bin(value):
    return value and not re.sub(DATA_PERSO_TYPE_BIN, '', value) and True or False

def is_valid_embossname(value):
    return value and not re.sub(DATA_PERSO_TYPE_EMBOSSNAME, '', value) and True or False

def is_valid_regexp(value, regexp):
    return value and not re.sub(regexp, '', value) and True or False

def is_valid_iterable(value, allowed_values):
    """
        Checks iterable: List, Tuple, String
    """
    return value and value in allowed_values and True or False

def checkTagData(index, key, field, value):
    """
        Проверить значение тега контента файла.
        
        Аргументы:
            index  -- Int, порядковый номер поля
            key    -- String, имя поля
            field  -- Tuple, дескриптор поля <filetypes>.fieldset item
            value  -- String, значение поля

        Возврат:
            String, OK или код ошибки <app.errors>.
    """
    code = None

    number, name, field_type, data_type, perso_type, encoding, size, is_obligatory, comment = field

    if not number:
        pass
    elif (isIterable(perso_type) or (isinstance(perso_type, str) and ':' in perso_type)) and \
        not is_valid_iterable(value, perso_type):
        code = ERROR_CHECKER_INVALID_VALUE
    elif perso_type == DATA_PERSO_TYPE_PAN16 and not is_valid_pan16(value):
        code = ERROR_CHECKER_BAD_PAN16
    elif perso_type == DATA_PERSO_TYPE_PAN19 and not is_valid_pan19(value):
        code = ERROR_CHECKER_BAD_PAN19
    elif perso_type == DATA_PERSO_TYPE_PANWIDE16 and not is_valid_panwide16(value):
        code = ERROR_CHECKER_BAD_PANWIDE16
    elif perso_type == DATA_PERSO_TYPE_PANWIDE19 and not is_valid_panwide19(value):
        code = ERROR_CHECKER_BAD_PANWIDE19
    elif perso_type in (DATA_PERSO_TYPE_EXPIREDATE, DATA_PERSO_TYPE_DATE_MMYY) and not is_valid_expiredate(value):
        code = ERROR_CHECKER_BAD_EXPIREDATE
    elif perso_type == DATA_PERSO_TYPE_BIN and not is_valid_bin(value):
        code = ERROR_CHECKER_BAD_BIN
    elif perso_type == DATA_PERSO_TYPE_EMBOSSNAME and not is_valid_embossname(value):
        code = ERROR_CHECKER_BAD_EMBOSSNAME
    else:
        code = CHECKER_OK

    return code
