# -*- coding: cp1251 -*-

# ---------------------- #
#   postbank filetypes   #
# ---------------------- #

__all__ = [
    'LOCAL_IS_CHANGE_EXPIREDATE', 'LOCAL_IS_PLASTIC_BATCHSORT', 'LOCAL_IS_PACKAGE_BATCHSORT', 'LOCAL_IS_REPORT_TODAY', 
    'LOCAL_CHECK_DELIVERY_ZONE', 'LOCAL_CHECK_POSTONLINE_FREE', 'LOCAL_POSTONLINE_WITH_FORMS', 'LOCAL_DATESTAMP', 'LOCAL_ID_TAG', 
    'LOCAL_EASY_TIMESTAMP', 'LOCAL_FILE_DELIVERY_SPLITTER', 'LOCAL_DELIVERY_DATE', 'LOCAL_PRINT_TYPE', 'LOCAL_DELIVERY_WITH_DATE', 'LOCAL_DELIVERY_WITH_BARCODE', 'LOCAL_DELIVERY_WITH_POSTONLINE', 'LOCAL_FILESTATUS_READY',
    'DEFAULT_DELIVERY_TYPE', 'DEFAULT_MERGE_INTERVAL', 'DEFAULT_EOL', 'DEFAULT_FILETYPE', 'FILETYPE_FOLDER', 
    'FILETYPE_POSTBANK_V1', 'FILETYPE_POSTBANK_ID', 'FILETYPE_POSTBANK_IDM', 'FILETYPE_POSTBANK_X5', 'FILETYPE_POSTBANK_CYBERLAB', 'FILETYPE_POSTBANK_LOYALTY', 'FILETYPE_POSTBANK_REFERENCE', 
    'CLIENT_NAME', 'SQL', 'REF_INDEX', 'REF_ENCODE_COLUMNS', 'ERROR_RECIPIENTS', 
    'local_GetPostBarcode', 'local_GetDeliveryCompany', 'local_GetErrorCode', 'local_GetPlasticInfo', 'local_GetPlasticSPrefix', 'local_GetDeliveryDate', 
    'local_GetPackageSize', 'local_GetPackageWeight', 'local_GetCardGroup', 'local_GetPackageType', 'local_GetMergePostfix', 'local_GetAREPRecordName', 
    'local_ParseAddress', 'local_SetDeliveryDate', 'local_SetExpireDate', 'local_GetIssueNumber',
    'local_UpdateStampCode', 'local_RegisterPostOnline', 'local_ChangePostOnline', 'local_IsCyberLab', 'local_UpdateCyberLabNumber',
    'local_IsPlasticDisabled', 'local_IsFastFile', 'local_IsAddrDelivery', 'local_IsNamedType', 'local_IsDeliveryWithDate', 'local_IsDeliveryWithBarcode', 'local_IsDeliveryWithPostOnline', 
    'local_WithCardHolder', 'local_WithIndigo', 'local_WithLoyalty', 'local_WithBarcode', 'local_WithEnclosure', 'local_CheckDesignIsInvalid',
    'local_PackageNumberGroups', 'local_CaseEnvelope', 'local_CaseLeaflet', 'local_CaseCover', 'local_PlasticFrontPrintType', 'local_PlasticBackPrintType', 
    'local_filetypes'
    ]

#
#   Лист изменений:
#   ---------------
#   20190325: тип файла FILETYPE_POSTBANK_ID
#   20190322: настройки ИД 'plastic_types': 40599111, 40599211
#   20190222: регистрация упаковок local_GetPackageType, добавлен 6-й ключ 'plastic_type'
#   20190524: файл-реестр с номерами лояльности FILETYPE_POSTBANK_LOYALTY
#   20190527: тип файла "Пятерочка" FILETYPE_POSTBANK_X5
#   20190701: настройки Visa MARKI Red/Blue: 40599217-40599220
#   20190709: настройки ИД 'plastic_types' Visa REWARDS Individual: 40599122
#   20190926: настройки ИД 'plastic_types' Mir Privilege Individual: 22007701
#   20191112: настройки МИР 22007704A Карты лояльности проекта "Пятерочка" (Именная)
#   20191112: настройки ИД Visa Rewards Marki Individual: 40599222
#   20191204: регистрация упаковок local_GetPackageType, добавлен 5-й ключ 'plastic_type' (дублирование транспортных упаковок)
#   20191211: дизайн 41826203 Visa Platinum Green World VP18
#   20200110: БИН 405991 'pay_system' перепривязка 'LongRSA' (ключ RSA, Мельникова)
#   20200114: флаг 'plastic_types'... disabled, блокировка дизайнов: local_IsPlasticDisabled, 
#   20200114: блокировка неактуальных дизайнов: 40599112
#   20200117: добавлен дизайн 40599223, Visa Classic Express Name (именные)
#   20200117: дизайн 220077014, изменен параметр PAY_SYSTEM:KONA_2320_NSPK_701
#   20200421: актуализация ТЗ 1.3.0:
#   20200421: добавлена линейка продуктов Mir EagleDual NoName: 22007702C, 22007702D, 22007702E
#   20200421: блокировка неактуальных дизайнов: 40599211
#   20200422: маскированы опции СПСР, s-prefix:S (None)
#   20200422: добавлены опции Почта России доставка EMS, s-prefix:E
#   20200424: добавлен признак "Конверты ОВПО" (FILETYPE_POSTBANK_CASECOVER_PRODUCTS, тег CASE_COVER): 22007702D
#   20200518: WebPerso Command: RepeatUnloadedReport (RUR)
#   20200603: настройки EMS, local_IsDeliveryWithPostonline
#   20200904: параметры дизайнов: 22007702C, 22007702D, 22007702E
#   20201007: смена дизайнов 22007702 на БИН 22007706 (!) настройки выполнять по БИН (ПРИЛОЖЕНИЕ 2. СООТВЕТСТВИЕ КОДОВ ДИЗАЙНОВ И ТИПОВ КАРТ)
#   20201022: добавлен дизайн 220077043, MirGreenWorld (именные)
#   20201130: дизайн 41826201 Visa Marki Vip VP24
#   20201130: ПРОЕКТ "КИБЕРЛАБ" дизайны 40599212, 40599213, 40599214, 40599215 Visa Cyberlab VP25,VP26,VP27,VP28
#   20201204: Добавлен Тип файла PostBank_CL (КИБЕРЛАБ): FILETYPE_POSTBANK_CYBERLAB
#   20210114: Флаг LOCAL_CHECK_POSTONLINE_FREE
#   20210116: Контроль загрузки периода config.IsCheckSuspendedDates
#   20210209: дизайн 220077012 Mir Eagle Dual Name VP29
#   20210312: дизайн 220077014, изменен параметр PAY_SYSTEM:KONA_2350_NSPK_701 (отменено)
#   20210407: дизайн 41826101 Visa Business Corporate VP30
#   20210412: local_CaseEnvelope, local_CaseLeaflet - конверт, листовка, параметры типа файла: 'envelope', 'leaflet'
#   20210423: AREPRecord root record definitions (special for VP30)
#   20210430: дизайн 40599124 Visa Вездеход 120 KONA_2320 VP31
#   20210430: дизайн 40599125 Visa Вездеход 120 NoName KONA_2320 VP32
#   20210528: дизайн 220077071 Мир Supreme KONA_2350 VP33
#   20210628: тип отправки EMS, mail-type:EMS_TENDER, transport-mode:EXPRESS (письмо банка от 17.06.2021)
#   20210823: добавить поле отчета CRDSRT Номер тиража: local_GetIssueNumber
#   20210914: смена чипа 'MICRON_706' на 'KONA_2350' для дизайнов 22007702C, 22007702D, 22007702E
#   20210924: дизайн 220077071 (VP33, Supreme): конверт, листовка
#   20211014: дизайн 40599126 (индивидульное изображения будет в поле в файле на персо) Visa Platinum Individual KONA_2350 VP34
#   20211204: блокировка дизайна 40599113, сборка ядра 1.50
#   20211211: освобождение индекса отправления core.srvlib: resumeSeen
#   20211213: контроль отправки отчетов: LOCAL_FILESTATUS_READY
#   20220124: дизайн 52731701 (VP35, MC World Elite Debit)
#   20220208: дизайн 220077071 (VP33, Supreme): добавлен картхолдер (отгрузка C2)
#

from copy import deepcopy

import os
import pymssql

import config
from app.core import ProcessException, AbstractIncomingLoaderClass, AbstractReferenceLoaderClass
from app.types import *
from app.barcodes import Code128Barcode, I25Barcode, EAN13Barcode
from app.mails import send_mail_with_attachment
from app.srvlib import makeFileTypeIndex, SRV_GetValue
from app.utils import normpath, check_folder_exists, getDate, getToday, daydelta, isIterable

from ..defaults import *
from ..postonline import registerPostOnline, changePostOnline
from ..xmllib import *

from ext import calendar, suspended_dates

##  ---------------
##  LOCAL CONSTANTS
##  ---------------

