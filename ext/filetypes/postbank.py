# -*- coding: cp1251 -*-

# ---------------------- #
#   postbank filetypes   #
# ---------------------- #

__all__ = [
    'LOCAL_IS_CHANGE_EXPIREDATE', 'LOCAL_IS_PLASTIC_BATCHSORT', 'LOCAL_IS_PACKAGE_BATCHSORT', 'LOCAL_DATESTAMP', 'LOCAL_ID_TAG', 
    'LOCAL_EASY_TIMESTAMP', 'LOCAL_FILE_DELIVERY_SPLITTER', 'LOCAL_DELIVERY_DATE', 
    'DEFAULT_DELIVERY_TYPE', 'DEFAULT_MERGE_INTERVAL', 'DEFAULT_EOL', 'DEFAULT_FILETYPE', 'FILETYPE_FOLDER', 
    'FILETYPE_POSTBANK_V1', 'FILETYPE_POSTBANK_ID', 'FILETYPE_POSTBANK_IDM', 'FILETYPE_POSTBANK_X5', 'FILETYPE_POSTBANK_LOYALTY', 'FILETYPE_POSTBANK_REFERENCE', 
    'CLIENT_NAME', 'SQL', 'REF_INDEX', 'REF_ENCODE_COLUMNS', 'ERROR_RECIPIENTS', 
    'local_GetPostBarcode', 'local_GetDeliveryCompany', 'local_GetErrorCode', 'local_GetPlasticInfo', 'local_GetPlasticSPrefix', 'local_GetDeliveryDate', 
    'local_GetPackageSize', 'local_GetPackageWeight', 'local_GetCardGroup', 'local_GetPackageType', 'local_GetMergePostfix', 'local_GetAREPRecordName', 
    'local_ParseAddress', 'local_SetDeliveryDate', 'local_SetExpireDate', 'local_UpdateStampCode', 'local_RegisterPostOnline', 'local_ChangePostOnline', 
    'local_IsFastFile', 'local_IsAddrDelivery', 'local_IsNamedType', 'local_WithCardHolder', 'local_WithIndigo', 'local_WithLoyalty', 
    'local_PackageNumberGroups', 
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
#

from copy import deepcopy

import os
import pymssql

import config
"""
from config import (
     IsPrintExceptions,
     UTC_EASY_TIMESTAMP, DATE_STAMP,
     print_exception,
     postonline
)
"""
from app.core import ProcessException, AbstractIncomingLoaderClass, AbstractReferenceLoaderClass
from app.types import *
from app.barcodes import Code128Barcode, I25Barcode, EAN13Barcode
from app.mails import send_mail_with_attachment
from app.srvlib import makeFileTypeIndex, SRV_GetValue
from app.utils import normpath, check_folder_exists, getDate, getToday, daydelta, isIterable

from ..defaults import *
from ..postonline import registerPostOnline, changePostOnline
from ..xmllib import *

from ext import calendar

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
    '40599111:40599112:40599113:40599114:40599115:40599122:' \
    '40599211:40599216:40599217:40599218:40599219:40599220:40599222:' \
    '220077014:220077044:220077045:22007704A:'

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
        'N'   : 1,
        'NC'  : 2,
        'NCA' : 3,
        'I'   : 4,
        'IC'  : 5,
        'IA'  : 6,
        'ICA' : 7,
    },
}

##  -------------------------------
##  НЕИМЕННЫЕ И ИМЕННЫЕ КАРТЫ БАНКА
##  -------------------------------

FILETYPE_POSTBANK_V1 = deepcopy(FILETYPE_POSTBANK_TEMPLATE)

