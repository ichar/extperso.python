# -*- coding: cp1251 -*-

# ------------------- #
#   postbank.loader   #
# ------------------- #

__all__ = [
    'validator', 
    'incoming', 'incoming_custom', 
    'incoming_individual_design', 'incoming_individual_design_custom', 
    'incoming_nspk_individual_design', 'incoming_nspk_individual_design_custom', 
    'incoming_X5', 'incoming_X5_custom', 
    'reference', 'reference_custom', 'reference_outgoing', 
    'loyalty', 'loyalty_custom', 'loyalty_outgoing' 
    ]

import re
from copy import deepcopy

from config import (
    IsDebug, IsDeepDebug, IsDisableOutput, IsPrintExceptions,
    default_print_encoding, default_unicode, default_encoding, default_iso, cr,
    LOCAL_EASY_DATESTAMP, UTC_FULL_TIMESTAMP, DATE_STAMP,
    print_to, print_exception
)

from app.modules.loader import BaseIncomingLoader, BaseReferenceLoader
from app.types.errors import *
from app.srvlib import *
from app.utils import normpath

from ..defaults import *
from ..filetypes.postbank import *
from ..xmllib import *

# ------------------------- #

"""
    Модуль Загрузки входящих данных.

    = LOADER =

    Назначение модуля:
        1. Загрузка входящего файла заказа.
        2. Загрузка входящего файла справочника.
        3. Загрузка входящего файла-реестра лояльности.
"""

# ------------------------- #

incoming = deepcopy(FILETYPE_POSTBANK_V1)

incoming.update({
    'class'     : BaseIncomingLoader,
    'location'  : '%s/%s/%s' % (DEFAULT_INCOMING_ROOT, FILETYPE_FOLDER, DEFAULT_FROMBANK),
    'mask'      : r'VBEX_.*_(40599((?:11[2|3|4|5])|(?:21[6|7|8|9])|(?:220))).*\.txt',
    'encoding'  : DEFAULT_INCOMING_TYPE['encoding'],
})

incoming_individual_design = deepcopy(FILETYPE_POSTBANK_ID)

incoming_individual_design.update({
    'class'     : BaseIncomingLoader,
    'location'  : '%s/%s/%s' % (DEFAULT_INCOMING_ROOT, FILETYPE_FOLDER, DEFAULT_FROMBANK),
    'mask'      : r'VBEX_.*_(40599((?:[1|2]11)|(?:122)|(?:222))).*\.txt',
    'encoding'  : DEFAULT_INCOMING_TYPE['encoding'],
})

incoming_nspk_individual_design = deepcopy(FILETYPE_POSTBANK_IDM)

incoming_nspk_individual_design.update({
    'class'     : BaseIncomingLoader,
    'location'  : '%s/%s/%s' % (DEFAULT_INCOMING_ROOT, FILETYPE_FOLDER, DEFAULT_FROMBANK),
    'mask'      : r'VBEX_.*_22007701[4].*\.txt',
    'encoding'  : DEFAULT_INCOMING_TYPE['encoding'],
})

incoming_X5 = deepcopy(FILETYPE_POSTBANK_X5)

incoming_X5.update({
    'class'     : BaseIncomingLoader,
    'location'  : '%s/%s/%s' % (DEFAULT_INCOMING_ROOT, FILETYPE_FOLDER, DEFAULT_FROMBANK),
    'mask'      : r'VBEX_.*_22007704[4|5|A].*\.txt',
    'encoding'  : DEFAULT_INCOMING_TYPE['encoding'],
})

reference = deepcopy(FILETYPE_POSTBANK_REFERENCE)

reference.update({
    'class'     : BaseReferenceLoader,
    'location'  : '%s/%s/%s' % (DEFAULT_REFERENCE_ROOT, FILETYPE_FOLDER, DEFAULT_FROMBANK),
    'mask'      : r'VBEX_AUX_\d{8}\.CSV',
    'encoding'  : DEFAULT_REFERENCE_TYPE['encoding'],
})

loyalty = deepcopy(FILETYPE_POSTBANK_LOYALTY)

loyalty.update({
    'class'     : BaseReferenceLoader,
    'location'  : '%s/%s/%s' % (DEFAULT_LOYALTY_ROOT, FILETYPE_FOLDER, DEFAULT_FROMBANK),
    'mask'      : r'LOYALTYNUMBERS_\d{8}_\d{2}\.CSV',
    'encoding'  : DEFAULT_LOYALTY_TYPE['encoding'],
})