# Смена формата даты YY/MM -> MMYY
LOCAL_IS_CHANGE_EXPIREDATE = False
# Сортировка по типу пластика
LOCAL_IS_PLASTIC_BATCHSORT = False
# Сортировка по коду упаковки
LOCAL_IS_PACKAGE_BATCHSORT = True
# Установить максимальную дату отгрузки
LOCAL_IS_MAX_DELIVERY_DATE = True
# Использовать текущую дату в отчетности: 0 - повтор отчетности
LOCAL_IS_REPORT_TODAY = 1
# Выполнять проверку Тарифного пояса при приеме справочника филиалов
LOCAL_CHECK_DELIVERY_ZONE = False
# Регистрировать только новые(пустые) отправления ПочтаРоссии
LOCAL_CHECK_POSTONLINE_FREE = 0
# Тег ID записи
LOCAL_ID_TAG = 'ID'
# Формат даты отгрузки в отчетах
LOCAL_DATESTAMP = '%d.%m.%Y'
# Формат даты в файлах выгрузки
LOCAL_EASY_TIMESTAMP = '%Y%m%d_%H%M'
# Разделитель ключа доставки в имени файла
LOCAL_FILE_DELIVERY_SPLITTER = '$'
# Ключ даты отгрузки
LOCAL_DELIVERY_DATE = 'LOCAL_DELIVERY_DATE'
# Выгрузка расширенного списка документов на отгрузку: 0 - пакет документации по умолчанию, 1 - расширенный пакет
LOCAL_POSTONLINE_WITH_FORMS = 0
# Тип печати: 'THERMO' - этикетка (самоклеящийся ярлык), 'PAPER' - печатная форма E-1
LOCAL_PRINT_TYPE = 'PAPER'
# Префиксы транспортных компаний с датой отгрузки
LOCAL_DELIVERY_WITH_DATE = ('P', 'E')
# Префиксы транспортных компаний с ШПИ
LOCAL_DELIVERY_WITH_BARCODE = ('P', 'E')
# Префиксы транспортных компаний с регистрацией отправлений
LOCAL_DELIVERY_WITH_POSTONLINE = ('P', 'E')
# Статусы файлов для отправки отчетов
LOCAL_FILESTATUS_READY = (28, 61, 62, 71, 198)

##  --------
##  DEFAULTS
##  --------

# Способ доставки по умолчанию
DEFAULT_DELIVERY_TYPE = 'ПОЧТА 1 КЛАСС'
# Временной интервал для старта процесса группировки
DEFAULT_MERGE_INTERVAL = ('15:00', '16:15')
# Символ конца строки в файлах-квитанциях
DEFAULT_EOL = '\r\n'

##  -----------
##  DESCRIPTORS
##  -----------

# Наименование Банка: полное наименование, ClientIDStr (BankPerso), краткое наименование
CLIENT_NAME = ('ПАО «ПОЧТА БАНК»', 'ПочтаБанк', 'ПОЧТА БАНК',)
# Корневой каталог системы инфообмена с Банком
FILETYPE_FOLDER = 'PostBank'
# Каталог выгрузки отчетов доставки Почта России (relative)
FILETYPE_POSTONLINE_UNLOAD = '/Inkass/InputData/PostBank/postonline'
# Получатели почтовых уведомлений об ошибках
ERROR_RECIPIENTS = ('personalization@pochtabank.ru',)

"""
    FileType Descriptor.

    Keywords:

        `fieldset`  -- dict, fields mapping, key: destination field name (tag name), item's value format:

            (<number>, [<name>], [<field_type>], [<data_type>], [<perso_type>], [<encoding>], [<size>], is_obligatory, [<comment>])

                <number>        -- any, ordered number of the field
                <name>          -- str, field name
                <field_type>    -- int, const:DATA_TYPE_<TYPE>, default:this['defaults']['field_type']
                <data_type>     -- int, const:DATA_TYPE_<TYPE>, default:this['defaults']['data_type']
                <perso_type>    -- int, const:DATA_PERSO_TYPE_<TYPE>, default:undefined
                <encoding>      -- str, const:ENCODING_<TYPE>, default:this['defaults']['encoding']
                <size>          -- tuple: (min, [max]), int
                <is_obligatory> -- bool, 1/0
                <comment>       -- str, описание поля

        `defaults`  -- dict, default attributes value:

            `field_type` --  int, const:DATA_TYPE_<FIELD-TYPE>
            `data_type`  --  int, const:DATA_TYPE_<TYPE>
            `encoding`   --  tuple, const:ENCODING_<TYPE>, file field's encodings
"""

# ------------------------- #

FILETYPE_POSTBANK_PRODUCT_DESIGNS = \
    '220077012:220077014:22007702C:22007702D:22007702E:220077043:220077044:220077045:22007704A:220077071' \
    '40599111:40599112:40599113:40599114:40599115:40599122:40599124:40599125:40599126:' \
    '40599211:40599212:40599213:40599214:40599215:40599216:40599217:40599218:40599219:40599220:40599222:40599223:' \
    '41826101:41826201:41826203:' \
    '52731701'

FILETYPE_POSTBANK_TEMPLATE = {
    'class'           : AbstractIncomingLoaderClass,
    'object_type'     : FILE_TYPE_INCOMING_ORDER,
    'bankname'        : CLIENT_NAME,
    'format'          : FILE_FORMAT_CSV,
    'persotype'       : None,
    'defaults'        : {
        'field_type'        : DATA_TYPE_FIELD,
        'data_type'         : DATA_TYPE_TEXT,
        'encoding'          : ENCODING_WINDOWS,
    },
    'line_delimeter'  : crlf,
    'field_delimeter' : b'|',
    'is_trancate'     : 1,
    'is_stripped'     : 0,
    # ---------------------
    # Формат входных данных
    # ---------------------
    'fieldset'        : {
        'ID'                    : ('001', None, None, DATA_TYPE_INTEGER, None, None, (4, 20), 1, 'ID карты в системе Octopus'),
        'PID'                   : ('002', None, None, DATA_TYPE_INTEGER, None, None, (9,), 1, 'Код клиента'),
        'PAN'                   : ('003', None, None, DATA_TYPE_TEXT_NS, DATA_PERSO_TYPE_PANWIDE16, None, (19,), 1, 'Номер карты (в формате NNNN NNNN NNNN NNNN)'),
        'ExpireDate'            : ('004', 'ExpiryDate', None, DATA_TYPE_TEXT_NS, DATA_PERSO_TYPE_EXPIREDATE, None, (5,), 1, 'Дата окончания действия карты (формат mm/yy)'),
        'CardholderName'        : ('005', 'Cardholder', None, DATA_TYPE_TEXT_ANS, DATA_PERSO_TYPE_EMBOSSNAME, None, (2, 26), 0, 'Имя и фамилия держателя карты'),
        'Track1CardholderName'  : ('006', 'CH_Name_Track1', None, DATA_TYPE_TEXT_ANS, DATA_PERSO_TYPE_EMBOSSNAME, None, (2, 26), 1, 'Имя держателя карты на первом треке магнитной полосы'),
        'Organization'          : ('007', None, None, DATA_TYPE_TEXT_ANC, None, None, (2, 26), 0, 'Данные для персонализации 4-й строки на лицевой стороне карты'),
        'ProductDesign'         : ('008', None, None, DATA_TYPE_TEXT_AN, FILETYPE_POSTBANK_PRODUCT_DESIGNS, None, (1, 24), 1, 'Код дизайна пластика'),
        'BRANCHDELIVERY'        : ('009', None, None, DATA_TYPE_TEXT_NS, None, None, (0, 11), 0, 'Код филиала доставки карт'),
        'BRANCH_SEND_TO'        : ('010', None, None, DATA_TYPE_TEXT_NS, None, None, (0, 11), 0, 'Код филиала отправки карт'),
        'PSN'                   : ('011', None, None, DATA_TYPE_INTEGER, '0:1:90:91', None, (1, 2), 1, 'Значение PAN Sequence Number'),
        'DeliveryCanalCode'     : ('012', None, None, DATA_TYPE_TEXT_AN, ('0', 'PR01'), None, (1, 4), 1, 'Канал отсылки карты на адрес клиента'),
        'CardholderFIO'         : ('013', None, None, DATA_TYPE_TEXT, None, ENCODING_UNICODE, (1, 250), 0, 'ФИО клиента'),
        'CardholderAddress'     : ('014', None, None, DATA_TYPE_TEXT, None, ENCODING_UNICODE, (1, 200), 0, 'Почтовый адрес для доставки карты клиенту'),
        'ImageName'             : ('015', 'PictureID', None, DATA_TYPE_TEXT_ANC, None, None, (0, 50), 0, 'Код картинки'),
    },
    # ------------------------
    # Порядок группировки карт
    # ------------------------
    'card_groups' : {
        'N'   : 1, # C1
        'NC'  : 2, # C2
        'NCA' : 3, # inactive
        'I'   : 4, # C1
        'IC'  : 5, # inactive
        'IA'  : 6, # inactive
        'ICA' : 7, # C3
    },
}