FILETYPE_POSTBANK_V1.update({
    'tytle'           : '%s входящий файл заказа PostBank_v1 версия 1' % CLIENT_NAME[0],
    'filetype'        : 'PostBank_v1',
    # ------------------------------
    # Параметры банковских продуктов
    # ------------------------------
    #   product     -- PlasticType: {VP01|VP02|VP03|VP04|VP09|VP10|VP11|VP12|VP14}
    #   scode       -- ServiceCode (MSDP)
    #   pvki        -- PVKI (MSDP)
    #   d-prefix    -- префикс баркода карты (Префикс для ШК EAN-13)
    #   s-prefix    -- префикс баркода упаковки по транспортным компаниям: (без адресной доставки, с адресной доставкой)
    #   pay_system  -- PAY_SYSTEM (SDC)
    #   name        -- наименование пластика
    #
    'plastic_types'   : {
        '40599112'    : {
            'product'    : 'VP03', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '516',
            's-prefix'   : {
                'D'         : ('RAL', 'ROL'),
                'default'   : ('RPN', 'ROL'),
                'S'         : ('RSN', 'ROL'),
            },
            'pay_system' : 'KONA_2320',
            'name'       : 'Visa Platinum PayWave Eagle',
        },
        '40599113'    : {
            'product'    : 'VP01', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '516',
            's-prefix'   : {
                'D'         : ('RAL', 'ROL'),
                'default'   : ('RPN', 'ROL'),
                'S'         : ('RSN', 'ROL'),
            },
            'pay_system' : 'KONA_2320',
            'name'       : 'Visa Platinum PayWave Cosmos',
        },
        '40599114'    : {
            'product'    : 'VP04', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '516',
            's-prefix'   : {
                'D'         : ('RAL', 'ROL'),
                'default'   : ('RPN', 'ROL'),
                'S'         : ('RSN', 'ROL'),
            },
            'pay_system' : 'KONA_2320',
            'name'       : 'Visa Platinum PayWave Green World',
        },
        '40599115'    : {
            'product'    : 'VP02', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '516',
            's-prefix'   : {
                'D'         : ('RLB', 'RLB'),
                'default'   : ('RPR', 'RPR'),
                'S'         : ('RSR', 'RSR'),
            },
            'pay_system' : 'KONA_2320',
            'name'       : 'Visa Platinum PayWave Cosmos NoName',
        },
        '40599216'    : {
            'product'    : 'VP14', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '416',
            's-prefix'   : {
                'D'         : ('RLB', 'RLB'),
                'default'   : ('RPR', 'RPR'),
                'S'         : ('RSR', 'RSR'),
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
                'S'         : ('RSN', 'ROL'),
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
                'D'         : ('RLB', 'RLB'),
                'default'   : ('RPR', 'RPR'),
                'S'         : ('RSR', 'RSR'),
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
                'D'         : ('RLB', 'RLB'),
                'default'   : ('RPR', 'RPR'),
                'S'         : ('RSR', 'RSR'),
            },
            'pay_system' : 'LongRSA',
            'name'       : 'Visa MARKI Blue NoName',
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
    #   product     -- PlasticType: {VP05|VP06|VP13}
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
                'S'         : ('RSN', 'ROL'),
            },
            'pay_system' : 'KONA_2320',
            'name'       : 'Visa Platinum Individual',
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
                'S'         : ('RSN', 'ROL'),
            },
            'pay_system' : 'LongRSA',
            'name'       : 'Visa Classic Individual',
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
                'S'         : ('RSN', 'ROL'),
            },
            'pay_system' : 'KONA_2320',
            'name'       : 'Visa REWARDS Individual',
            'indigo'     : 1,
        },
        '40599222'    : {
            'product'    : 'VP17', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : '416',
            's-prefix'   : {
                'D'         : ('RAL', 'ROL'),
                'default'   : ('RPN', 'ROL'),
                'S'         : ('RSN', 'ROL'),
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
            },
            'pay_system' : 'KONA_2320_NSPK',
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
                'S'         : ('RSR', 'RSR'),
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
                'S'         : ('531', '531'),
            },
            'pay_system' : 'KONA_2320_X5',
            'name'       : 'Mir X5 Dual PR',
        },
    'plastic_types'   : {
        '22007704A'   : {
            'product'    : 'VP16', 
            'scode'      : '201', 
            'pvki'       : '1', 
            'd-prefix'   : 'XXX',
            's-prefix'   : {
                'D'         : ('RAL', 'ROL'),
                'default'   : ('RPN', 'ROL'),
                'S'         : ('RSN', 'ROL'),
            },
            'pay_system' : 'KONA_2320_X5',
            'name'       : 'Mir X5 Dual Name',
        },
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
}