encoding = DEFAULT_INCOMING_TYPE.get('encoding')

eol = DEFAULT_EOL

REF_INFO = 'REF_INFO'
LTY_INFO = 'LTY_INFO'

# ========================= #

def accept(filename):
    return normpath('%s/%s/%s/%s.ACCEPT' % (DEFAULT_INCOMING_ROOT, FILETYPE_FOLDER, DEFAULT_TOBANK, filename))

def error(filename):
    return normpath('%s/%s/%s/%s.ERROR' % (DEFAULT_INCOMING_ROOT, FILETYPE_FOLDER, DEFAULT_TOBANK, filename))

# ========================= #

def validator(value):
    return value != '-' and re.sub(r'""', '"', value) or ''

def incoming_custom(n, node, logger, saveback, **kw):
    """
        Загрузчик записи входящего файла заказа
    """
    pass

def incoming_individual_design_custom(n, node, logger, saveback, **kw):
    """
        Загрузчик записи входящего файла заказа, индивидуальный дизайн
    """
    pass

def incoming_nspk_individual_design_custom(n, node, logger, saveback, **kw):
    """
        Загрузчик записи входящего файла заказа, индивидуальный дизайн, приложение "МИР"
    """
    pass

def incoming_X5_custom(n, node, logger, saveback, **kw):
    """
        Загрузчик записи входящего файла заказа, проект "Пятерочка"
    """
    pass

def loyalty_custom(n, data, logger, saveback, **kw):
    """
        Загрузчик записи входящего файла-реестра с номерами лояльности
    """
    fieldset = kw.get('fieldset')
    keys = kw.get('keys')
    connect = kw.get('connect')
    checker = kw.get('checker')

    mode = 'LoyaltyNumbers'
    code = data.get('LoyaltyNumber')

    # ---------------
    # Контроль данных
    # ---------------

    if LTY_INFO not in saveback:
        saveback[LTY_INFO] = {'updated' : 0, 'added' : 0, 'errors' : 0}

    # Ошибка в структуре данных
    res, errors = FMT_UnpackChecker(checker)
    
    if errors:
        logger('>>> Запись: %s, номер лояльности: %s, %s %s' % (n, code, res, errors), is_error=True)
        saveback[LTY_INFO]['errors'] += 1

    # --------------------------------
    # Проверить данные на дублирование
    # --------------------------------

    if not (connect and callable(connect)):
        return HANDLER_CODE_ERROR

    for i, key in enumerate(keys): #('LoyaltyNumber', 'EAN')
        value = data.get(key)
        check = 'check%s' % (i + 1)
        error_code = 'D%s' % (i + 1)

        cursor, is_error = connect(SQL[mode][check], (value,), with_result=True)
        TID = SRV_GetValue(cursor, is_error) or None

        if TID:
            res, error = '%s exists' % key, ('EXISTS:%s' % key, error_code,)
            logger('>>> Запись: %s, %s существует: %s, %s %s' % (n, key, value, res, error), is_error=True)
            saveback[LTY_INFO]['errors'] += 1
            errors.append(error)

    if 'EAN' in keys:
        # Первые 3 цифры EAN
        ean3 = data.get('EAN')[0:3]

        # не должны быть в указанном диапазоне
        if ean3 >= '960' and ean3 <= '999':
            res, error = 'EAN3 is invalid', ('EAN3', 'R2',)
            saveback['errors'].append((n, code, errors))
            logger('>>> Запись: %s, некорректный EAN: %s, %s %s' % (n, code, res, error), is_error=True)
            saveback[LTY_INFO]['errors'] += 1
            errors.append(error)

    if errors:
        saveback['errors'].append((n, code, errors))
        return HANDLER_CODE_ERROR

    # ---------------------------
    # Добавить запись справочника
    # ---------------------------

    values = [data.get(key) for key in keys]

    # Дата обновления
    values.append(getDate(getToday(), UTC_FULL_TIMESTAMP))

    cursor, is_error = connect(SQL[mode]['add'], tuple(values), raise_error=True)

    if is_error:
        logger('--> Ошибка записи реестра лояльности: %s, TID=%s' % (repr(data), TID), True, is_error=is_error)
        saveback[LTY_INFO]['errors'] += 1
    else:
        saveback[LTY_INFO]['added'] += 1

    return not is_error and HANDLER_CODE_UNDEFINED or HANDLER_CODE_ERROR

