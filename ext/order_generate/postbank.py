# -*- coding: cp1251 -*-

# --------------------- #
#   postbank.generate   #
# --------------------- #

__all__ = [
    'status_to', 'status_error', 'status_postonline_to', 'tags', 'custom_step1', 'custom_step2', 'custom_postonline', 
    'change_delivery_date'
    ]

import re

from config import (
     IsDebug, IsDeepDebug, IsTrace, IsDisableOutput, IsPrintExceptions, IsCheckF103Sent,
     default_print_encoding, default_unicode, default_encoding, default_iso, cr,
     LOCAL_EASY_DATESTAMP, UTC_FULL_TIMESTAMP, UTC_EASY_TIMESTAMP, DATE_STAMP,
     print_to, print_exception,
     email_address_list
)

from app.core import ProcessException, CustomException, Order
from app.types.constants import READY_DATE, TOTAL, DISABLED, EMPTY_NODE
from app.types.statuses import *
from app.srvlib import *
from app.utils import getDate, getToday, Capitalize, isIterable, sortedDict, sjoin, getDefaultValueByKey

from ..defaults import *
from ..filetypes.postbank import *
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

IsErrorPostOnlineFixed = False

LOCAL_ORDERFILES = 'orderfiles'
LOCAL_BATCHES_TAG = 'PostOnlineBatches'
LOCAL_ORDERS_TAG = 'PostOnlineOrders'
LOCAL_CHANGE_DELIVERY_DATE = 'change_delivery_date'

# ------------------------- #

def status_to(order):
    """
        Статус генерации (to)
    """
    return local_IsFastFile(order) and STATUS_FILTER_VERIFIED or STATUS_ON_ORDER_WAIT

def status_error(order):
    """
        Статус ошибки (to)
    """
    return order.status_error or STATUS_REJECTED_INVALID

def status_postonline_to(order):
    """
        Статус регистрации почтовых отправлений (to)
    """
    # Тип файла
    filetype = order.filetype
    is_with_indigo = local_WithIndigo(order, filetype=filetype)
    #return ('$P' in order.filename or is_with_indigo) and STATUS_POST_ONLINE_STARTED or STATUS_POST_ONLINE_FINISHED
    return STATUS_ON_DELIVERY_DONE

def tags():
    """
        Теги записей для генерации контента
    """
    return ('FileInfo', 'FileBody_Record', 'ProcessInfo',)

# ========================= #

def _make_batch_groups(logger, **kw):
    """
        Привязка отгрузочного адреса (пакета отгрузки в филиал) к индексу партии.
        Связано с ограничением предельного размера партии 500 карт.
    """
    groups = {}

    cursor = local_PackageNumberGroups(logger, **kw)

    if not cursor:
        return groups

    index, total = 1, 0

    for record in cursor:
        package_number, package_type, cards = record

        x = total + cards
        is_new = False

        if x < DEFAULT_PACKAGE_LIMIT:
            total += cards
        elif x > DEFAULT_PACKAGE_LIMIT:
            index += 1
            total = cards
        else:
            is_new = True

        groups[package_number] = index

        if is_new:
            index += 1
            total = 0

    return groups

def _check_package_size(node, order, **kw):
    """
        Параметры, связанные с количеством карт в файле
    """
    package_type = kw.get('package_type')
    delivery_company = kw.get('delivery_company')
    is_named_type = kw.get('is_named_type')

    step = kw.get('step')

    # Максимальное (предельное) кол-во карт/пломб в упаковках
    stamp_size, package_size = local_GetPackageSize(node, order)

    # Материалы к упаковке, вложения
    if package_type == 'C1':
        updateTag(node, 'CASE_PACKAGE', 'C1-B%s-%s' % (delivery_company, str(package_size)))

    elif package_type == 'C2':
        updateTag(node, 'CASE_PACKAGE', 'C2-B%s' % delivery_company)

    elif package_type == 'C3':
        updateTag(node, 'CASE_PACKAGE', '')

    else:
        raise ProcessException('Undefined package_type [custom_step%s]!' % step)

    updateTag(node, 'StampSize', stamp_size)
    updateTag(node, 'PackageSize', package_size)