REF_INDEX = makeFileTypeIndex(FILETYPE_POSTBANK_REFERENCE)

REF_ENCODE_COLUMNS = (1,4,5,6,7,8,9,10,11)

DEFAULT_FILETYPE = FILETYPE_POSTBANK_V1

local_filetypes = {
    FILETYPE_POSTBANK_V1['filetype'] : FILETYPE_POSTBANK_V1,
    FILETYPE_POSTBANK_ID['filetype'] : FILETYPE_POSTBANK_ID,
    FILETYPE_POSTBANK_IDM['filetype'] : FILETYPE_POSTBANK_IDM,
    FILETYPE_POSTBANK_X5['filetype'] : FILETYPE_POSTBANK_X5,
}

# ========================= #

def local_GetErrorCode(keys, key, code=None):
    """
        Код ошибки в квитанциях
    """
    return key in keys and '%02d' % (keys.index(key)+1) or code or '00'

def local_GetDeliveryCompany(value):
    """
        Условное обозначение транспортной компании
    """
    return value == 'СПСР' and 'S' or value =='DHL' and 'D' or 'P'

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

def local_GetPlasticInfo(product, **kw):
    """
        Информация о продукте.
        
        Аргументы:
            product  -- str, символьный код продукта '405991XX'
        
        Ключевые аргументы:
            filetype -- dict, дескриптор типа файла
            key      -- str, идентификатор параметра (keys)

        Возврат:
            list, [<код продукта>, <сервис-код MSDP>, <PVKI>, <префикс дизайна>, <тип чипа>, <name>].
    """
    keys = ('product', 'scode', 'pvki', 'd-prefix', 'pay_system', 'name',)
    filetype = local_filetypes.get(kw.get('filetype')) or DEFAULT_FILETYPE
    value = filetype['plastic_types'].get(product)

    if not value:
        return (None,)*6

    key = kw.get('key')
    if key:
        return value and key and value.get(key) or None
    return [value and value.get(x) for x in keys]