FILETYPE_POSTBANK_NONAME_PRODUCTS = (
    '40599115', '40599125', '40599216', '40599219', '40599220', '41826101', '22007702C', '22007702D', '22007702E', '220077044', '220077045',
)

FILETYPE_POSTBANK_WITHCARDHOLDER_PRODUCTS = (
    '22007702D', '22007702E', '220077045', '220077071', '41826101',
)

FILETYPE_POSTBANK_CASECOVER_PRODUCTS = (
    '22007702D', '220077045', 
)

FILETYPE_POSTBANK_GREENWORLD_PRODUCTS = (
    '40599114', 
)

##  -------------------------------
##  НЕИМЕННЫЕ И ИМЕННЫЕ КАРТЫ БАНКА
##  -------------------------------

FILETYPE_POSTBANK_V1 = deepcopy(FILETYPE_POSTBANK_TEMPLATE)

FILETYPE_POSTBANK_V1.update({
    'tytle'           : '%s входящий файл заказа PostBank_v1 версия 1' % CLIENT_NAME[0],
    'filetype'        : 'PostBank_v1',
    # ------------------------------------------------
    # Параметры банковских продуктов (по коду дизайна)
    # ------------------------------------------------
    #   product     -- PlasticType: {VP01|VP02|VP03|VP04|VP09|VP10|VP11|VP12|VP18|VP20|VP21|VP22|VP23|VP24|VP29}
    #   scode       -- ServiceCode (MSDP)
    #   pvki        -- PVKI (MSDP)
    #   d-prefix    -- префикс баркода карты (Префикс для ШК EAN-13)
    #   s-prefix    -- префикс баркода упаковки по транспортным компаниям: (без адресной доставки, с адресной доставкой)
    #   pay_system  -- PAY_SYSTEM (SDC)
    #   name        -- наименование пластика
    #   disabled    -- признак блокировки дизайна (не использовать в отгрузке)
    #
    'plastic_types'   : {
        '220077012'   : {
            'product'    : 'VP29', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '616',
            's-prefix'   : {
                'D'         : ('RAL', 'ROL'),
                'default'   : ('RPN', 'ROL'),
                'E'         : ('REN', 'ROL'),
            },
            'pay_system' : 'KONA_2350',
            'name'       : 'Mir EagleDual Name',
            'BIN'        : '22007701',
        },
        '22007702C'   : {
            'product'    : 'VP20', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '718',
            's-prefix'   : {
                'D'         : ('RLB', None),
                'default'   : ('RPR', None),
                'E'         : ('RER', None),
            },
            'pay_system' : 'KONA_2350', 
            'name'       : 'Mir EagleDual NoName',
            'BIN'        : '22007706',
        },
        '22007702D'   : {
            'product'    : 'VP21', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '718',
            's-prefix'   : {
                'D'         : ('511', None),
                'default'   : ('511', None),
                'E'         : ('511', None),
            },
            'pay_system' : 'KONA_2350', 
            'name'       : 'Mir EagleDual NoName PR',
            'BIN'        : '22007706',
        },
        '22007702E'   : {
            'product'    : 'VP22', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '718',
            's-prefix'   : {
                'D'         : ('521', None),
                'default'   : ('521', None),
                'E'         : ('521', None),
            },
            'pay_system' : 'KONA_2350', 
            'name'       : 'Mir EagleDual NoName PFR',
            'BIN'        : '22007706',
        },
        '220077043'   : {
            'product'    : 'VP23', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '317',
            's-prefix'   : {
                'D'         : ('RAL', 'ROL'),
                'default'   : ('RPN', 'ROL'),
                'E'         : ('REN', 'ROL'),
            },
            'pay_system' : 'KONA_2350',
            'name'       : 'MirGreenWorld',
            'BIN'        : '22007704',
        },
        '220077071'   : {
            'product'    : 'VP33', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '719',
            's-prefix'   : {
                'D'         : ('RAL', 'ROL'),
                'default'   : ('RPN', 'ROL'),
                'E'         : ('REN', 'ROL'),
            },
            'pay_system' : 'KONA_2350',
            'name'       : 'Mir Supreme',
            'BIN'        : '22007707',
            'envelope'   : 'C2-COVER1.NO-WINDOW',
            'leaflet'    : 'C2-I.SUPREME',
        },
        '40599112'    : {
            'product'    : 'VP03', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '516',
            's-prefix'   : {
                'D'         : ('RAL', 'ROL'),
                'default'   : ('RPN', 'ROL'),
                'E'         : ('REN', 'ROL'),
            },
            'pay_system' : 'LongRSA',
            'name'       : 'Visa Platinum PayWave Eagle',
            'disabled'   : 0,
        },
        '40599113'    : {
            'product'    : 'VP01', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '516',
            's-prefix'   : {
                'D'         : ('RAL', 'ROL'),
                'default'   : ('RPN', 'ROL'),
                'E'         : ('REN', 'ROL'),
            },
            'pay_system' : 'LongRSA',
            'name'       : 'Visa Platinum PayWave Cosmos',
            'disabled'   : 1,
        },
        '40599114'    : {
            'product'    : 'VP04', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '516',
            's-prefix'   : {
                'D'         : ('RAL', 'ROL'),
                'default'   : ('RPN', 'ROL'),
                'E'         : ('REN', 'ROL'),
            },
            'pay_system' : 'LongRSA',
            'name'       : 'Visa Platinum PayWave Green World',
        },
        '40599115'    : {
            'product'    : 'VP02', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '516',
            's-prefix'   : {
                'D'         : ('RLB', None),
                'default'   : ('RPR', None),
                'E'         : ('RER', None),
            },
            'pay_system' : 'LongRSA',
            'name'       : 'Visa Platinum PayWave Cosmos NoName',
        },
        '40599124'    : {
            'product'    : 'VP31', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '516',
            's-prefix'   : {
                'D'         : ('RAL', 'ROL'),
                'default'   : ('RPN', 'ROL'),
                'E'         : ('REN', 'ROL'),
            },
            'pay_system' : 'LongRSA',
            'name'       : 'Visa Вездеход 120',
        },
        '40599125'    : {
            'product'    : 'VP32', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '516',
            's-prefix'   : {
                'D'         : ('RLB', None),
                'default'   : ('RPR', None),
                'E'         : ('RER', None),
            },
            'pay_system' : 'LongRSA',
            'name'       : 'Visa Вездеход 120 NoName',
        },
        '40599216'    : {
            'product'    : 'VP14', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '416',
            's-prefix'   : {
                'D'         : ('RLB', None),
                'default'   : ('RPR', None),
                'E'         : ('RER', None),
            },
            'pay_system' : 'LongRSA',
            'name'       : 'Visa Classic PayWave Express',
        },
        '40599217'    : {
            'product'    : 'VP09', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '416',
            's-prefix'   : {
                'D'         : ('RAL', 'ROL'),
                'default'   : ('RPN', 'ROL'),
                'E'         : ('REN', 'ROL'),
            },
            'pay_system' : 'LongRSA',
            'name'       : 'Visa MARKI Red',
        },
        '40599218'    : {
            'product'    : 'VP10', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '416',
            's-prefix'   : {
                'D'         : ('RAL', 'ROL'),
                'default'   : ('RPN', 'ROL'),
                'S'         : ('RSN', 'ROL'),
                'E'         : ('REN', 'ROL'),
            },
            'pay_system' : 'LongRSA',
            'name'       : 'Visa MARKI Blue',
        },
        '40599219'    : {
            'product'    : 'VP11', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '416',
            's-prefix'   : {
                'D'         : ('RLB', None),
                'default'   : ('RPR', None),
                'S'         : ('RSR', None),
                'E'         : ('REN', None),
            },
            'pay_system' : 'LongRSA',
            'name'       : 'Visa MARKI Red NoName',
        },
        '40599220'    : {
            'product'    : 'VP12', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '416',
            's-prefix'   : {
                'D'         : ('RLB', None),
                'default'   : ('RPR', None),
                'E'         : ('REN', None),
            },
            'pay_system' : 'LongRSA',
            'name'       : 'Visa MARKI Blue NoName',
        },
        '41826101'    : {
            'product'    : 'VP30', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '816',
            's-prefix'   : {
                'D'         : ('RLB', None),
                'default'   : ('RPR', None),
                'E'         : ('RER', None),
            },
            'pay_system' : 'LongRSA',
            'name'       : 'Visa Business Corporate',
            'envelope'   : 'C2-COVER1.01',
            'leaflet'    : 'C2-N.01',
            'AREPRecord' : 'RecordX5',
        },
        '41826201'    : {
            'product'    : 'VP24', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '518',
            's-prefix'   : {
                'D'         : ('RAL', 'ROL'),
                'default'   : ('RPN', 'ROL'),
                'E'         : ('REN', 'ROL'),
            },
            'pay_system' : 'LongRSA',
            'name'       : 'Visa MARKI VIP',
        },
        '41826203'    : {
            'product'    : 'VP18', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '518',
            's-prefix'   : {
                'D'         : ('RAL', 'ROL'),
                'default'   : ('RPN', 'ROL'),
                'E'         : ('REN', 'ROL'),
            },
            'pay_system' : 'LongRSA',
            'name'       : 'Visa Platinum Green World',
        },
        '40599223'    : {
            'product'    : 'VP19', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '416',
            's-prefix'   : {
                'D'         : ('RAL', 'ROL'),
                'default'   : ('RPN', 'ROL'),
                'E'         : ('REN', 'ROL'),
            },
            'pay_system' : 'LongRSA',
            'name'       : 'Visa Classic Express Name',
        },
        '52731701'   : {
            'product'    : 'VP35', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '520',
            's-prefix'   : {
                'D'         : ('RAL', 'ROL'),
                'default'   : ('RPN', 'ROL'),
                'E'         : ('REN', 'ROL'),
            },
            'pay_system' : 'KONA_2320_MC',
            'name'       : 'MC World Elite Debit',
            'BIN'        : '527317',
            'envelope'   : 'C2-COVER1.NO-WINDOW',
        },
    },
})