def custom_step1(n, node, logger, saveback, **kw):
    """
        Генерация контента (FAST-файлы+индивидуальный дизайн и общие поля, шаг 1)
    """
    order = kw.get('order')
    connect = kw.get('connect')

    # Наименование банка-клиента
    client = CLIENT_NAME[1]
    # Имя входящего файла
    filename = order.filename
    # Тип файла
    filetype = order.filetype

    if node.tag == 'FileInfo':
        print_log_space('FileID:%s = custom_step1' % order.id)
        return

    if node.tag == 'ProcessInfo':
        saveback[READY_DATE] = local_GetDeliveryDate(
            size=n-1, 
            is_fastfile=local_IsFastFile(order), 
            is_with_indigo=local_WithIndigo(order, filetype=filetype),
            is_with_loyalty=local_WithLoyalty(order),
            delivery_companies=saveback['DeliveryCompany'],
            package_types=saveback['PackageType'],
            filename=filename,
            )
        return

    if node.tag != 'FileBody_Record':
        return

    if not (connect and callable(connect)):
        raise ProcessException('Uncallable connect [step1]!')

    # -----------------
    # Данные персофайла
    # -----------------

    # Порядковый номер карты в файле
    recno = getTag(node, 'FileRecNo')
    # PAN
    PAN = re.sub(r'\s', '', getTag(node, 'PAN'))
    pan_masked = FMT_PanMask_6_4(PAN)
    # BIN
    BIN = PAN[:6]
    # Имя держателя карты
    cardholder_name = getTag(node, 'CardholderName')
    # Срок действия
    expire_date = getTag(node, 'ExpireDate')
    # Имя держателя для печати на карте
    track1_cardholder_name = getTag(node, 'Track1CardholderName')
    # Код дизайна пластика
    product_design = getTag(node, 'ProductDesign')
    # Тип пластика, данные MSDP, данные SDC, префикс дизайна, тип чипа, наименование пластика
    plastic_type, service_code, pvki, design_prefix, pay_system, plastic_name = local_GetPlasticInfo(product_design, filetype=filetype)
    # ФИО владельца карты
    FIO = FMT_ParseFIO(node, 'CardholderFIO')
    # Код элемента структуры
    branch_delivery = getTag(node, 'BRANCHDELIVERY')
    # Филиал доставки
    branch_send_to = getTag(node, 'BRANCH_SEND_TO')
    # Код филиала доставки (!!!)
    ID_VSP = branch_send_to
    # PAN Sequence Number
    PSN = getTag(node, 'PSN')
    # БЕЗ печати ПИН-конвертов
    pCode = 0

    # Код сопоставления справочника
    TID = int(getTag(node, 'DeliveryRefID') or '0') or None

    # Именные/Неименные
    is_named_type = local_IsNamedType(node)
    # Признак "с картхолдером"
    with_cardholder = local_WithCardHolder(node)
    # Карты с адресной доставкой
    is_addr_delivery = local_IsAddrDelivery(node)

    # Срочный файл
    is_fastfile = local_IsFastFile(order)
    # Индивидуальный дизайн
    is_with_indigo = local_WithIndigo(order, filetype=filetype)
    # Печать ШПИ
    is_with_barcode = local_WithBarcode(product_design, filetype=filetype)
    # Карта лояльности
    is_with_loyalty = local_WithLoyalty(order)
    # Конверт ОВПО
    is_case_cover = local_CaseCover(node)

    # ------------------------
    # ВХОДНОЙ КОНТРОЛЬ ДИЗАЙНА
    # ------------------------

    local_CheckDesignIsInvalid(product_design, is_named_type=is_named_type)

    # ---------------------------------
    # Данные справочника филиалов Банка
    # ---------------------------------

    mode = 'DeliveryRef'

    is_error = False

    if 'ref' not in saveback:
        saveback['ref'] = {}

    if is_addr_delivery:
        cursor = None
    elif TID in saveback['ref']:
        cursor = saveback['ref'][TID]
    else:
        cursor, is_error = connect(SQL[mode]['select'], (TID,), encode_columns=REF_ENCODE_COLUMNS, with_result=True)

        if is_error:
            raise ProcessException('SQL Error[select], mode:%s' % mode)

        if TID not in saveback['ref']:
            saveback['ref'][TID] = cursor

    # -------------------------------
    # Генерация дополнительных данных
    # -------------------------------

    # Имя Банка-клиента
    updateTag(node, 'CLIENTID', client)
    # Имя входящего файла
    updateTag(node, 'ORDER_FILE', filename)
    # PAN
    updateTag(node, 'PAN', PAN)
    # BIN
    updateTag(node, 'BIN', BIN)

    # Change ExpireDate from YY/MM to MMYY
    if LOCAL_IS_CHANGE_EXPIREDATE:
        local_SetExpireDate(node)

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
    # Тип печати на лицевой стороне
    updateTag(node, 'PrintTypeFront', local_PlasticFrontPrintType(product_design, filetype=filetype))
    # Тип печати на оборотной стороне
    updateTag(node, 'PrintTypeBack', local_PlasticBackPrintType(product_design, filetype=filetype))

    # ---------------
    # Штрих-код карты
    # ---------------

    # Код лояльности
    loyalty_number = getTag(node, 'LoyaltyNumber')
    # EAN
    ean = getTag(node, 'EAN')

    card_barcode = card_barcode_control = None

    if is_with_barcode:
        if is_with_loyalty:
            card_barcode_control = ean
            card_barcode = card_barcode_control[:-1]

            design_prefix = card_barcode[:3]
        else:
            card_barcode = '%3s%9s' % (design_prefix, PAN[6:15])
            card_barcode_control = EAN_13Digit(card_barcode)

            # Номер лояльности
            updateTag(node, 'LoyaltyNumber', '')

        if len(card_barcode.strip()) != 12:
            raise ProcessException('Invalid card barcode:[%s]' % card_barcode)

    # ШК без контрольной цифры (12 цифр)
    updateTag(node, 'EANN', card_barcode)
    # ШК с конрольной цифрой (13 цифр)
    updateTag(node, 'EAND', card_barcode_control)
    # Префикс для ШК EAN-13 карты
    updateTag(node, 'DesignPrefix', design_prefix)

    # ------------------
    # ПАРАМЕТРЫ ДОСТАВКИ
    # ------------------

    # Вид клиентской доставки (именные/неименные, с картхолдером, с адресной доставкой):{I|N}{C}{A}
    card_type = '%s%s%s' % (
        is_named_type and 'I' or 'N',
        with_cardholder and 'C' or '',
        is_addr_delivery and 'A' or '',
    )
    updateTag(node, 'CardType', card_type)

    # С адресной доставкой
    setBooleanTag(node, 'IsAddrDelivery', is_addr_delivery)

    # Именная/Неименная доставка
    p = is_named_type and 'Named' or 'Nonamed'

    # Группа карт
    card_group = local_GetCardGroup(card_type, filetype=filetype)
    updateTag(node, 'CardGroup', card_group)

    if TID is not None and cursor is not None:
        # Данные справочника
        company_name = SRV_GetValue(cursor, is_error, REF_INDEX['CompanyName'])
        delivery_type = SRV_GetValue(cursor, is_error, REF_INDEX[p+'PostType'])
        delivery_zone = SRV_GetValue(cursor, is_error, REF_INDEX['Zone'])
        receiver_name = SRV_GetValue(cursor, is_error, REF_INDEX['Receiver'])
        receiver_address = SRV_GetValue(cursor, is_error, REF_INDEX['Address'])
        receiver_contact = SRV_GetValue(cursor, is_error, REF_INDEX[p+'Contact'])
        receiver_phone = SRV_GetValue(cursor, is_error, REF_INDEX[p+'Phone'])
    else:
        # Данные входящего файла заказа
        company_name = ''
        delivery_type = ''
        delivery_zone = ''
        receiver_name = getTag(node, 'CardholderFIO')
        receiver_address = FMT_ParseAddress(getTag(node, 'CardholderAddress'))
        receiver_contact = ''
        receiver_phone = ''

    # -----------------------------------
    # Обязательные параметры по умолчанию
    # -----------------------------------

    if not delivery_type:
        delivery_type = DEFAULT_DELIVERY_TYPE

    # Наименование подразделения
    updateTag(node, 'CompanyName', company_name)
    # Способ доставки
    updateTag(node, 'DeliveryType', delivery_type)
    # Зона/Тариф на доставку
    updateTag(node, 'DeliveryZone', delivery_zone)
    # Получатель
    updateTag(node, 'ReceiverName', receiver_name)
    # Адрес
    updateTag(node, 'ReceiverAddress', receiver_address)
    # Контакт получателя
    updateTag(node, 'ReceiverContact', receiver_contact)
    # Телефон
    updateTag(node, 'ReceiverPhone', receiver_phone)

    # ------------------
    # ПАРАМЕТРЫ УПАКОВКИ
    # ------------------

    # Вид упаковки
    package_type = is_addr_delivery and 'C3' or with_cardholder and 'C2' or 'C1'
    """
    if is_named_type:
        package_type = is_addr_delivery and (is_with_indigo and 'C3' or 'C2') or 'C1'
    else:
        package_type = with_cardholder and 'C2' or 'C1'
    """
    updateTag(node, 'PackageType', package_type)

    # Условное обозначение транспортной компании
    delivery_company = local_GetDeliveryCompany(delivery_type)
    updateTag(node, 'DeliveryCompany', delivery_company)

    # Дата отгрузки
    delivery_date = local_SetDeliveryDate(node, order, saveback)

    # Номер пломбы, индекс первой карты, номер транспортной упаковки, ШПИ
    stamp_code, stamp_index, package_code, post_code = '', '', '', ''
    if is_fastfile or is_with_indigo:
        stamp_code, stamp_index, package_code, post_code = local_UpdateStampCode(node, order, connect, logger, saveback, filetype=filetype)

    # Максимальное (предельное) кол-во карт/пломб в упаковках
    _check_package_size(node, order, package_type=package_type, delivery_company=delivery_company, is_named_type=is_named_type, step=1)

    # Материалы к упаковке, вложения
    if package_type == 'C1':
        updateTag(node, 'CASE_BOX', is_named_type and not is_addr_delivery and 'C1-A2' or 'C1-A1')
        updateTag(node, 'CASE_COVER', '')
        updateTag(node, 'CASE_ENCLOSURE', local_WithEnclosure(product_design, is_named_type=is_named_type))
        updateTag(node, 'CASE_ENVELOPE', '')
        updateTag(node, 'CASE_LEAFLET', '')

    elif package_type == 'C2':
        updateTag(node, 'CASE_BOX', is_addr_delivery and 'C2-LETTER' or 'C2-BOX')
        updateTag(node, 'CASE_COVER', is_case_cover and 'C2-OVPO' or '')
        updateTag(node, 'CASE_ENCLOSURE', '')
        updateTag(node, 'CASE_ENVELOPE', local_CaseEnvelope(product_design, filetype=filetype) or is_named_type and 'C2-COVER2' or 'C2-COVER1')
        updateTag(node, 'CASE_LEAFLET', local_CaseLeaflet(product_design, filetype=filetype) or is_named_type and 'C2-I' or 'C2-N')

    elif package_type == 'C3':
        updateTag(node, 'CASE_BOX', 'C3-LETTER')
        updateTag(node, 'CASE_COVER', '')
        updateTag(node, 'CASE_ENCLOSURE', '')
        updateTag(node, 'CASE_ENVELOPE', 'C3-COVER2')
        updateTag(node, 'CASE_LEAFLET', 'C3-I')

    # ----------------------
    # Служебные/опциональные
    # ----------------------

    # Код филиала доставки карт
    updateTag(node, 'ID_VSP', ID_VSP)
    # Параметры MSDP
    updateTag(node, 'ServiceCode', service_code)
    # Track3
    updateTag(node, 'Track3', '')

    is_indent = 0

    if local_IsCyberLab(order):
        output = local_UpdateCyberLabNumber(node, order, connect, logger, saveback, PAN=PAN)
    
        # 4-я строка на обороте
        updateTag(node, 'Organization', output)
        updateTag(node, 'LoyaltyNumber', output.split(' ')[1])
        is_indent = 1

    # Индент-печать
    setBooleanTag(node, 'IsIndent', is_indent)

    # Сортировка в партиях
    if LOCAL_IS_PLASTIC_BATCHSORT:
        sort = '%s:%s:%s:%s:%s' % (plastic_type, card_type, delivery_type, branch_send_to, recno)
    else:
        sort = '%s:%s:%s:%s' % (card_group, delivery_company, branch_delivery, recno)
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
    ])

    # -----------------
    # INC RECORD OUTPUT
    # -----------------

    if TID:
        receiver_address = FMT_ParseDefaultAddress(receiver_address)

    GEN_INC_Record(node, [
        ('FileRecNo', recno,),
        ('Client', client,),
        ('OrderFile', filename,),
        ('PAN', FMT_PanMask_6_4(PAN),),
        ('EMBNAME', cardholder_name,),
        ('PHONE', getTag(node, 'ReceiverPhone'),),
        ('BADDR', FMT_CleanAddress(receiver_address),),
        ('BRANCHDELIVERY', branch_delivery,),
        ('BRANCH_SEND_TO', branch_send_to,),
        ('BRANCH', company_name,),

        ('Card_Type', card_type,),
        ('PlasticType', '%s %s' % (product_design, plastic_name),),
        ('PackageType', package_type,),
        ('PackageCode', package_code,),
        ('StampCode', stamp_code,),
        ('StampIndex', stamp_index,),
        ('PostCode', post_code,),

        ('DeliveryCompany', delivery_company,),
        ('DeliveryType', delivery_type,),
        ('DeliveryZone', getTag(node, 'DeliveryZone'),),
        ('DeliveryDate', delivery_date,),
        ('ReceiverName', receiver_name,),
        ('ReceiverContact', getTag(node, 'ReceiverContact'),),
    ])

    # -----------------------------------
    # DLV RECORD OUTPUT (DELIVERY REPORT)
    # -----------------------------------

    GEN_DLV_Record(node, [
        stamp_code,
        branch_delivery,
        PAN,
        product_design,
        delivery_date,
        local_IsDeliveryWithBarcode(node, delivery_company=delivery_company) and getTag(node, 'PostBarcode') or '',
        card_barcode or '',
    ], ';')

    # ------------------
    # AREP RECORD OUTPUT
    # ------------------

    address = local_ParseAddress(node, 'CardholderAddress')
    root = local_GetAREPRecordName(order, filetype, product_design, is_addr_delivery=is_addr_delivery)

    if package_type in ('C2',) and (not is_named_type or is_with_loyalty):
        #
        # Листовки: Неименная карта лояльности КЕЙС-2
        #
        GEN_AREP_Record(node, [
            ('PANMSK', FMT_PanMask_4_4(PAN),),
            ('PostBarcode', local_GetPostBarcode(post_code),),
            ('PostCode', post_code,),
            ('EAND', card_barcode_control,),
            ('CardBarcode', local_GetPostBarcode(card_barcode_control, 'EAN13'),),
            ('B1', card_barcode_control[0],),
        ], root=root)

    elif package_type in ('C2','C3') and is_named_type and is_addr_delivery:
        #
        # Листовки: Именная с адресной доставкой КЕЙС-2/3
        #
        addrs = FMT_Limitstrlist([address.get(x) or '' 
            for x in ('district', 'city', 'town', 'street', 'house', 'building', 'flat')],
                limit=40, comma=', ', max_items=4)

        GEN_AREP_Record(node, [
            ('PANMSK', FMT_PanMask_6_4(PAN),),
            ('PostBarcode', local_GetPostBarcode(post_code),),
            ('PostCode', post_code,),
            ('EAND', card_barcode_control,),
            ('Salutation', ('%s %s' % (Capitalize(FIO.get('firstname')), Capitalize(FIO.get('lastname')))).strip() + '!',),
            ('ADDR1', ('%s %s %s %s' % (FIO.get('surname'), FIO.get('firstname'), FIO.get('lastname'), FIO['other'])).strip(),),
            ('ADDR2', addrs[0],),
            ('ADDR3', addrs[1],),
            ('ADDR4', addrs[2],),
            ('ADDR5', addrs[3],),
            ('ADDR6', address['region'],),
            ('ADDR7', address['index'],),
        ], root=root)

    else:
        #
        # Листовки: Неименная КЕЙС-2 и прочие
        #
        GEN_AREP_Record(node, [
            ('PANMSK', FMT_PanMask_6_4(PAN),),
            ('PostBarcode', package_type == 'C2' and card_barcode_control or '',),
            ('PostCode', '',),
            ('EAND', card_barcode_control,),
            ('CardBarcode', '',),
            ('B1', '',),
        ], root=root)

    # -----------------------------------------
    # Зафиксировать выделенный номер лояльности
    # -----------------------------------------

    if is_with_loyalty:
        mode = 'LoyaltyNumbers'

        file_id = order.id
        TID = getTag(node, 'LoyaltyTID')

        cursor, is_error = connect(SQL[mode]['fix'], (file_id, recno, TID), with_commit=False)

        if is_error:
            msg = 'Loaylty Fix: Unexpected error, TID:%s, LoyaltyNumber:%s, PAN:%s recno:%s' % (
                TID, loyalty_number, pan_masked, recno)
            print_to(None, 'ERROR:'+repr(cursor))
            raise ProcessException(msg)

    logger('--> Generate Step1 Node: %s' % node.tag)

