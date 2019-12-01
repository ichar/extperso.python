# -*- coding: cp1251 -*-

# --------------------- #
#   otkrytie.generate   #
# --------------------- #

__all__ = ['tags', 'custom']

import re

from config import (
     IsDebug, IsDeepDebug, IsDisableOutput, IsPrintExceptions,
     default_print_encoding, default_unicode, default_encoding, default_iso, cr,
     LOCAL_EASY_DATESTAMP, UTC_FULL_TIMESTAMP, UTC_EASY_TIMESTAMP, DATE_STAMP,
     print_to, print_exception
)

from app.core import ProcessException
from app.types.statuses import *
from app.srvlib import *
from app.utils import getDate, getToday

from ..defaults import *
from ..filetypes.otkrytie import *
from ..xmllib import *

# ------------------------- #

"""
    Модуль Генерации данных заказа.

    = ORDER.GENERATE =

    Назначение модуля:
        1. Верификация и формирование данных входящих файлов.
        2. Генерация дополнительных данных.
"""

# ------------------------- #

def tags():
    """
        Теги записей для генерации контента
    """
    return ('FileBody_Record',)

# ========================= #

def custom(n, node, logger, saveback, **kw):
    """
        Генерация контента
    """
    if node.tag != 'FileBody_Record':
        return

    order = kw.get('order')

    # ------------
    # Данные файла
    # ------------

    # Наименование банка-клиента
    client = FILETYPE_OTKRYTIE_V1['bankname'][1]
    # Имя файла
    orderfile = order.filename
    # Порядковый номер карты в файле
    recno = getTag(node, 'FileRecNo')
    # PAN
    PAN = re.sub(r'\s', '', getTag(node, 'PAN'))
    # BIN
    BIN = PAN[:6]
    # Имя держателя карты
    cardholder_name = getTag(node, 'CardholderName')
    # Тип пластика, данные MSDP, префикс дизайна, тип чипа, наименование пластика
    plastic_type, service_code, pvki, design_prefix, pay_system, plastic_name = ['']*6
    # ФИО владельца карты
    FIO = FMT_ParseFIO(node, '')
    # Срок действия
    expire_date = getTag(node, 'ExpireDate')
    # Имя держателя для печати на карте
    track1_cardholder_name = getTag(node, 'CardholderName')
    # Код филиала доставки (!!!)
    ID_VSP = ''
    # PAN Sequence Number
    PSN = ''
    # БЕЗ печати ПИН-конвертов
    pCode = 0

    # -------------------------------
    # Генерация дополнительных данных
    # -------------------------------

    # Имя Банка-клиента
    updateTag(node, 'CLIENTID', client)
    # Имя входящего файла
    updateTag(node, 'ORDER_FILE', orderfile)
    # PAN
    updateTag(node, 'PAN', PAN)
    # BIN
    updateTag(node, 'BIN', BIN)

    # -------------------
    # Теги персонализации
    # -------------------

    # Тип пластика
    updateTag(node, 'PlasticType', plastic_type)
    # Тип чипа
    updateTag(node, 'PAY_SYSTEM', pay_system)
    # Чиповая персонализация
    setBooleanTag(node, 'DUMPBANK_FLAG', 1)
    # Печать ПИН-конвертов
    setBooleanTag(node, 'PCode', pCode)

    # ------------------
    # ПАРАМЕТРЫ ДОСТАВКИ
    # ------------------

    # Вид клиентской доставки
    card_type = ''
    updateTag(node, 'CardType', card_type)

    # ----------------------
    # Служебные/опциональные
    # ----------------------

    sort = '%s' % (recno)
    updateTag(node, 'Sort', sort)

    # -----------------
    # PIN RECORD OUTPUT
    # -----------------

    GEN_PIN_Record(node, [
        ('RECID', recno,),
        ('PAN', PAN,),
        ('LLine1', FIO.get('surname'),),
        ('LLine2', FIO.get('firstname'),),
        ('LLine3', FIO.get('lastname'),),
        ('LLine4', card_type,),
        ('LLine5', '',),
        ('LLine6', '',),
        ('LLine7', '',),
        ('LLine8', '',),
        ('RLine1', '%s  %s; %s' % (PAN[:6], PAN[-4:], ID_VSP),),
        ('RLine2', cardholder_name,),
        ('RLine3', '',),
        ('PinBlock', '',),
        ('ExpDate', expire_date,),
        ('Name', cardholder_name,),
        ('MagName', track1_cardholder_name,),
        ('SCode', service_code,),
        ('PVKNO', pvki,),
        ('PCode', pCode,),
    ], remove_empty=True)

    # -----------------
    # DTC RECORD OUTPUT
    # -----------------

    track1 = getTag(node, 'Track1')
    track2 = getTag(node, 'Track2')
    track3 = getTag(node, 'Track3')

    GEN_DTC_Record(node, [
        ('RECNO', recno,),
        ('CONVN', '%010d' % int(PAN[8:]),),
        ('BILN', FMT_BILN(getTag(node, 'BILN'), PAN=PAN),),
        ('ELN1', FMT_PanWide(PAN),),
        ('ELN2', FMT_ExpireDate(expire_date),),
        ('ELN3', cardholder_name,),
        ('ELN4', '',),
        ('ILN1', '',),
        ('ILN2', '',),
        ('ILN3', '',),
        ('ILN4', '',),
        ('EANN', '',),
        ('EAND', '',),
        ('T1', track1,),
        ('T2', track2,),
        ('T3', track3,),
        ('DUMPB', '',),
        ('DUMPE', getTag(node, 'DUMPE'),),
        ('DUMPA', '',),
    ])

    # -----------------
    # OTK RECORD OUTPUT
    # -----------------

    GEN_OTK_Record(node, [
        ('FileRecNo', recno,),
        ('PAN', PAN,),
        ('OTK_EMBNAME', cardholder_name,),
        ('OTK_Track1', track1,),
        ('OTK_Track2', track2,),
        ('OTK_Track3', track3,),
    ])

    # -----------------
    # INC RECORD OUTPUT
    # -----------------

    GEN_INC_Record(node, [
        ('FileRecNo', recno,),
        ('Client', client,),
        ('OrderFile', orderfile,),
        ('PAN', FMT_PanMask_6_4(PAN),),
        ('EMBNAME', cardholder_name,),
    ])

    updateTag(node, 'CARD_TYPE', card_type)
    updateTag(node, 'MPR_Barcode', '')
    updateTag(node, 'MPR_EncodingCategory', '0')
    updateTag(node, 'MPR_ExtHandler', '')
    updateTag(node, 'MPR_SectorMask', '0')
    updateTag(node, 'MPR_Track1', track1)
    updateTag(node, 'MPR_Track2', track2)
    updateTag(node, 'MPR_Track3', track3)

    logger('--> Generate Node: %s' % node.tag)

def checker(n, node, logger, saveback, **kw):
    if node.tag != 'FileBody_Record':
        return

    order = kw.get('order')
    recno = getTag(node, 'FileRecNo')

    changed = True

    if not changed:
        return

    logger('--> Changed %s Node: %s, recno: %s' % (order.filename, node.tag, recno), force=True)