##  ---------------------
##  ИНДИВИДУАЛЬНЫЙ ДИЗАЙН
##  ---------------------

FILETYPE_POSTBANK_ID = deepcopy(FILETYPE_POSTBANK_TEMPLATE)

FILETYPE_POSTBANK_ID.update({
    'tytle'           : '%s входящий файл заказа PostBank_ID индивидуальный дизайн' % CLIENT_NAME[0],
    'filetype'        : 'PostBank_ID',
    # ------------------------------
    # Параметры банковских продуктов
    # ------------------------------
    #   product     -- PlasticType: {VP05|VP06|VP13|VP17}
    #   scode       -- ServiceCode (MSDP)
    #   pvki        -- PVKI (MSDP)
    #   d-prefix    -- префикс баркода карты
    #   s-prefix    -- префикс баркода упаковки по транспортным компаниям: (без адресной доставки, с адресной доставкой)
    #   pay_system  -- PAY_SYSTEM (SDC)
    #   name        -- наименование пластика
    #
    'plastic_types'   : {
        '40599111'    : {
            'product'    : 'VP05', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '516',
            's-prefix'   : {
                'D'         : ('RAL', 'ROL'),
                'default'   : ('RPN', 'ROL'),
                'E'         : ('REN', 'ROL'),
            },
            'pay_system' : 'LongRSA', #'KONA_2320',
            'name'       : 'Visa Platinum Individual',
            'indigo'     : 1,
        },
        '40599122'    : {
            'product'    : 'VP13', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '516',
            's-prefix'   : {
                'D'         : ('RAL', 'ROL'),
                'default'   : ('RPN', 'ROL'),
                'E'         : ('REN', 'ROL'),
            },
            'pay_system' : 'LongRSA',
            'name'       : 'Visa REWARDS Individual',
            'indigo'     : 1,
        },
        '40599126'    : {
            'product'    : 'VP34', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '516',
            's-prefix'   : {
                'D'         : ('RAL', 'ROL'),
                'default'   : ('RPN', 'ROL'),
                'E'         : ('REN', 'ROL'),
            },
            'pay_system' : 'LongRSA',
            'name'       : 'Visa Platinum Ind LogoBack',
            'indigo'     : 1,
        },
        '40599211'    : {
            'product'    : 'VP06', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '416',
            's-prefix'   : {
                'D'         : ('RAL', 'ROL'),
                'default'   : ('RPN', 'ROL'),
            },
            'pay_system' : 'LongRSA',
            'name'       : 'Visa Classic Individual',
            'indigo'     : 1,
            'disabled'   : 1,
        },
        '40599222'    : {
            'product'    : 'VP17', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '416',
            's-prefix'   : {
                'D'         : ('RAL', 'ROL'),
                'default'   : ('RPN', 'ROL'),
                'E'         : ('REN', 'ROL'),
            },
            'pay_system' : 'LongRSA',
            'name'       : 'Visa Rewards Marki Individual',
            'indigo'     : 1,
        },
    },
})

##  -------------------------
##  ИНДИВИДУАЛЬНЫЙ ДИЗАЙН МИР
##  -------------------------

FILETYPE_POSTBANK_IDM = deepcopy(FILETYPE_POSTBANK_TEMPLATE)

FILETYPE_POSTBANK_IDM.update({
    'tytle'           : '%s входящий файл заказа PostBank_IDM индивидуальный дизайн' % CLIENT_NAME[0],
    'filetype'        : 'PostBank_IDM',
    # ------------------------------
    # Параметры банковских продуктов
    # ------------------------------
    #   product     -- PlasticType: {VP15}
    #   scode       -- ServiceCode (MSDP)
    #   pvki        -- PVKI (MSDP)
    #   d-prefix    -- префикс баркода карты
    #   s-prefix    -- префикс баркода упаковки по транспортным компаниям: (без адресной доставки, с адресной доставкой)
    #   pay_system  -- PAY_SYSTEM (SDC)
    #   name        -- наименование пластика
    #
    'plastic_types'   : {
        '220077014'   : {
            'product'    : 'VP15', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '616',
            's-prefix'   : {
                'D'         : ('RAL', 'ROL'),
                'default'   : ('RPN', 'ROL'),
                'S'         : ('RSN', 'ROL'),
                'E'         : ('REN', 'ROL'),
            },
            'pay_system' : 'KONA_2320_NSPK_701', # KONA_2320_NSPK
            'name'       : 'Mir Privilege Individual',
            'indigo'     : 1,
        },
    },
})

##  ----------------
##  ПРОЕКТ ПЯТЁРОЧКА
##  ----------------

FILETYPE_POSTBANK_X5 = deepcopy(FILETYPE_POSTBANK_TEMPLATE)

FILETYPE_POSTBANK_X5.update({
    'tytle'           : '%s входящий файл заказа PostBank_X5 Пятёрочка' % CLIENT_NAME[0],
    'filetype'        : 'PostBank_X5',
    'postfix'         : '_X5',
    # ------------------------------
    # Параметры банковских продуктов
    # ------------------------------
    #   product     -- PlasticType: {VP07|VP08|VP16}
    #   scode       -- ServiceCode (MSDP)
    #   pvki        -- PVKI (MSDP)
    #   d-prefix    -- префикс баркода карты
    #   s-prefix    -- префикс баркода упаковки по транспортным компаниям: (без адресной доставки, с адресной доставкой)
    #   pay_system  -- PAY_SYSTEM (SDC)
    #   name        -- наименование пластика
    #
    'plastic_types'   : {
        '220077044'   : {
            'product'    : 'VP07', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : 'XXX',
            's-prefix'   : {
                'D'         : ('RLB', 'RLB'),
                'default'   : ('RPR', 'RPR'),
                'E'         : ('RER', 'ROL'),
            },
            'pay_system' : 'KONA_2320_X5',
            'name'       : 'Mir X5 Dual',
        },
        '220077045'   : {
            'product'    : 'VP08', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : 'XXX',
            's-prefix'   : {
                'D'         : ('531', '531'),
                'default'   : ('531', '531'),
                'E'         : ('531', '531'),
            },
            'pay_system' : 'KONA_2320_X5',
            'name'       : 'Mir X5 Dual PR',
        },
        '22007704A'   : {
            'product'    : 'VP16', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : 'XXX',
            's-prefix'   : {
                'D'         : ('RAL', 'ROL'),
                'default'   : ('RPN', 'ROL'),
                'E'         : ('REN', 'ROL'),
            },
            'pay_system' : 'KONA_2320_X5',
            'name'       : 'Mir X5 Dual Name',
        },
    },
})

##  ---------------
##  ПРОЕКТ КИБЕРЛАБ
##  ---------------

FILETYPE_POSTBANK_CYBERLAB = deepcopy(FILETYPE_POSTBANK_TEMPLATE)