def custom_step2(n, node, logger, saveback, **kw):
    """
        Генерация контента (единый файл дня, шаг 2)
    """
    order = kw.get('order')
    connect = kw.get('connect')
    phase = kw.get('phase')

    saveback[EMPTY_NODE] = False

    # Имя входящего файла
    filename = order.filename

    #
    # Установить дату отгрузки в зависимости от суммарного объема персофайлов
    #
    if phase == 1:
        ready_date = saveback and saveback.get(READY_DATE)
        disabled = saveback and saveback.get(DISABLED) or 0

        if disabled:
            logger('order_generate[custom_step2]: %s total disabled[%s]' % (filename, disabled), force=True)

        if ready_date:
            date = getDate(getDate(ready_date, UTC_EASY_TIMESTAMP, is_date=True), LOCAL_DATESTAMP)
            if date != saveback.get(LOCAL_DELIVERY_DATE):
                params = {'date' : date}
                change_delivery_date(n-disabled-2, node, logger, saveback, order=order, params=params, force=False)
            else:
                return -1
        return
    #
    # Рассчитать суммарный объем персофайлов в потоке и дату отгрузки
    #
    if phase == 0:
        if node.tag == 'FileInfo':
            print_log_space('FileID:%s = custom_step2' % order.id)

            if not DISABLED in saveback:
                saveback[DISABLED] = 0

        if node.tag == 'ProcessInfo':
            engine = kw.get('engine')
            size = 0
            disabled = saveback.get(DISABLED) or 0
            if engine is not None:
                orderfiles = saveback.get(LOCAL_ORDERFILES) or []
                for orderfile in orderfiles:
                    o = Order(orderfile)
                    o.get_original(engine)
                    size += o.fqty
            if disabled:
                size -= disabled
            saveback[READY_DATE] = local_GetDeliveryDate(size=size or n-2)
            return

    if node.tag == 'FileInfo':
        saveback[LOCAL_ORDERFILES] = []
        return

    if node.tag != 'FileBody_Record':
        return

    if not (connect and callable(connect)):
        raise ProcessException('Uncallable connect [step2]!')

    # Имя входящего персофайла
    orderfile = getTag(node, 'ORDER_FILE')

    if IsDeepDebug and IsTrace:
        print_to(None, 'Step2:%s' % orderfile)

    # Сформировать общий список входящих персофайлов потока
    if orderfile not in saveback[LOCAL_ORDERFILES]:
        saveback[LOCAL_ORDERFILES].append(orderfile)

    # Номер записи
    recno = getTag(node, 'FileRecNo')
    # Тип файла
    filetype = order.filetype
    # Код дизайна пластика
    product_design = getTag(node, 'ProductDesign')
    # Тип пластика
    plastic_type = local_GetPlasticInfo(product_design, key='product', filetype=filetype)
    # Способ доставки
    delivery_type = getTag(node, 'DeliveryType')
    # Условное обозначение транспортной компании
    delivery_company = getTag(node, 'DeliveryCompany') or local_GetDeliveryCompany(delivery_type)
    # Код элемента структуры
    branch_delivery = getTag(node, 'BRANCHDELIVERY')
    # Филиал доставки
    branch_send_to = getTag(node, 'BRANCH_SEND_TO')
    # Вид упаковки
    package_type = getTag(node, 'PackageType')
    # Именные/Неименные
    is_named_type = local_IsNamedType(node)
    # Карты с адресной доставкой
    is_addr_delivery = local_IsAddrDelivery(node)
    # Печать ШПИ
    is_with_barcode = local_WithBarcode(product_design, filetype=filetype)
    # Карта лояльности
    is_with_loyalty = local_WithLoyalty(order)
    # Группа карт
    card_group = getTag(node, 'CardGroup')

    # ------------------------
    # ВХОДНОЙ КОНТРОЛЬ ДИЗАЙНА
    # ------------------------

    local_CheckDesignIsInvalid(product_design, is_named_type=is_named_type)

    # ------------------
    # БЛОКИРОВКА ДИЗАЙНА
    # ------------------

    if local_IsPlasticDisabled(product_design):
        saveback[EMPTY_NODE] = True
        logger('order_generate[custom_step2]: %s design is disabled[%s] ID:%s, recno:[%s]' % (
            filename, product_design, getTag(node, LOCAL_ID_TAG), recno), 
            is_warning=True)
        saveback[DISABLED] += 1
        return

    # -------------------------------
    # Генерация дополнительных данных
    # -------------------------------

    # Максимальное (предельное) кол-во карт/пломб в упаковках
    _check_package_size(node, order, package_type=package_type, delivery_company=delivery_company, is_named_type=is_named_type, step=2)

    # Дата доставки/отгрузки
    delivery_date = local_SetDeliveryDate(node, order, saveback)

    # Номер пломбы, индекс первой карты, номер транспортной упаковки, ШПИ
    stamp_code, stamp_index, package_code, post_code = local_UpdateStampCode(node, order, connect, logger, saveback, filetype=filetype)

    # Транспортный ШПИ
    updateTag(node, 'PostBarcode', local_GetPostBarcode(post_code))

    # Сортировка в партиях
    if LOCAL_IS_PACKAGE_BATCHSORT:
        sort = '%s:%s:%s' % (package_code, stamp_code, recno)
    else:
        sort = '%s:%s:%s:%s:%s' % (delivery_type, branch_delivery, card_group, product_design, recno)
    updateTag(node, 'Sort', sort)

    # -----------------
    # PIN RECORD UPDATE
    # -----------------

    GEN_PIN_Record(node, [
        ('RECID', recno,),
    ])

    # -----------------
    # INC RECORD UPDATE
    # -----------------

    GEN_INC_Record(node, [
        ('FileRecNo', recno,),
        ('DeliveryDate', delivery_date,),
        ('PackageCode', package_code,),
        ('StampCode', stamp_code,),
        ('StampIndex', stamp_index,),
        ('PostCode', post_code,),
    ])

    # -----------------
    # DLV RECORD UPDATE
    # -----------------

    GEN_DLV_Record(node, [
        stamp_code,
        None,
        None,
        None,
        delivery_date,
    ], ';')

    # ------------------
    # AREP RECORD UPDATE
    # ------------------

    if package_type in ('C2','C3'):
        root = local_GetAREPRecordName(order, filetype, product_design, is_addr_delivery=is_addr_delivery)
        #
        # Листовки: КЕЙС-2/3
        #
        GEN_AREP_Record(node, [
            ('PostBarcode', local_GetPostBarcode(post_code),),
            ('PostCode', post_code,),
        ], root=root)

    logger('--> Generate Step2 Node: %s' % node.tag)