def loyalty_outgoing(logger, saveback, is_error, **kw):
    """
        Файл-квитанция о приеме файла-реестра лояльности
    """
    if not makeOutgoing(logger, saveback, is_error, 
        accept=accept, 
        error=error, 
        get_error_code=local_GetErrorCode, 
        encoding=encoding, 
        eol=eol, 
        no_ext=True, 
        with_full_reject=False, 
        **kw
        ):
        return

    if saveback and LTY_INFO in saveback:
        logger('Файл: %s, info: %s, errors: %s' % (
            kw.get('filename'), repr(saveback[LTY_INFO]), saveback['errors']), 
            True)

def reference_custom(n, data, logger, saveback, **kw):
    """
        Загрузчик записи входящего файла справочника
    """
    fieldset = kw.get('fieldset')
    keys = kw.get('keys')
    connect = kw.get('connect')
    checker = kw.get('checker')

    mode = 'DeliveryRef'
    code = data.get('BranchDelivery')

    # ---------------
    # Контроль данных
    # ---------------

    if REF_INFO not in saveback:
        saveback[REF_INFO] = {'updated' : 0, 'added' : 0, 'errors' : 0}

    # Ошибка в структуре данных
    res, errors = FMT_UnpackChecker(checker)
    
    if errors:
        saveback['errors'].append((n, code, errors))
        logger('>>> Запись: %s, код филиала: %s, %s %s' % (n, code, res, errors), is_error=True)
        saveback[REF_INFO]['errors'] += 1
        return HANDLER_CODE_ERROR

    # Тарифный пояс
    zone = data.get('Zone')
    if not zone and (
        data.get('NonamedPostType') == 'ПОЧТА 1 КЛАСС' or data.get('NamedPostType') == 'ПОЧТА 1 КЛАСС'):
        res, errors = 'Zone is empty', [('Zone', ERROR_CHECKER_IS_EMPTY,),]
        saveback['errors'].append((n, code, errors))
        logger('>>> Запись: %s, код филиала: %s, %s %s' % (n, code, res, errors), is_error=True)
        saveback[REF_INFO]['errors'] += 1
        return HANDLER_CODE_ERROR

    # ------------------------------------
    # Добавить/Обновить запись справочника
    # ------------------------------------

    if not (connect and callable(connect)):
        return HANDLER_CODE_ERROR

    cursor, is_error = connect(SQL[mode]['check'], (code,), with_result=True)
    TID = SRV_GetValue(cursor, is_error) or None

    values = [data.get(key) for key in keys]

    # Дата обновления
    values.append(getDate(getToday(), UTC_FULL_TIMESTAMP))

    if TID:
        values.append(int(TID))
        cursor, is_error = connect(SQL[mode]['update'], tuple(values), raise_error=True)
    else:
        cursor, is_error = connect(SQL[mode]['add'], tuple(values), raise_error=True)

    if is_error:
        logger('--> Ошибка записи справочника: %s, TID=%s' % (repr(data), TID), True, is_error=is_error)
        saveback[REF_INFO]['errors'] += 1
    else:
        #logger('--> %s справочника[TID=%s]' % (TID and 'Обновление' or 'Добавление', TID), True)

        if TID:
            saveback[REF_INFO]['updated'] += 1
        else:
            saveback[REF_INFO]['added'] += 1

    return not is_error and HANDLER_CODE_UNDEFINED or HANDLER_CODE_ERROR

def reference_outgoing(logger, saveback, is_error, **kw):
    """
        Файл-квитанция о приеме файла-справочника
    """
    if not makeOutgoing(logger, saveback, is_error, 
        accept=accept, 
        error=error, 
        get_error_code=local_GetErrorCode, 
        encoding=encoding, 
        eol=eol, 
        no_ext=True, 
        with_full_reject=True, 
        **kw
        ):
        return

    if saveback and REF_INFO in saveback:
        logger('Файл: %s, info: %s, errors: %s' % (
            kw.get('filename'), repr(saveback[REF_INFO]), saveback['errors']), 
            True)

def outgoing(logger, saveback, is_error, **kw):
    """
        Файл-квитанция о приема персофайла (REJECT ONLY)
    """
    if not is_error:
        return

    makeOutgoing(logger, saveback, is_error, 
        accept=accept, 
        error=error, 
        get_error_code=local_GetErrorCode, 
        encoding=encoding, 
        eol=eol, 
        no_ext=False, 
        with_full_reject=True, 
        **kw
        )