FILETYPE_POSTBANK_CYBERLAB.update({
    'tytle'           : '%s входящий файл заказа PostBank_CL КИБЕРЛАБ' % CLIENT_NAME[0],
    'filetype'        : 'PostBank_CL',
    'postfix'         : '_CL',
    # ------------------------------
    # Параметры банковских продуктов
    # ------------------------------
    #   product     -- PlasticType: {VP25|VP26|VP27|VP28}
    #   scode       -- ServiceCode (MSDP)
    #   pvki        -- PVKI (MSDP)
    #   d-prefix    -- префикс баркода карты
    #   s-prefix    -- префикс баркода упаковки по транспортным компаниям: (без адресной доставки, с адресной доставкой)
    #   pay_system  -- PAY_SYSTEM (SDC)
    #   name        -- наименование пластика
    #
    'plastic_types'   : {
        '40599212'    : {
            'product'    : 'VP25', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : None,
            's-prefix'   : {
                'D'         : ('RAL', 'ROL'),
                'default'   : ('RPN', 'ROL'),
                'S'         : ('RSN', 'ROL'),
            },
            'pay_system' : 'LongRSA',
            'name'       : 'Visa Cyberlab Wasted',
            'front_print': 'no',
            'back_print' : 'LASER',
            'no_barcode' : 1,
        },
        '40599213'    : {
            'product'    : 'VP26', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : None,
            's-prefix'   : {
                'D'         : ('RAL', 'ROL'),
                'default'   : ('RPN', 'ROL'),
                'S'         : ('RSN', 'ROL'),
            },
            'pay_system' : 'LongRSA',
            'name'       : 'Visa Cyberlab Alien',
            'front_print': 'no',
            'back_print' : 'LASER',
            'no_barcode' : 1,
        },
        '40599214'    : {
            'product'    : 'VP27', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : None,
            's-prefix'   : {
                'D'         : ('RAL', 'ROL'),
                'default'   : ('RPN', 'ROL'),
                'S'         : ('RSN', 'ROL'),
            },
            'pay_system' : 'LongRSA',
            'name'       : 'Visa Cyberlab SWAT',
            'front_print': 'no',
            'back_print' : 'LASER',
            'no_barcode' : 1,
        },
        '40599215'    : {
            'product'    : 'VP28', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : None,
            's-prefix'   : {
                'D'         : ('RAL', 'ROL'),
                'default'   : ('RPN', 'ROL'),
                'S'         : ('RSN', 'ROL'),
            },
            'pay_system' : 'LongRSA',
            'name'       : 'Visa Cyberlab Dragon',
            'front_print': 'no',
            'back_print' : 'LASER',
            'no_barcode' : 1,
        },
    },
})

##  ---------------------------------
##  ФАЙЛ-РЕЕСТР С НОМЕРАМИ ЛОЯЛЬНОСТИ
##  ---------------------------------

FILETYPE_POSTBANK_LOYALTY = {
    'class'           : AbstractReferenceLoaderClass,
    'object_type'     : FILE_TYPE_INCOMING_LOYALTY,
    'tytle'           : 'ПОЧТА БАНК входящий файл-реестр с номерами лояльности',
    'filetype'        : 'PostBank_Lty',
    'format'          : FILE_FORMAT_CSV,
    'persotype'       : None,
    'defaults'        : {
        'field_type'        : DATA_TYPE_FIELD,
        'data_type'         : DATA_TYPE_TEXT,
        'encoding'          : ENCODING_WINDOWS,
    },
    'line_delimeter'  : crlf,
    'field_delimeter' : b';',
    'with_header'     : 0,
    # ---------------------
    # Формат входных данных
    # ---------------------
    'fieldset'        : {
        'LoyaltyNumber'     : ('001', None, None, DATA_TYPE_TEXT_N, None, None, (16,), 1, 'Бонусный номер счёта (номер лояльности)'),
        'EAN'               : ('002', None, None, DATA_TYPE_TEXT_N, None, None, (13,), 1, 'Номер для формирования ШК EAN-13'),
    },
}

##  -------------------
##  СПРАВОЧНИК ФИЛИАЛОВ
##  -------------------

FILETYPE_POSTBANK_REFERENCE = {
    'class'           : AbstractReferenceLoaderClass,
    'object_type'     : FILE_TYPE_INCOMING_REFERENCE,
    'tytle'           : 'ПОЧТА БАНК входящий дополнительный файл',
    'filetype'        : 'PostBank_Ref',
    'format'          : FILE_FORMAT_CSV,
    'persotype'       : None,
    'defaults'        : {
        'field_type'        : DATA_TYPE_FIELD,
        'data_type'         : DATA_TYPE_TEXT,
        'encoding'          : ENCODING_WINDOWS,
    },
    'line_delimeter'  : crlf,
    'field_delimeter' : b';',
    'with_header'     : 1,
    # ---------------------
    # Формат входных данных
    # ---------------------
    'fieldset'        : {
        'CompanyName'       : ('001', None, None, DATA_TYPE_TEXT, None, None, (1, 250), 1, 'Наименование подразделения'),
        'BranchDelivery'    : ('002', None, None, DATA_TYPE_INTEGER, None, None, (1, 11), 1, 'Код элемента структуры'),
        'BranchSendTo'      : ('003', None, None, DATA_TYPE_INTEGER, None, None, (1, 11), 1, 'Код филиала доставки карт'),
        'NonamedPostType'   : ('004', None, None, DATA_TYPE_TEXT, ['DHL', 'СПСР', 'ПОЧТА 1 КЛАСС', 'EMS'], None, (1, 20), 1, 'Способ доставки неименных карт'),
        'NamedPostType'     : ('005', None, None, DATA_TYPE_TEXT, ['DHL', 'СПСР', 'ПОЧТА 1 КЛАСС', 'EMS'], None, (1, 20), 1, 'Способ доставки именных карт'),
        'Receiver'          : ('006', None, None, DATA_TYPE_TEXT, None, None, (1, 250), 0, 'Организация-получатель'),
        'Address'           : ('007', None, None, DATA_TYPE_TEXT, None, None, (1, 4000), 0, 'Адрес'),
        'NonamedContact'    : ('008', None, None, DATA_TYPE_TEXT, None, None, (1, 250), 0, 'Контакт получателя (неименные карты)'),
        'NamedContact'      : ('009', None, None, DATA_TYPE_TEXT, None, None, (1, 250), 0, 'Контакт получателя (именные карты)'),
        'NonamedPhone'      : ('010', None, None, DATA_TYPE_TEXT, None, None, (1, 50), 0, 'Телефон (неименные)'),
        'NamedPhone'        : ('011', None, None, DATA_TYPE_TEXT, None, None, (1, 50), 0, 'Телефон (именные)'),
        'Zone'              : ('012', None, None, DATA_TYPE_INTEGER, '1:2:3:4:5', None, (1,), 0, 'Тарифный пояс'),
    },
}

"""
    References Block.
    
    Public definitions:
    
        `SQL`                -- dict, SQL-queries to operate with reference
        
        `REF_INDEX`          -- list, number of fields in queries
        
        `REF_ENCODE_COLUMNS` -- tuple, list of fields to encode from DBMS internal encoding
"""

SQL = {
    'LoyaltyNumbers' : {
        'check1'   : 'SELECT TOP 1 * FROM [BankDB].[dbo].[CUSTOM_PostBankLoyaltyNumbers_tb] WHERE LoyaltyNumber=%s',
        'check2'   : 'SELECT TOP 1 * FROM [BankDB].[dbo].[CUSTOM_PostBankLoyaltyNumbers_tb] WHERE EAN=%s',
        'add'      : 'INSERT INTO [BankDB].[dbo].[CUSTOM_PostBankLoyaltyNumbers_tb](LoyaltyNumber, EAN, RD) VALUES(%s, %s, %s)',
        'get'      : 'SELECT TOP 1 TID, LoyaltyNumber, EAN FROM [BankDB].[dbo].[CUSTOM_PostBankLoyaltyNumbers_tb] WHERE PAN IS NULL',
        'register' : 'UPDATE [BankDB].[dbo].[CUSTOM_PostBankLoyaltyNumbers_tb] SET '
                        'PAN=%s'
                     ' '
                     'WHERE TID=%d',
        'fix'      : 'UPDATE [BankDB].[dbo].[CUSTOM_PostBankLoyaltyNumbers_tb] SET '
                        'FileID=%d,'
                        'Recno=%d'
                     ' '
                     'WHERE TID=%d',
        'select'   : 'SELECT TOP 1 * FROM [BankDB].[dbo].[CUSTOM_PostBankLoyaltyNumbers_tb] WHERE TID=%d',
    },
    'DeliveryRef' : {
        'check'    : 'SELECT TOP 1 * FROM [BankDB].[dbo].[CUSTOM_PostBankDeliveryRef_tb] WHERE BranchDelivery=%d',
        'add'      : 'INSERT INTO [BankDB].[dbo].[CUSTOM_PostBankDeliveryRef_tb] VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
        'update'   : 'UPDATE [BankDB].[dbo].[CUSTOM_PostBankDeliveryRef_tb] SET '
                        'CompanyName=%s,'
                        'BranchDelivery=%s,'
                        'BranchSendTo=%s,'
                        'NonamedPostType=%s,'
                        'NamedPostType=%s,'
                        'Receiver=%s,'
                        'Address=%s,'
                        'NonamedContact=%s,'
                        'NamedContact=%s,'
                        'NonamedPhone=%s,'
                        'NamedPhone=%s,'
                        'Zone=%s,'
                        'RD=%s'
                     ' '
                     'WHERE TID=%d',
        'select'   : 'SELECT TOP 1 * FROM [BankDB].[dbo].[CUSTOM_PostBankDeliveryRef_tb] WHERE TID=%d',
    },
    'StampNumber' : {
        'register' : '[dbo].[REGISTER_PostBankStamp_sp]',
    },
    'PostCode' : {
        'register' : '[dbo].[REGISTER_PostBankCode_sp]',
    },
    'PackageNumber' : {
        'groups'   : 'SELECT PackageNumber, PackageType, sum(RecordsCount) as Records FROM [BankDB].[dbo].[CUSTOM_PostBankStamp_tb] '
                        'WHERE FName=%s '
                        'GROUP BY PackageNumber, PackageType '
                        'ORDER BY Records desc, PackageType, PackageNumber',
    },
    'CyberLabNumber' : {
        'register' : '[dbo].[REGISTER_PostBankCyberLabNumber_sp]',
    },
    'IssueNumber' : {
        'get'      : 'SELECT PValue FROM [BankDB].[dbo].[WEB_FileTZs_vw] '
                        'WHERE FileType=%s and TagValue=%s and PName=\'Номер тиража\''
    },
}