def custom_step3(n, node, logger, saveback, **kw):
    """
        Генерация индекса партии BatchIndex
    """
    if node.tag == 'FileInfo':
        saveback['groups'] = _make_batch_groups(logger, **kw)
        return

    # Имя входящего персофайла
    orderfile = getTag(node, 'ORDER_FILE')

    groups = saveback.get('groups')

    if IsDeepDebug and IsTrace:
        print_to(None, 'Step3:%s groups:%s' % (orderfile, groups))

    if node.tag != 'FileBody_Record' or not groups:
        return
    
    package_code = getINCRecordValue(node, 'PackageCode')
    batch_index = '%03d' % (package_code and groups.get(int(package_code[-5:])) or 0)

    updateTag(node, 'BatchIndex', batch_index)

    logger('--> Generate Step3 Node: %s' % node.tag)

def _get_batch_params(order, service):
    addr_to = service is not None and service('pochta_mail_to') or email_address_list.get('russianpost')
    unload_to = service is not None and service('postbank_unload_to')
    send_date = getDate(order.ready_date, format=DATE_STAMP)
    return addr_to, unload_to, send_date

def custom_postonline(n, node, logger, saveback, **kw):
    """
        ПОЧТА РОССИИ ОНЛАЙН (РЕГИСТРАЦИЯ ОТПРАВЛЕНИЙ).
        
        Двухфазная (двупроходная) процедура регистрации отправлений.
            phase : 0 -- подготовка данных и регистрация (packages)
                    1 -- запись данных в тегах

        Параметры отправления:
            PostOrderID -- ID отправления
            PostBarcode -- код ШПИ
            PostRate    -- стоимость отправления (цена)
    """
    order = kw.get('order')
    service = kw.get('service')
    phase = kw.get('phase')

    # Имя файла
    filename = order.filename
    # Тип файла
    filetype = order.filetype

    recno = None

    if phase == 0:
        if node.tag == 'FileInfo':
            print_log_space('FileID:%s = custom_postonline' % order.id)

            # Почтовые отправления
            saveback['packages'] = sortedDict()
            # Номера партий
            saveback['names'] = {}
            # Код пакета для группировки партий
            saveback['code'] = None
            return

    packages = saveback['packages']

    if phase == 1:
        if node.tag in ('FileBody_Record',):
            recno = getTag(node, 'FileRecNo')
            package_code = getTag(node, 'PackageCode')
            package = packages.get(package_code)

            if not package:
                return
    
            # Код дизайна пластика
            product_design = getTag(node, 'ProductDesign')

            ids, props, attrs, data = package
            card_type, case_box, case_enclosure, package_code, package_type, package_size, is_named_type, is_addr_delivery = props
            order_id, post_code, post_rate = data

            # ID заказа на отправку ПОЧТА РОССИИ
            updateTag(node, 'PostOrderID', order_id)
            # Транспортный ШПИ
            updateTag(node, 'PostBarcode', post_code)
            # Стоимость услуги
            updateTag(node, 'PostRate', post_rate)

            # -----------------
            # INC RECORD UPDATE
            # -----------------

            GEN_INC_Record(node, [
                ('PostCode', post_code,),
            ])

            # ------------------
            # AREP RECORD UPDATE
            # ------------------

            if package_type in ('C2','C3'):
                root = local_GetAREPRecordName(order, filetype, product_design, is_addr_delivery=is_addr_delivery)
                #
                # Листовки: КЕЙС-2/3
                #
                GEN_AREP_Record(node, [
                    ('PostBarcode', local_GetPostBarcode(post_code, 'I25'),),
                    ('PostCode', post_code,),
                ], root=root)

            if recno in package[0]:
                package[0].remove(recno)

            if len(package[0]) == 0:
                del saveback['packages'][package_code]

        elif node.tag in ('ProcessInfo',):
            if not packages:
                logger('Finished PostOnline successfully: %s, phase[%s]' % (filename, phase), force=True)

        return

    if node.tag in ('FileBody_Record',):
        # Транспортная компания
        delivery_company = getTag(node, 'DeliveryCompany')
        if not local_IsDeliveryWithPostOnline(node, delivery_company=delivery_company):
            return

        # Дизайн продукта
        product_design = getTag(node, 'ProductDesign')

        # ------------------
        # БЛОКИРОВКА ДИЗАЙНА
        # ------------------

        if local_IsPlasticDisabled(product_design, filetype=filetype):
            return

        # Регистрировать только новые(пустые) отправления
        if LOCAL_CHECK_POSTONLINE_FREE:
            if getTag(node, 'PostBarcode'):
                return

        # Номер записи
        recno = getTag(node, 'FileRecNo')
        # Тип карт
        card_type = getTag(node, 'CardType')
        # Упаковка для пластиковых карт (как тип отправления в ОПС)
        case_box = getTag(node, 'CASE_BOX')
        # Вложение
        case_enclosure = getTag(node, 'CASE_ENCLOSURE')
        # Номер транспортной упаковки
        package_code = getTag(node, 'PackageCode')
        # Вид упаковки
        package_type = getTag(node, 'PackageType')
        # Максимальное кол-во пломб|карт в транспортной упаковке
        package_size = int(getTag(node, 'PackageSize') or 0)
        # Именные/Неименные
        is_named_type = local_IsNamedType(node)
        # Карты с адресной доставкой
        is_addr_delivery = local_IsAddrDelivery(node)

    elif packages and len(packages.keys()) > 0:

        package_code = packages.keys()[-1]
        package = packages[package_code]
        
        ids, props, attrs, data = package
        card_type, case_box, case_enclosure, package_code, package_type, package_size, is_named_type, is_addr_delivery = props

        recno = 0
    else:
        return

    code = package_code

    if node.tag in ('FileBody_Record', 'ProcessInfo',):
        if package_code not in packages:
            packages[package_code] = [
                [], 
                (card_type, case_box, case_enclosure, package_code, package_type, package_size, is_named_type, is_addr_delivery,), 
                {
                    'address'  : getTag(node, 'ReceiverAddress'),
                    'receiver' : getTag(node, 'ReceiverName'),
                    'contact'  : getTag(node, 'ReceiverContact'),
                    'phone'    : getTag(node, 'ReceiverPhone'),
                    'number'   : '%s:%s:%s' % (getTag(node, 'BRANCHDELIVERY'), package_code, order.id),
                    'comment'  : getTag(node, 'ORDER_FILE'),

                    'delivery_canal_code' : getTag(node, 'DeliveryCanalCode'),
                    'delivery_company' : delivery_company,
                },
                None,
            ]

        if saveback['code'] and package_code != saveback['code'] or recno == 0:
            package_code = saveback['code']
            package = packages[package_code]

            ids, props, attrs, data = package
            card_type, case_box, case_enclosure, package_code, package_type, package_size, is_named_type, is_addr_delivery = props

            branch_delivery = attrs.get('number').split(':')[0]

            is_ems = attrs.get('delivery_company') == 'E' and True or False

            if package_type == 'C1':
                attrs['mass'] = local_GetPackageWeight(package_type, len(ids), enclosure=case_enclosure)
                attrs['category'] = 'ORDINARY'
                attrs['type'] = is_ems and 'EMS_TENDER' or 'PARCEL_CLASS_1'

            elif package_type in ('C2','C3') and is_named_type and is_addr_delivery:
                if len(ids) > 1 or package_size != 1:
                    raise ProcessException('PostOnline: Письмо с количеством карт больше 1:%s' % ids)

                attrs['mass'] = local_GetPackageWeight(case_box, 1)
                attrs['category'] = 'ORDERED'
                attrs['type'] = 'LETTER'

            elif package_type == 'C2':
                #if len(ids) > package_size:
                #    raise ProcessException('PostOnline: Коробка с количеством карт больше %s:%s' % (package_size, ids))
                attrs['mass'] = local_GetPackageWeight(case_box, len(ids))
                attrs['category'] = 'ORDINARY'
                attrs['type'] = is_ems and 'EMS_TENDER' or 'PARCEL_CLASS_1'

            if is_ems:
                attrs['transport-mode'] = 'EXPRESS'

            attrs['self_clean'] = True

            # ============================
            # Зарегистрировать отправление
            # ============================

            errors = []

            data = local_RegisterPostOnline(1, case_box, [package_code], errors=errors, **attrs)

            if not (data and isIterable(data) and len(data) == 3) or errors:
                msg = 'PostOnline: Unexpected error, data:%s, errors:%s, branch:%s, recno:%s' % ( 
                    data, repr(errors), branch_delivery, recno)
                print_to(None, 'ERROR:'+repr(package))

                if errors and IsErrorPostOnlineFixed:
                    logger('[%s] FixedError. %s' % ('custom_postonline', msg), is_error=True)
                    data = None
                else:
                    raise CustomException(msg)

            package[3] = data

            if data is not None:
                order_id, post_code, post_rate = data

                if IsDeepDebug:
                    logger('--> RegisterPostOnline: %s, attrs: %s, props: %s' % (repr(package[3]), attrs, props), force=True)

        package = packages[code]

    if node.tag in ('FileBody_Record',):
        package[0].append(recno)
        saveback['code'] = code

        if IsDeepDebug:
            logger('--> package: %s' % package[0], force=True)

        logger('--> Generate PostOnline Node: %s' % node.tag)

    if node.tag in ('ProcessInfo',) and len(packages) > 0:
        orders = {}

        for key in packages:
            ids, props, attrs, data = packages[key]
            
            if data is None:
                continue

            card_type, case_box, case_enclosure, package_code, package_type, package_size, is_named_type, is_addr_delivery = props
            order_id, post_code, post_rate = data

            if package_code != key:
                raise ProcessException('PostOnline: Package is not checked, key:%s-%s' % (package_code, key))

            if case_box not in orders:
                orders[case_box] = []

            orders[case_box].append(order_id)

        # ==========================
        # Создать партию на отправку
        # ==========================

        send_date = getDate(order.ready_date, format=LOCAL_EASY_DATESTAMP)

        for case_box in orders:
            errors = []

            names = local_RegisterPostOnline(2, case_box, orders[case_box], send_date=send_date, errors=errors)

            if not names or errors:
                raise ProcessException('PostOnline: Checkin is invalid, names:%s, errors:%s' % (names, errors))

            saveback['names'][case_box] = names

        # ===================
        # Выгрузить документы
        # ===================

        addr_to, unload_to, send_date = _get_batch_params(order, service)

        names = saveback['names']

        for case_box in orders:
            errors = []

            data = local_RegisterPostOnline(3, case_box, names[case_box], 
                addr_to=addr_to, 
                unload_to=unload_to, 
                filename=filename,
                send_date=send_date, 
                print_type=LOCAL_PRINT_TYPE,
                with_forms=LOCAL_POSTONLINE_WITH_FORMS,
                errors=errors,
                )

            if not data or len(data) != len(names[case_box]) or errors:
                raise ProcessException('PostOnline: Documents unload is failed, names:%s, errors:%s' % (data, errors))

        def _get_batch_key(x, values):
            return '%s:%s' % (x, sjoin(values, ','))

        orders = ','.join(["'%s':[%s]" % (_get_batch_key(x, names[x]), sjoin(orders[x], ',')) for x in names])

        updateTag(node, LOCAL_ORDERS_TAG, orders)

        batches = ';'.join([_get_batch_key(x, names[x]) for x in names])

        updateTag(node, LOCAL_BATCHES_TAG, batches)

        logger('PostOnline OK: %s, phase[%s], созданы почтовые отправления: %s' % (filename, phase, batches), force=True)

