# -*- coding: cp1251 -*-

# ------------------ #
#   postbank.check   #
# ------------------ #

__all__ = ['accept', 'error', 'status_error_to', 'outgoing', 'check_parameters', 'check_data',]

import re

from config import (
    IsDebug, IsDeepDebug, IsDisableOutput, IsPrintExceptions,
    default_print_encoding, default_unicode, default_encoding, default_iso, cr,
    LOCAL_EASY_DATESTAMP, UTC_FULL_TIMESTAMP, DATE_STAMP,
    print_to, print_exception
)

from app.core import ProcessException, CustomException
from app.types.datatypes import *
from app.types.errors import *
from app.checker import is_empty, is_valid_text, is_valid_size
from app.srvlib import *
from app.utils import normpath

from ..defaults import *
from ..filetypes.postbank import *
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
        5. Дополнительные операции, в т.ч. подготовка индивидуального дизайна (контроль INDIGO)
"""

# ------------------------- #

encoding = DEFAULT_OUTGOING_TYPE.get('encoding')
eol = DEFAULT_EOL

# ========================= #

ToBank = 'ToBank'

def accept(filename):
    return normpath('%s/%s/%s/%s.ACCEPT' % (DEFAULT_INCOMING_ROOT, FILETYPE_FOLDER, ToBank, filename))

def error(filename):
    return normpath('%s/%s/%s/%s.ERROR' % (DEFAULT_INCOMING_ROOT, FILETYPE_FOLDER, ToBank, filename))

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

def status_error_to(order):
    """
        Статус контроля (error)
    """
    return order._status_error or STATUS_REJECTED_ERROR

def check_parameters(n, node, logger, saveback, **kw):
    """
        Контроль параметров
    """
    if node.tag != 'FileBody_Record':
        return

    checker = kw.get('checker')

    res, errors = _check(node, logger, saveback, checker=checker)

    order = kw.get('order')

    # Порядковый номер карты в файле
    recno = getTag(node, 'FileRecNo')
    # ID карты Банка
    id = getTag(node, LOCAL_ID_TAG)
    # Тип файла
    filetype = order.filetype
    # Файл индивидуального дизайна PictureID
    picture_id = getTag(node, 'ImageName')
    
    if local_WithIndigo(order, filetype=filetype):
        incoming = local_filetypes.get(filetype) or FILETYPE_POSTBANK_ID

        if is_empty(picture_id):
            _add_error(n, node, id, ('ImageName', ERROR_CHECKER_IS_EMPTY,), errors, saveback)
            return HANDLER_CODE_ERROR
        if not is_valid_text(picture_id, DATA_TYPE_TEXT_ANC):
            _add_error(n, node, id, ('ImageName', ERROR_CHECKER_BAD_TEXT,), errors, saveback)
            return HANDLER_CODE_ERROR
        if not is_valid_size(picture_id, incoming['fieldset']['ImageName'][6]):
            _add_error(n, node, id, ('ImageName', ERROR_CHECKER_BAD_SIZE,), errors, saveback)
            return HANDLER_CODE_ERROR

def check_data(n, node, logger, saveback, **kw):
    """
        Контроль данных входящего персофайла
    """
    if node.tag != 'FileBody_Record':
        return

    checker = kw.get('checker')

    res, errors = _check(node, logger, saveback, checker=checker)

    # ------------------------------
    # Сопоставить запись справочника
    # ------------------------------

    order = kw.get('order')
    connect = kw.get('connect')

    # Порядковый номер карты в файле
    recno = getTag(node, 'FileRecNo')
    # ID карты Банка
    id = getTag(node, LOCAL_ID_TAG)
    # Код филиала доставки карт
    code = getTag(node, 'BRANCHDELIVERY')
    # Код сопоставления записи справочника
    TID = None

    if not (connect and callable(connect)):
        raise Exception('Uncallable connect!')

    # Именные/Неименные
    is_named_type = local_IsNamedType(node)
    # Карты с адресной доставкой
    is_addr_delivery = local_IsAddrDelivery(node)
    # Карта лояльности
    is_with_loyalty = local_WithLoyalty(order)

    # ------------------
    # Данные справочника
    # ------------------

    is_error = False

    if 'ref' not in saveback:
        saveback['ref'] = {}

    if is_addr_delivery:
        pass
    elif code in saveback['ref']:
        TID, cursor = saveback['ref'][code]
    else:
        mode = 'DeliveryRef'

        cursor, is_error = connect(SQL[mode]['check'], (code,), encode_columns=REF_ENCODE_COLUMNS, with_result=True)
        TID = SRV_GetValue(cursor, is_error) or None

        is_error = not TID and True or False

        if is_error:
            _add_error(n, node, id, ('UNMATCHED', '00',), errors, saveback)
            return HANDLER_CODE_ERROR

        if code not in saveback['ref']:
            saveback['ref'][code] = (TID, cursor,)

    # --------------
    # Особые условия
    # --------------

    # PAN
    PAN = re.sub(r'\s', '', getTag(node, 'PAN'))
    pan_masked = FMT_PanMask_6_4(PAN)
    # Код дизайна пластика
    product_design = getTag(node, 'ProductDesign')
    # Имя заказа
    orderfile = order.ordername
    # Канал отсылки на адрес клиента
    delivery_canal_code = getTag(node, 'DeliveryCanalCode')

    if product_design[:6] != PAN[:6]:
        _add_error(n, node, id, ('ProductDesign', 'Not matched with PAN',), errors, saveback)

    if product_design not in orderfile:
        _add_error(n, node, id, ('ProductDesign', 'Not matched with filename',), errors, saveback)

    if is_addr_delivery:
        for key in ('CardholderFIO', 'CardholderAddress'):
            if not getTag(node, key):
                _add_error(n, node, id, (key, ERROR_CHECKER_IS_EMPTY,), errors, saveback)

    if is_named_type and is_addr_delivery:
        key = 'CardholderAddress'
        address = local_ParseAddress(node, key)
        if not address or len(address) != 9 or not address['index']:
            _add_error(n, node, id, (key, ERROR_CHECKER_INVALID_VALUE,), errors, saveback)

    # -------------------------------
    # Генерация дополнительных данных
    # -------------------------------

    if TID is not None:
        # Код филиала отправки карт
        updateTag(node, 'BRANCH_SEND_TO', SRV_GetValue(cursor, is_error, REF_INDEX['BranchSendTo']))
        # Код сопоставления справочника
        updateTag(node, 'DeliveryRefID', str(TID))

    if errors:
        return HANDLER_CODE_ERROR

    # ------------------------------------
    # Выделить свободные номера лояльности
    # ------------------------------------

    # Имя входящего файла
    filename = order.filename

    if is_with_loyalty:
        mode = 'LoyaltyNumbers'

        TID = None
        loyalty_number = None

        is_error = False
        cursor = None

        try:
            cursor, is_error = connect(SQL[mode]['get'], None, with_result=True)
            TID = SRV_GetValue(cursor, is_error) or None

            is_error = not TID and True or False

            if is_error:
                errors.append(('NO FREE LOAYLTY NUMBER', 'B1',))
                saveback['errors'].append((n, id, errors))
                FMT_XMLErrorRecord(node, errors)
                #
                # Статус ожидания файла-реестра лояльности (нет свободных номеров)
                #
                order._status_error = STATUS_ON_SUSPENDED
                msg = 'Loaylty Register: %s No free loaylty numbers, PAN:%s recno:%s' % (filename, pan_masked, recno)
                raise CustomException(msg, recipients=ERROR_RECIPIENTS)

            loyalty_number, ean = cursor[0][1:]

            # ID реестра лояльности
            updateTag(node, 'LoyaltyTID', TID)
            # Номер лояльности
            updateTag(node, 'LoyaltyNumber', loyalty_number)
            # EAN
            updateTag(node, 'EAN', ean)

            cursor, is_error = connect(SQL[mode]['register'], (PAN, TID))

        except ProcessException as ex:
            raise

        except:
            msg = 'Loaylty Register: %s Unexpected error, TID:%s, LoyaltyNumber:%s, PAN:%s recno:%s' % (
                filename, TID, loyalty_number, pan_masked, recno)
            print_to(None, 'ERROR:'+repr(cursor))
            raise ProcessException(msg)

    return HANDLER_CODE_UNDEFINED

def outgoing(logger, saveback, is_error, **kw):
    """
        Файл-квитанция о приема персофайла
    """
    if is_error and not kw.get('saveback_errors'):
        return

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