def local_GetPlasticSPrefix(product_design, delivery_type, **kw):
    """
        Префикс для пломб.
        
        Аргументы:
            product_design -- str, символьный код продукта '405991XX'
            delivery_type  -- str, тип доставки (транспортная компания) {EMS|DHL|...}
        
        Ключевые аргументы:
            filetype       -- dict, дескриптор типа файла
            index          -- int, {0|1} 1:адресная доставка

        Возврат:
            str, префикс для пломбы: {ROL|RAL|...}, XXX - значение не определено.
    """
    key = 's-prefix'
    filetype = local_filetypes.get(kw.get('filetype')) or DEFAULT_FILETYPE
    index = kw.get('index') or 0
    item = filetype['plastic_types'].get(product_design)

    if not (item and isinstance(item, dict) and key in item):
        raise ProcessException('Unexpected Error[PlasticSPrefix], product_design:%s' % product_design)

    item = item[key]
    delivery_company = local_GetDeliveryCompany(delivery_type)
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
    # Способ доставки (транспортная компания)
    delivery_company = local_GetDeliveryCompany(getTag(node, 'DeliveryType'))
    # Кол-во карт в заказе
    size = order.fqty
    if card_type in ('ICA','IA') and package_type in ('C2','C3'):
        s, p = 1, 1
    elif card_type.startswith('N') and package_type == 'C2':
        if delivery_company == 'D':
            s, p = 20, 10
        elif delivery_company == 'S':
            s, p = 20, 10
        else:
            s, p = 20, 1
    else:
        if delivery_company == 'D':
            s, p = 10, size <= 200 and 20 or 50
        elif delivery_company == 'S':
            s, p = 10, size <= 50 and 5 or size <= 100 and 10 or size <= 500 and 50 or 50 # 70 !
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
            filetype -- dict, дескриптор типа файла
    """
    filetype = local_filetypes.get(kw.get('filetype')) or DEFAULT_FILETYPE
    return filetype['card_groups'].get(key) or 9

def local_GetMergePostfix(**kw):
    filetype = local_filetypes.get(kw.get('filetype')) or DEFAULT_FILETYPE
    return filetype.get('postfix') or ''

def local_GetAREPRecordName(order):
    return local_WithLoyalty(order) and 'RecordX5'

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
    items = ['index', 'region', 'district', 'city', 'town', 'street', 'house', 'building', 'flat']
    x = getTag(node, key).split(',')
    return dict(zip(items, x))

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

        Возврат:
            str, stamp_code     -- номер пломбы
            str, stamp_index    -- последние 4 цифры PAN первой карты в упаковке
            str, package_code   -- код транспортной упаковки
            str, post_code      -- ШПИ (опционально)
    """
    orderfile = kw.get('filename') or order.filename
    filetype = kw.get('filetype') or order.filetype
    
    recno = getTag(node, 'FileRecNo')
    product_design = getTag(node, 'ProductDesign')
    card_type = getTag(node, 'CardType')
    package_type = getTag(node, 'PackageType')

    delivery_type = getTag(node, 'DeliveryType')
    PAN4 = getTag(node, 'PAN')[-4:]
    is_addr_delivery = getBooleanTag(node, 'IsAddrDelivery')

    # Префикс для пломб
    index = is_addr_delivery and 1 or 0
    stamp_prefix = local_GetPlasticSPrefix(product_design, delivery_type, index=index, filetype=filetype)

    mode = 'StampNumber'
    """
    # Для именных карт с адресной доставкой пломба не формируется (!!!)
    if card_type in ('ICA', 'IA') and package_type in ('C2','C3'):
        mode = 'PostCode'
    """

    package_type = local_GetPackageType(node)
    stamp_limit, package_limit = local_GetPackageSize(node, order)
    params = [1, orderfile, package_type, recno, PAN4, stamp_limit, package_limit, pymssql.output(str)]

    cursor, is_error = connect(SQL[mode]['register'], params, with_commit=False, with_result=True, callproc=True)

    if is_error or not cursor or len(cursor) < 7:
        raise ProcessException('SQL Error[register], mode:%s, cursor:%s' % (mode, cursor))

    # Сквозной номер упаковки
    x = cursor[7].split(':')
    stamp_number, stamp_index, package_number, post_code = int(x[0] or 0), x[1], int(x[2] or 0), x[3]

    if config.IsDebug:
        config.print_to(None, '%s:%s, params:%s' % (mode, x, params[:6]))

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

    if kw.get('is_fastfile'):
        delta = 1
    elif kw.get('is_with_indigo'):
        delta = size < 106 and 4 or size < 421 and 5 or 10
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
    if daydelta(today, delta).isoweekday() == 1 and today.isoweekday() > 4:
        delta += 1

    date = daydelta(today, delta)
    #
    #   Исключить праздничные дни
    #
    d = None
    for x in calendar:
        if not d:
            d = getDate(date, config.DATE_STAMP)
        if x > d:
            break
        if x < d:
            continue
        date = daydelta(date, 1)
        d = None

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
        new_delivery_date = local_GetDeliveryDate(size=size, format=format, 
            is_fast=local_IsFastFile(order),
            is_with_indigo=local_WithIndigo(order, filetype=filetype),
            is_with_loyalty=local_WithLoyalty(order),
            package_type=getTag(node, 'PackageType')
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
    return getTag(node, 'ProductDesign') not in ('40599115', '40599216', '40599219', '40599220', '220077044', '220077045',)

def local_WithCardHolder(node):
    """
        Признак "С картходером"
    """
    return getTag(node, 'ProductDesign') in ('220077045',) or local_IsNamedType(node) and local_IsAddrDelivery(node)

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
    return order.filetype in ('PostBank_X5',) and True or False

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