def custom_postonline_sender(n, node, logger, saveback, **kw):
    """
        Рассылка почтовых отправлений в ОПС (zip)
    """
    if node.tag != 'ProcessInfo' or not IsCheckF103Sent:
        return

    order = kw.get('order')
    service = kw.get('service')

    batches = getTag(node, LOCAL_BATCHES_TAG)

    if batches:
        print_log_space('FileID:%s = custom_postonline_sender' % order.id)

        filename = order.filename

        # ====================
        # Отправить Ф103 в ОПС
        # ====================

        addr_to, unload_to, send_date = _get_batch_params(order, service)

        for batch in batches.split(';'):
            case_box, orders = batch.split(':')
            names = orders.split(',')

            errors = []

            emails = local_RegisterPostOnline(4, case_box, names, 
                addr_to=addr_to, 
                unload_to=unload_to, 
                send_date=send_date, 
                client_title=CLIENT_NAME[2],
                filename=filename,
                errors=errors,
                )

            for msg in emails:
                logger('PostOnline Email[%s]: %s' % (filename, msg), force=True)
            if not emails:
                logger('PostOnline Email[%s]: unavailable %s!' % (filename, addr_to), is_warning=True)
                return

# ========================= #

def change_delivery_date(n, node, logger, saveback, **kw):
    """
        Перенос даты отгрузки
    """
    order = kw.get('order')
    service = kw.get('service')
    phase = kw.get('phase')

    recno = getTag(node, 'FileRecNo')
    force = True

    filename = order.filename

    if 'force' in kw:
        force = kw.get('force')

    params = kw.get('params')

    delivery_date = getDefaultValueByKey('date', params, None)

    if not delivery_date:
        return

    if phase == 0:
        if node.tag == 'FileInfo':
            print_log_space('FileID:%s = change_delivery_date' % order.id)

    if node.tag == 'ProcessInfo':
        batches = getTag(node, LOCAL_BATCHES_TAG).split(';')

        # --------------------------------------------------
        # Перерегистрация отправлений с новой датой отгрузки
        # --------------------------------------------------

        send_date = getDate(delivery_date, LOCAL_DATESTAMP, is_date=True)
        is_change_delivery_date = saveback.get(LOCAL_CHANGE_DELIVERY_DATE)

        if not phase and is_change_delivery_date:
            errors = {}

            if params.get('auto') and batches:
                addr_to, unload_to, ready_date = _get_batch_params(order, service)

                data, errors = local_ChangePostOnline(batches, send_date, 
                    addr_to=addr_to, 
                    no_email=not IsCheckF103Sent, 
                    no_break=False,
                    print_type=LOCAL_PRINT_TYPE,
                    with_forms=LOCAL_POSTONLINE_WITH_FORMS,
                    )

                if not data or len(data) != len(batches):
                    raise ProcessException('PostOnline: Documents unload is failed, ids:%s, errors:%s' % (data, errors))

                saveback['DATA'] = data
                saveback['ERRORS'] = errors

            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # Проверить - требуется ли изменение даты отгрузки для записи с заданным номером заказа
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            should_be_changed = []

            try:
                orders = eval('{%s}' % getTag(node, LOCAL_ORDERS_TAG))

                for batch in orders:
                    if not list(filter(lambda x: x != 'BATCH_NOT_CHANGED', errors.get(batch))):
                        should_be_changed += orders[batch] or []
            except:
                should_be_changed = None

            saveback['should_be_changed'] = should_be_changed

        if phase == 1:
            if is_change_delivery_date:
                if not checkTagExists(node, LOCAL_BATCHES_TAG) or not saveback.get('DATA'):
                    raise ProcessException('PostOnline: Batches data is invalid!, batches:%s' % batches)

                logger('PostOnline, OK: %s, выполнена перерегистрация отправлений: %s, ids:%s, errors:%s' % (
                    filename, batches, saveback['DATA'], saveback['ERRORS']), force=True)

        if phase == 1 or phase is None:
            saveback[READY_DATE] = '%s 18:00' % getDate(send_date, LOCAL_EASY_DATESTAMP)
            logger('Changed delivery date for: %s to %s' % (order.filename, saveback[READY_DATE]), force=force)

        return

    if not phase:
        if node.tag == 'FileBody_Record' and not saveback.get(LOCAL_CHANGE_DELIVERY_DATE):
            if local_IsDeliveryWithDate(node):
                saveback[LOCAL_CHANGE_DELIVERY_DATE] = True

    if phase == 0 or node.tag != 'FileBody_Record':
        return

    post_order_id = getTag(node, 'PostOrderID')

    if post_order_id and post_order_id.isdigit():
        should_be_changed = saveback.get('should_be_changed')

        if should_be_changed is not None and int(post_order_id) not in should_be_changed:
            return

    updateTag(node, 'DeliveryDate', delivery_date)

    GEN_INC_Record(node, [
        ('DeliveryDate', delivery_date,),
    ])

    GEN_DLV_Record(node, [
        None,
        None,
        None,
        None,
        delivery_date,
    ], ';')

    logger('--> Changed %s Node: %s, recno: %s' % (order.filename, node.tag, recno), force=force)