REF_INDEX = makeFileTypeIndex(FILETYPE_POSTBANK_REFERENCE)

REF_ENCODE_COLUMNS = (1,4,5,6,7,8,9,10,11)

DEFAULT_FILETYPE = FILETYPE_POSTBANK_V1

local_filetypes = {
    FILETYPE_POSTBANK_V1['filetype'] : FILETYPE_POSTBANK_V1,
    FILETYPE_POSTBANK_ID['filetype'] : FILETYPE_POSTBANK_ID,
    FILETYPE_POSTBANK_IDM['filetype'] : FILETYPE_POSTBANK_IDM,
    FILETYPE_POSTBANK_X5['filetype'] : FILETYPE_POSTBANK_X5,
    FILETYPE_POSTBANK_CYBERLAB['filetype'] : FILETYPE_POSTBANK_CYBERLAB,
}
#
#   Local Functions
#
def _get_filetype(filetype):
    return filetype and local_filetypes.get(filetype) or DEFAULT_FILETYPE

def _get_product_param(filetype, product_design, param, default=None):
    """
        Returns `key` value for given product design param
    """
    f = _get_filetype(filetype)
    p = f and f.get('plastic_types')
    d = p and product_design and p.get(product_design)
    return d and param and d.get(param) or default

# ========================= #

def local_GetErrorCode(keys, key, code=None):
    """
        Код ошибки в квитанциях
    """
    return key in keys and '%02d' % (keys.index(key)+1) or code or '00'

def local_GetDeliveryCompany(delivery_type):
    """
        Условное обозначение транспортной компании по способу доставки
    """
    return delivery_type == 'СПСР' and 'S' or delivery_type == 'EMS' and 'E' or delivery_type =='DHL' and 'D' or 'P'

def local_GetPostBarcode(value, code=None):
    """
        ШПИ код (Code128, Interleaved 2 of 5).

        IDAutomationC128S
        IDAutomationC128XS
        IDAutomationUPCEANS
        IntP48DlTt
        IDAutomationI25XL
    """
    if not value:
        return ''
    elif not code or code == 'I25':
        return I25Barcode().ttf(value)
    elif code == 'EAN13':
        return EAN13Barcode().ttf(value)
    return Code128Barcode().ttf(value)

def local_IsPlasticDisabled(product_design, **kw):
    """
        Проверка блокировки дизайна (disabled).
        
        Аргументы:
            product_design -- str, символьный код продукта '405991XX'
        
        Ключевые аргументы:
            filetype       -- str, тип файла

        Возврат:
            bool, флаг блокировки: 1/0.
    """
    filetype = local_filetypes.get(kw.get('filetype')) or DEFAULT_FILETYPE
    value = filetype['plastic_types'].get(product_design)

    if not value:
        return False

    return value.get('disabled') and True or False

def local_GetPlasticInfo(product_design, **kw):
    """
        Информация о продукте.
        
        Аргументы:
            product_design -- str, символьный код дизайна '405991XX[X]'
        
        Ключевые аргументы:
            filetype       -- str, тип файла
            key            -- str, идентификатор параметра (keys)

        Возврат:
            list, [<код дизайна>, <сервис-код MSDP>, <PVKI>, <префикс дизайна>, <тип чипа>, <name>].
    """
    keys = ('product', 'scode', 'pvki', 'd-prefix', 'pay_system', 'name',)

    filetype = local_filetypes.get(kw.get('filetype')) or DEFAULT_FILETYPE
    value = filetype['plastic_types'].get(product_design)

    key = kw.get('key')

    if not value and not key:
        return (None,)*6

    if key:
        return value and key and value.get(key) or None
    return [value and value.get(x) for x in keys]

def local_GetPlasticSPrefix(product_design, delivery_type, **kw):
    """
        Префикс для пломб.
        
        Аргументы:
            product_design -- str, символьный код продукта '405991XX'
            delivery_type  -- str, тип доставки (транспортная компания) {СПСР|EMS|DHL|...}, default:ПочтаРоссии ('P')
        
        Ключевые аргументы:
            orderfile      -- str, имя файла
            filetype       -- str, тип файла
            index          -- int, {0|1} 1:адресная доставка

        Возврат:
            str, префикс для пломбы: {ROL|RAL|...}, XXX - значение не определено.
    """
    key = 's-prefix'

    orderfile = kw.get('filename') or ''
    filetype = local_filetypes.get(kw.get('filetype')) or DEFAULT_FILETYPE
    index = kw.get('index') or 0
    item = filetype['plastic_types'].get(product_design)

    if not (item and isinstance(item, dict) and key in item):
        raise ProcessException('Unexpected Error[PlasticSPrefix]: %s product_design:%s' % (
            orderfile, product_design))

    item = item[key]
    delivery_company = local_GetDeliveryCompany(delivery_type)

    if not delivery_company in item and delivery_company != 'P':
        raise ProcessException('Unexpected Error[PlasticSPrefix]: %s product_design:%s, delivery_company:%s' % (
            orderfile, product_design, delivery_company))

    value = item.get(delivery_company) or item.get('default')

    return value and isIterable(value) and len(value) > index and value[index] or '000' # XXX

def local_GetPackageType(node):
    """
        Тип транспортного пакета (в SQL-запросах)
    """
    # Тип карт {I|N}{C}{A}
    card_type = getTag(node, 'CardType')
    # Тип пластика (VPXX)
    plastic_type = getTag(node, 'PlasticType')
    # Вид упаковки (КЕЙС1, КЕЙС2)
    package_type = getTag(node, 'PackageType')
    # Способ доставки (транспортная компания)
    delivery_company = local_GetDeliveryCompany(getTag(node, 'DeliveryType'))
    # Код элемента структуры
    branch_delivery = getTag(node, 'BRANCHDELIVERY')
    # Код филиала доставки карт
    branch_send_to = getTag(node, 'BRANCH_SEND_TO')
    #return '%s:%s:%s:%s:%s||%s:%s' % (delivery_company, branch_send_to, branch_delivery, package_type, plastic_type, card_type, plastic_type)
    return '%s:%s:%s:%s||%s:%s' % (delivery_company, branch_send_to, branch_delivery, package_type, card_type, plastic_type)

def local_GetPackageSize(node, order):
    """
        Объем заказа по количеству карт.
        
        Возврат:
            s, int -- максимальное кол-во карт в упаковке 1-го уровня (размер пломбы|конверта)
            p, int -- максимальное кол-во пломб|карт в транспортной упаковке
    """
    # Тип карт
    card_type = getTag(node, 'CardType')
    # Вид упаковки (КЕЙС1, КЕЙС2)
    package_type = getTag(node, 'PackageType')
    # Ттранспортная компания
    delivery_company = getTag(node, 'DeliveryCompany')
    # Кол-во карт в заказе
    size = order.fqty
    if card_type in ('ICA','IA') and package_type in ('C2','C3'):
        s, p = 1, 1
    elif card_type.startswith('N') and package_type == 'C2':
        if delivery_company == 'D':
            s, p = 20, 10
        elif delivery_company == 'S':
            s, p = 20, 10
        elif delivery_company == 'E':
            s, p = 20, 10
        else:
            s, p = 20, 1
    else:
        if delivery_company == 'D':
            s, p = 10, size <= 200 and 20 or 50
        elif delivery_company == 'S':
            s, p = 10, size <= 50 and 5 or size <= 100 and 10 or size <= 500 and 50 or 50 # 70 !
        elif delivery_company == 'E':
            s, p = 10, size <= 200 and 20 or 50
        else:
            s, p = 10, 15
    return s, p

def local_GetPackageWeight(ptype, cards, s=10, delivery_company=None, enclosure=None):
    """
        Вес почтового отправления.

        Аргументы:
            ptype -- тип упаковки CASE_BOX: C1|C2-BOX|C2-LETTER|C3-LETTER
            cards -- кол-во карт в отправлении
            s     -- максимальное кол-во карт в упаковке 1-го уровня, default:10

        Ключевые аргументы:
            delivery_company -- str, код транспортной компании: D|S|P
            enclosure        -- str, буклет-вложение (наименование)
    """
    if ptype == 'C2-BOX':
        return int(cards*18 + 42)
    elif ptype in ('C2-LETTER','C3-LETTER'):
        return 18
    x = int(cards*5 + (s > 0 and 8*(int(cards/s) + (cards%s > 0 and 1 or 0)) or 0)) + (
        delivery_company == 'D' and (cards > 400 and 250 or 30) or
        16)
    if enclosure == 'GREENWORLD':
        x += cards*51
    return x