def change_delivery_address(n, node, logger, saveback, **kw):
    """
        Смена адреса филиала доставки
    """
    if node.tag == 'FileInfo':
        saveback['count'] = 0
        return

    if node.tag == 'ProcessInfo':
        saveback['stdout'] = 'Changed %s records' % saveback['count']
        return

    order = kw.get('order')
    connect = kw.get('connect')

    address, recno, branch = '', None, ''

    params = kw.get('params')

    if params and isinstance(params, dict):
        address = params.get('address')
        recno = params.get('recno')
        branch = params.get('branch')

    if not address:
        return

    # Номер записи файла
    file_recno = getTag(node, 'FileRecNo')
    # Код элемента структуры
    branch_delivery = getTag(node, 'BRANCHDELIVERY')

    if branch and branch_delivery != branch or recno is not None and int(recno) != int(file_recno):
        return

    updateTag(node, 'ReceiverAddress', address)

    GEN_INC_Record(node, [
        ('BADDR', FMT_CleanAddress(address),),
    ])

    saveback['count'] += 1

    logger('Changed %s Node: %s, address:%s, recno: %s' % (order.filename, node.tag, address, file_recno), force=True)

def unregister(n, node, logger, saveback, **kw):
    order = kw.get('order')
    connect = kw.get('connect')

    recno = getTag(node, 'FileRecNo')

    # -----------------------------------------------------------------
    # Полная переупаковка файла с перерегистрацией упаковок ПочтаРоссии
    # -----------------------------------------------------------------

    delivery_date = '15.01.2021'

    changed = False

    if node.tag == 'ProcessInfo':
        if LOCAL_CHECK_POSTONLINE_FREE:
            updateTag(node, LOCAL_BATCHES_TAG, 'C1-A2:4790') # !!!
        else:
            removeTag(node, LOCAL_BATCHES_TAG)
        logger('--> Unregister %s Node: %s, recno: %s' % (order.filename, node.tag, recno), force=True)
        return

    if node.tag != 'FileBody_Record':
        saveback[READY_DATE] = '%s 18:00' % getDate(getDate(delivery_date, format='%d.%m.%Y', is_date=True), LOCAL_EASY_DATESTAMP)
        return

    # Регистрировать только заданный тип карты
    if LOCAL_CHECK_POSTONLINE_FREE:
        if getTag(node, 'CardType') != 'ICA':
            return

    # Тип файла
    filetype = order.filetype

    recno = getTag(node, 'FileRecNo')

    p = getTag(node, 'PackageCode')
    s = getTag(node, 'StampCode')
    i = getTag(node, 'StampIndex')

    # Дата отгрузки
    updateTag(node, 'DeliveryDate', delivery_date)

    # Номер пломбы, индекс первой карты, номер транспортной упаковки, ШПИ
    stamp_code, stamp_index, package_code, post_code = local_UpdateStampCode(node, order, connect, logger, saveback, filetype=filetype)

    # Транспортный ШПИ
    updateTag(node, 'PostBarcode', local_GetPostBarcode(post_code))

    GEN_INC_Record(node, [
        ('DeliveryDate', delivery_date,),
        ('PackageCode', package_code,),
        ('StampCode', stamp_code,),
        ('StampIndex', stamp_index,),
        ('PostCode', post_code,),
    ])

    GEN_DLV_Record(node, [
        stamp_code,
        None,
        None,
        None,
        delivery_date,
    ], ';')

    # Удалить теги ОПС ПочтаРоссии
    removeTag(node, 'PostOrderID')
    removeTag(node, 'PostBarcode')
    removeTag(node, 'PostRate')

    # Удалить теги инкассации
    removeTag(node, 'INC_Date')
    removeTag(node, 'INC_Answer_DateTime')

    changed = True

    logger('--> recno:%s StampCode[%s:%s], StampIndex[%s:%s], PackageCode[%s:%s]' % (
        recno, s, stamp_code, i, stamp_index, p, package_code), force=True)

def checker(n, node, logger, saveback, **kw):
    #if node.tag != 'FileBody_Record':
    #    return

    order = kw.get('order')
    connect = kw.get('connect')

    recno = getTag(node, 'FileRecNo')

    changed = False

    # --------------------------------------------------------
    # Скорректировать теги регистрации отправлений ПочтаРоссии
    # --------------------------------------------------------

    if node.tag == 'ProcessInfo':
        if LOCAL_CHECK_POSTONLINE_FREE:
            updateTag(node, LOCAL_ORDERS_TAG, "'C3-LETTER:1260':[353004406],'C1-A2:4790':[348459066,348459093,348459116,348459220]")
            updateTag(node, LOCAL_BATCHES_TAG, 'C3-LETTER:1260;C1-A2:4790')
        else:
            return
    else:
        return

    """
    # -----------------------------------
    # Принудительно сменить дату отгрузки
    # -----------------------------------

    if node.tag == 'FileInfo':
        return

    delivery_date = '20.06.2020'

    if node.tag == 'ProcessInfo':
        saveback[READY_DATE] = '%s 18:00' % getDate(getDate(delivery_date, format='%d.%m.%Y', is_date=True), LOCAL_EASY_DATESTAMP)
        return

    updateTag(node, 'DeliveryDate', delivery_date)

    GEN_INC_Record(node, [
        ('DeliveryDate', delivery_date,),
    ])

    GEN_DLV_Record(node, [
        None,
        None,
        None,
        None,
        delivery_date,
    ], ';')
    """
    """
    updateTag(node, 'PAY_SYSTEM', 'KONA_2320_X5')
    """
    """
    # -----------------------
    # Исправить адрес филиала
    # -----------------------

    # Код элемента структуры
    branch_delivery = getTag(node, 'BRANCHDELIVERY')

    if branch_delivery != '507002552':
        return

    address = '664080,ОБЛ,ИРКУТСКАЯ,,,Г,ИРКУТСК,,,МКР ТОПКИНСКИЙ,44,,,,'

    updateTag(node, 'ReceiverAddress', address)

    GEN_INC_Record(node, [
        ('BADDR', FMT_CleanAddress(address),),
    ])
    """
    """
    # --------
    # Листовка
    # --------

    # Тип файла
    filetype = order.filetype
    # Код дизайна пластика
    product_design = getTag(node, 'ProductDesign')
    # Тип пластика, данные MSDP, префикс дизайна, тип чипа, наименование пластика
    plastic_type, service_code, pvki, design_prefix, pay_system, plastic_name = local_GetPlasticInfo(product_design, filetype=filetype)
    # Именные/Неименные
    is_named_type = local_IsNamedType(node)

    # Вид упаковки
    package_type = getTag(node, 'PackageType')

    # Вложения
    if is_named_type and product_design == '40599114' and package_type == 'C1':
        updateTag(node, 'CASE_ENCLOSURE', 'GREENWORLD')
    else:
        updateTag(node, 'CASE_ENCLOSURE', '')
    """
    """
    updateTag(node, 'ImageName', getTag(node, 'PictureID'))
    """
    """
    # -----------------------------
    # Перерегистрация номера пломбы
    # -----------------------------

    card_type = getTag(node, 'CardType')
    
    if card_type != 'N':
        return

    # Номер пломбы, индекс первой карты, номер транспортной упаковки, ШПИ
    stamp_code, stamp_index, package_code, post_code = local_UpdateStampCode(node, order, connect, logger, saveback, filetype=filetype)

    GEN_INC_Record(node, [
        ('PackageCode', package_code,),
        ('StampCode', stamp_code,),
        ('StampIndex', stamp_index,),
        ('PostCode', post_code,),
    ])

    GEN_DLV_Record(node, [
        stamp_code,
    ], ';')
    """
    """
    # ---------------------------------------------
    # Смена ШПИ ПочтаРоссии (переделка отправления)
    # ---------------------------------------------

    changed = False
    
    post_code = '10296128802603'

    updateTag(node, 'PostBarcode', post_code)
    updateTag(node, 'PostRate', 34)

    GEN_INC_Record(node, [
        ('PostCode', post_code,),
    ])
    """
    """
    card_type = getTag(node, 'CardType')
    card_group = local_GetCardGroup(card_type)
    
    updateTag(node, 'CardGroup', card_group)
    updateTag(node, 'Sort', str(card_group)+getTag(node, 'Sort'))
    """

    changed = True

    """
    if not getINCRecordValue(node, 'PostCode'):
        GEN_INC_Record(node, [
            ('PostCode', 'EH004057575RU',),
        ])
        changed = True
    """
    """
    expire_date = getTag(node, 'ExpireDate').split('/')
    if len(expire_date) == 2 and expire_date[1] > '24':
        new = '%s/24' % expire_date[0]
        updateTag(node, 'ExpireDate', new)
        GEN_PIN_Record(node, [
            ('ExpDate', new),
        ])
        
        changed = True
    """
    """
    record = getTag(node, 'DLV_Record')
    if record:
        values = record.split('|')
        if len(values) == 7:
            del values[6]
            updateTag(node, 'DLV_Record', '|'.join(values))
            changed = True
    """

    if not changed:
        return

    logger('--> Changed %s Node: %s, recno: %s' % (order.filename, node.tag, recno), force=True)