def local_GetCardGroup(key, **kw):
    """
        Группа карт в сортировке
        
        Ключевые аргументы:
            filetype       -- str, тип файла
    """
    filetype = local_filetypes.get(kw.get('filetype')) or DEFAULT_FILETYPE
    return filetype['card_groups'].get(key) or 9

def local_GetMergePostfix(**kw):
    filetype = local_filetypes.get(kw.get('filetype')) or DEFAULT_FILETYPE
    return filetype.get('postfix') or ''

def local_GetAREPRecordName(order, filetype, product_design, **kw):
    return \
        local_WithLoyalty(order) and (kw.get('is_addr_delivery') and 'Record' or 'RecordX5') or \
        local_IsCyberLab(order) and 'RecordCL' or \
        _get_product_param(filetype, product_design, 'AREPRecord')

def local_ParseAddress(node, key):
    """
        Адрес доставки
        
        Структура адреса в справочнике:
        
        1 - индекс;
        2 - тип региона;
        3 - регион;
        4 - тип района;
        5 - район;
        6 - тип города;
        7 - город;
        8 - тип населённого пункта;
        9 - населённый пункт;
        10 - тип улицы;
        11 - улица;
        12 - номер дома;
        13 - корпус;
        14 - строение;
        15 - владение;
        16 - номер офиса.
    """
    return FMT_ParseAddress(getTag(node, key), as_dict=True)

def local_UpdateStampCode(node, order, connect, logger, saveback, **kw):
    """
        Генерация номера пломбы в транспортной упаковке.

        Аргументы:
            node                -- ET.Element, узел тега текущей записи заказа, тег <FileBody_Record>
            order               -- Order, заказ
            connect             -- func, функция для работы с базой данных
            logger              -- func, функция печати журнала
            saveback            -- dict, сохраненные данные обработки на предыдущих итерациях

        Ключевые аргументы:
            filename            -- str, имя формируемого файла-заказа
            filetype            -- str, тип файла

        Возврат:
            str, stamp_code     -- номер пломбы
            str, stamp_index    -- последние 4 цифры PAN первой карты в упаковке
            str, package_code   -- код транспортной упаковки
            str, post_code      -- ШПИ (опционально)
    """
    orderfile = kw.get('filename') or order.filename
    filetype = kw.get('filetype') or order.filetype
    
    recno = getTag(node, 'FileRecNo')

    # Дизайн продукта
    product_design = getTag(node, 'ProductDesign')
    """
    if local_IsPlasticDisabled(product_design, filetype=filetype):
        config.print_to(None, 'PlasticDisabled:%s' % product_design)
        return ('',)*4
    """
    card_type = getTag(node, 'CardType')
    package_type = getTag(node, 'PackageType')

    delivery_type = getTag(node, 'DeliveryType')
    PAN4 = getTag(node, 'PAN')[-4:]
    is_addr_delivery = getBooleanTag(node, 'IsAddrDelivery')

    # Префикс для пломб
    index = is_addr_delivery and 1 or 0
    stamp_prefix = local_GetPlasticSPrefix(product_design, delivery_type, index=index, filetype=filetype, filename=orderfile)

    mode = 'StampNumber'
    """
    # Для именных карт с адресной доставкой пломба не формируется (!!!)
    if card_type in ('ICA', 'IA') and package_type in ('C2','C3'):
        mode = 'PostCode'
    """
    package_type = local_GetPackageType(node)
    stamp_limit, package_limit = local_GetPackageSize(node, order)
    params = [1, orderfile, package_type, recno, PAN4, stamp_limit, package_limit, pymssql.output(str)]

    if config.IsDeepDebug:
        config.print_to(None, '%s, params:%s' % (mode, params[:7]))

    cursor, is_error = connect(SQL[mode]['register'], params, with_commit=False, with_result=True, callproc=True, raise_error=True)

    if is_error or not cursor or len(cursor) < 7:
        raise ProcessException('SQL Error[register], mode:%s, cursor:%s' % (mode, cursor))

    # Сквозной номер упаковки
    x = cursor[7].split(':')
    stamp_number, stamp_index, package_number, post_code = int(x[0] or 0), x[1], int(x[2] or 0), x[3]

    if config.IsDebug:
        config.print_to(None, '%s:%s, params:%s' % (mode, x, params[:7]))

    # --------------------
    # Номер пломбы [an 10]
    # --------------------

    stamp_code = ''
    if mode == 'StampNumber':
        stamp_code = '%3s%07d' % (stamp_prefix, stamp_number)
    updateTag(node, 'StampCode', stamp_code)

    # --------------------------------
    # Трек-номер транспортной упаковки
    # --------------------------------

    package_code = ''
    if mode:
        x = getTag(node, 'DeliveryDate').split('.')
        delivery_date = '%s%s%s' % (x[0], x[1], x[2][-2:])

        package_code = '%1d%6s%05d' % (
            delivery_type == 'DHL' and 1 or delivery_type == 'СПСР' and 2 or 0,
            delivery_date,
            package_number or int(recno)
        )
    updateTag(node, 'PackageCode', package_code)

    return stamp_code, stamp_index, package_code, post_code

def local_RegisterPostOnline(mode, case, ids, **kw):
    """
        Онлайн-регистрация отправлений на портале ПОЧТА РОССИИ.

        см. postonline.registerPostOnline

        Ключевые аргументы:
            unload_to -- str[optional], подкаталог выгрузки файлов клиента
            send_date -- str[optional], дата отправления, default:today
    """
    def get_destination(**kw):
        root = kw.get('unload_to') or normpath('%s%s' % (config.persostation, FILETYPE_POSTONLINE_UNLOAD))
        send_date = kw.get('send_date') or getDate(getToday(), config.DATE_STAMP)
        destination = normpath('%s/%s' % (root, send_date))
        return root, send_date, destination

    return registerPostOnline(mode, case, ids, get_destination=get_destination, **kw)

def local_ChangePostOnline(batches, send_date, **kw):
    """
        Перерегистрация отправлений на портале ПОЧТА РОССИИ.

        см. postonline.registerPostOnline

        Ключевые аргументы:
            unload_to -- str[optional], подкаталог выгрузки файлов клиента
            send_date -- str[optional], дата отправления, default:today
    """
    def get_destination(**kw):
        root = kw.get('unload_to') or normpath('%s%s' % (config.persostation, FILETYPE_POSTONLINE_UNLOAD))
        send_date = getDate(kw.get('send_date'), config.DATE_STAMP)
        destination = normpath('%s/%s' % (root, send_date))
        return root, send_date, destination

    return changePostOnline(batches, send_date, get_destination=get_destination, **kw)

def local_GetDeliveryDate(**kw):
    """
        Рассчитать дату отгрузки с учетом выходных
    """
    package_type = kw.get('package_type')
    size = kw.get('size') or 1
    today = getToday()
    delta = 0

    is_fastfile = kw.get('is_fastfile') and True or False

    if is_fastfile:
        delta = 1
    elif kw.get('is_with_indigo'):
        delta = size < 106 and 3 or size < 421 and 4 or size < 1001 and 5 or size < 1501 and 7 or 10
    elif kw.get('is_with_loyalty'):
        delta = size < 1000 and 1 or \
            size < 5000  and (package_type == 'C1' and 2 or 3) or \
            size < 10000 and (package_type == 'C1' and 3 or 4) or \
            size < 20000 and (package_type == 'C1' and 4 or 5) or \
            size < 30000 and (package_type == 'C1' and 5 or 7) or \
            size < 50000 and  package_type == 'C1' and 8 or 10
    else:
        delta = size < 5000 and 2 or 3
    #
    #   Выходные (суббота, воскресенье)
    #
    x = 8 - daydelta(today, delta).isoweekday()
    if x < 3:
        delta += x
    #
    #   Перенос на вторник, если заказ поступил позже четверга
    #
    if not is_fastfile and daydelta(today, delta).isoweekday() == 1 and today.isoweekday() > 4:
        delta += 1

    date = daydelta(today, delta)
    #
    #   Исключить праздничные дни
    #
    d = None
    for x in calendar:
        while date.isoweekday() > 5:
            date = daydelta(date, 1)
            d = None
        if not d:
            d = getDate(date, config.DATE_STAMP)
        if x > d:
            break
        if x < d:
            continue
        date = daydelta(date, 1)
        d = None

    if config.IsCheckSuspendedDates and suspended_dates:
        delivery_companies = kw.get('delivery_companies')
        package_types = kw.get('package_types')
        if delivery_companies and package_types:
            for x, c, p in suspended_dates:
                if (not c or delivery_companies.intersection(set(c))) and (not p or package_types.intersection(set(p))):
                    d = daydelta(getDate(x, format=config.DATE_STAMP, is_date=True), -1)
                    if today < d and date >= d:
                        raise ProcessException(
                            'Date Suspended is checked: %s [local_GetDeliveryDate]!' % x, 
                            status=STATUS_ON_SUSPENDED
                            )

        if config.IsDebug:
            config.print_to(None, '%s: delivery_companies:%s, package_types:%s, date:%s' % (
                kw.get('filename'), 
                delivery_companies, 
                package_types,
                date,
                ))

    format = kw.get('format') or config.UTC_EASY_TIMESTAMP
    return getDate(date, format=format)

def local_SetDeliveryDate(node, order, saveback):
    """
        Установить дату отгрузки
    """
    delivery_date = saveback.get(LOCAL_DELIVERY_DATE)
    format = LOCAL_DATESTAMP
    
    def max_date(date1, date2):
        return getDate(date2, format=format, is_date=True) > getDate(date1, format=format, is_date=True) and date2 or date1
    
    if LOCAL_IS_MAX_DELIVERY_DATE or not delivery_date:
        size = order is not None and order.fqty
        filetype = order.filetype

        # Collect data from object
        package_type = checkSetExists(saveback, 'PackageType', node=node)
        delivery_company = checkSetExists(saveback, 'DeliveryCompany', node=node)

        new_delivery_date = local_GetDeliveryDate(size=size, format=format, 
            is_fastfile=local_IsFastFile(order),
            is_with_indigo=local_WithIndigo(order, filetype=filetype),
            is_with_loyalty=local_WithLoyalty(order),
            package_type=package_type,
            )
        saveback[LOCAL_DELIVERY_DATE] = delivery_date and max_date(delivery_date, new_delivery_date) or new_delivery_date
        delivery_date = saveback[LOCAL_DELIVERY_DATE]

    updateTag(node, 'DeliveryDate', delivery_date)
    return delivery_date

def local_SetExpireDate(node):
    """
        Обновить тег "ExpireDate" в формате на 'MMYY'
    """
    splitter = '/'
    name = 'ExpireDate'
    value = getTag(node, name)
    if not value or splitter not in value:
        return None
    x = value.split(splitter)
    if len(x) != 2:
        return None
    expire_date = '%s%s' % (x[1], x[0])
    return updateTag(node, 'ExpireDate', expire_date)

def local_PackageNumberGroups(logger, **kw):
    """
        Данные для формирования индекса партии BatchIndex
    """
    order = kw.get('order')
    connect = kw.get('connect')

    filename = order.filename

    if not (connect and callable(connect)):
        raise ProcessException('Uncallable connect [local_PackageNumberGroups]!')

    params = (filename,)

    cursor, is_error = connect(SQL['PackageNumber']['groups'], params, with_commit=False, with_result=True)

    if is_error:
        logger('--> Ошибка группировки: %s' % filename)
        return []

    return cursor

def local_GetIssueNumber(node, order, connect, logger, saveback, **kw):
    """
        Номер тиража
    """
    filetype = kw.get('filetype') or order.filetype
    plastic_type = getTag(node, 'PlasticType')

    mode = 'IssueNumber'

    if mode not in saveback:
        saveback[mode] = {}

    if plastic_type in saveback[mode]:
        return saveback[mode][plastic_type]

    params = (filetype, 'PlasticType: %s' % plastic_type,)

    cursor, is_error = connect(SQL[mode]['get'], params, with_commit=False, with_result=True, raise_error=True)

    if is_error or not cursor or len(cursor) < 1:
        x = '' #raise ProcessException('SQL Error[get], mode:%s, cursor:%s' % (mode, cursor))
    else:
        x = len(cursor[0]) > 0 and cursor[0][0] or ''

    saveback[mode][plastic_type] = x

    return x

##  ----------------------------
##  ПРИКЛАДНЫЕ НАСТРОЙКИ ДИЗАЙНА
##  ----------------------------

def local_IsCyberLab(order):
    """
        Проект "КИБЕРЛАБ"
    """
    return order.filetype == FILETYPE_POSTBANK_CYBERLAB['filetype']

def local_UpdateCyberLabNumber(node, order, connect, logger, saveback, **kw):
    """
        Проект "КИБЕРЛАБ". Генерация номера участника ФКС (RESF).

        Аргументы:
            node                -- ET.Element, узел тега текущей записи заказа, тег <FileBody_Record>
            order               -- Order, заказ
            connect             -- func, функция для работы с базой данных
            logger              -- func, функция печати журнала
            saveback            -- dict, сохраненные данные обработки на предыдущих итерациях

        Ключевые аргументы:
            filename            -- str, имя формируемого файла-заказа
            filetype            -- str, тип файла
            PAN                 -- str, PAN
    """
    orderfile = kw.get('filename') or order.filename
    filetype = kw.get('filetype') or order.filetype
    
    recno = getTag(node, 'FileRecNo')

    mode = 'CyberLabNumber'

    params = [1, orderfile, recno, kw.get('PAN'), pymssql.output(str)]

    if config.IsDeepDebug:
        config.print_to(None, '%s, params:%s' % (mode, params[:4]))

    cursor, is_error = connect(SQL[mode]['register'], params, with_commit=False, with_result=True, callproc=True, raise_error=True)

    if is_error or not cursor or len(cursor) < 4:
        raise ProcessException('SQL Error[register], mode:%s, cursor:%s' % (mode, cursor))

    # Сквозной номер участника
    x = cursor[4].split(':')
    tid, number = x[0], int(x[1] or 0)

    if config.IsDebug:
        config.print_to(None, '%s:%s, params:%s' % (mode, x, params[:4]))

    if number == 0:
        raise ProcessException('SQL Error[number over limit], mode:%s, cursor:%s' % (mode, cursor))

    return 'RESF 1%06d' % number

##  --------------------------------
##  ДОПОЛНИТЕЛЬНЫЕ НАСТРОЙКИ ДИЗАЙНА
##  --------------------------------

def local_IsFastFile(order):
    """
        Срочный заказ
    """
    return 'FAST' in order.filename

def local_IsAddrDelivery(node):
    """
        Карты с адресной доставкой (справочник не проверяется)
    """
    return getTag(node, 'DeliveryCanalCode') == 'PR01'

def local_IsNamedType(node):
    """
        Именные карты
    """
    return getTag(node, 'ProductDesign') not in FILETYPE_POSTBANK_NONAME_PRODUCTS

def local_IsDeliveryWithDate(node, delivery_company=None):
    """
        Персофайлы с контролем даты отгрузки
    """
    return (delivery_company or getTag(node, 'DeliveryCompany')) in LOCAL_DELIVERY_WITH_DATE

def local_IsDeliveryWithBarcode(node, delivery_company=None):
    """
        Персофайлы с ШПИ
    """
    return (delivery_company or getTag(node, 'DeliveryCompany')) in LOCAL_DELIVERY_WITH_BARCODE

def local_IsDeliveryWithPostOnline(node, delivery_company=None):
    """
        Персофайлы с регистрацией отправлений
    """
    return (delivery_company or getTag(node, 'DeliveryCompany')) in LOCAL_DELIVERY_WITH_POSTONLINE

def local_WithBarcode(product_design, **kw):
    """
        Признак "ШПИ"
    """
    return _get_product_param(kw.get('filetype'), product_design, 'no_barcode', default=0) == 0

def local_WithCardHolder(node):
    """
        Признак "С картходером"
    """
    return getTag(node, 'ProductDesign') in FILETYPE_POSTBANK_WITHCARDHOLDER_PRODUCTS or local_IsNamedType(node) and local_IsAddrDelivery(node)

def local_WithIndigo(order, **kw):
    """
        Индивидуальный дизайн INDIGO
    """
    words = order.filename.split('_')[4:]
    filetype = local_filetypes.get(kw.get('filetype')) or DEFAULT_FILETYPE
    plastic_types = filetype['plastic_types']

    for key in plastic_types:
        if plastic_types[key].get('indigo') and key in words:
            return True
    return False

def local_WithLoyalty(order, **kw):
    """
        Карта лояльности
    """
    return order.filetype in ('PostBank_X5',)

def local_CaseCover(node):
    """
        Признак "Конверт ОВПО"
    """
    return getTag(node, 'ProductDesign') in FILETYPE_POSTBANK_CASECOVER_PRODUCTS

def local_WithEnclosure(product_design, **kw):
    """
        Использовать "Вложение"
    """
    return product_design in FILETYPE_POSTBANK_GREENWORLD_PRODUCTS and kw.get('is_named_type') and 'GREENWORLD' or ''

def local_PlasticFrontPrintType(product_design, **kw):
    """
        Тип печати ЛИЦО
    """
    return _get_product_param(kw.get('filetype'), product_design, 'front_print') or 'EMBOSSING'

def local_PlasticBackPrintType(product_design, **kw):
    """
        Тип печати ОБОРОТ
    """
    return _get_product_param(kw.get('filetype'), product_design, 'back_print') or 'INDENT'

def local_CaseEnvelope(product_design, **kw):
    """
        Конверт к листовке
    """
    return _get_product_param(kw.get('filetype'), product_design, 'envelope')

def local_CaseLeaflet(product_design, **kw):
    """
        Бланк листовки
    """
    return _get_product_param(kw.get('filetype'), product_design, 'leaflet')

def local_CheckDesignIsInvalid(product_design, **kw):
    """
        Дополнительный входной контроль параметров дизайна
    """
    if product_design in ('220077012',) and not kw.get('is_named_type'):
        raise ProcessException('Invalid Design:[%s]' % product_design)