def check_process_info(n, node, logger, saveback, **kw):
    if node.tag != 'ProcessInfo':
        return

    order = kw.get('order')
    recno = getTag(node, 'FileRecNo')

    changed = False

    record = getTag(node, 'PostOnlineOrders')
    if record:
        updateTag(node, 'PostOnlineOrders', re.sub(r'[{}]', '', re.sub(r'(?:\'[\[\]])', '', record)))
        changed = True

    if not changed:
        return

    logger('--> Changed %s Node: %s, recno: %s' % (order.filename, node.tag, recno), force=True)

def dummy(n, node, logger, saveback, **kw):
    pass

def restart_perso(n, node, logger, saveback, **kw):
    if node.tag != 'FileBody_Record':
        return

    order = kw.get('order')

    recno = getTag(node, 'FileRecNo')

    removeTag(node, 'CARDS_Answer_DateTime')

    logger('--> Changed %s Node: %s, recno: %s' % (order.filename, node.tag, recno), force=True)

def restart_inc_cards(n, node, logger, saveback, **kw):
    if node.tag != 'FileBody_Record':
        return

    order = kw.get('order')

    recno = getTag(node, 'FileRecNo')

    removeTag(node, 'INC_Date')
    removeTag(node, 'INC_Answer_DateTime')

    logger('--> Changed %s Node: %s, recno: %s' % (order.filename, node.tag, recno), force=True)

def full_restart(n, node, logger, saveback, **kw):
    if node.tag != 'FileBody_Record':
        return

    order = kw.get('order')

    recno = getTag(node, 'FileRecNo')

    removeTag(node, 'ProcessSortID')
    #removeTag(node, 'PIN_Record')
    #removeTag(node, 'INC_Record')
    #removeTag(node, 'DLV_Record')
    #removeTag(node, 'AREP_Record')
    
    removeTag(node, 'BatchDefinitions')
    removeTag(node, 'GEN_CVV2')
    removeTag(node, 'GEN_Track1')
    removeTag(node, 'GEN_Track2')
    removeTag(node, 'GEN_PINBlock')
    removeTag(node, 'GEN_iCVV')
    removeTag(node, 'CHIP_Record')

    logger('--> Changed %s Node: %s, recno: %s' % (order.filename, node.tag, recno), force=True)
