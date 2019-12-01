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
#   ���� ���������:
#   ---------------
#   20190325: ��� ����� FILETYPE_POSTBANK_ID
#   20190322: ��������� �� 'plastic_types': 40599111, 40599211
#   20190222: ����������� �������� local_GetPackageType, �������� 6-� ���� 'plastic_type'
#   20190524: ����-������ � �������� ���������� FILETYPE_POSTBANK_LOYALTY
#   20190527: ��� ����� "���������" FILETYPE_POSTBANK_X5
#   20190701: ��������� Visa MARKI Red/Blue: 40599217-40599220
#   20190709: ��������� �� 'plastic_types' Visa REWARDS Individual: 40599122
#   20190926: ��������� �� 'plastic_types' Mir Privilege Individual: 22007701
#   20191112: ��������� ��� 22007704A ����� ���������� ������� "���������" (�������)
#   20191112: ��������� �� Visa Rewards Marki Individual: 40599222
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

# ����� ������� ���� YY/MM -> MMYY
LOCAL_IS_CHANGE_EXPIREDATE = False
# ���������� �� ���� ��������
LOCAL_IS_PLASTIC_BATCHSORT = False
# ���������� �� ���� ��������
LOCAL_IS_PACKAGE_BATCHSORT = True
# ���������� ������������ ���� ��������
LOCAL_IS_MAX_DELIVERY_DATE = True
# ��� ID ������
LOCAL_ID_TAG = 'ID'
# ������ ���� �������� � �������
LOCAL_DATESTAMP = '%d.%m.%Y'
# ������ ���� � ������ ��������
LOCAL_EASY_TIMESTAMP = '%Y%m%d_%H%M'
# ����������� ����� �������� � ����� �����
LOCAL_FILE_DELIVERY_SPLITTER = '$'
# ���� ���� ��������
LOCAL_DELIVERY_DATE = 'LOCAL_DELIVERY_DATE'

##  --------
##  DEFAULTS
##  --------

# ������ �������� �� ���������
DEFAULT_DELIVERY_TYPE = '����� 1 �����'
# ��������� �������� ��� ������ �������� �����������
DEFAULT_MERGE_INTERVAL = ('15:00', '16:15')
# ������ ����� ������ � ������-����������
DEFAULT_EOL = '\r\n'

##  -----------
##  DESCRIPTORS
##  -----------

# ������������ �����: ������ ������������, ClientIDStr (BankPerso), ������� ������������
CLIENT_NAME = ('��� ������ ���ʻ', '���������', '����� ����',)
# �������� ������� ������� ���������� � ������
FILETYPE_FOLDER = 'PostBank'
# ������� �������� ������� �������� ����� ������ (relative)
FILETYPE_POSTONLINE_UNLOAD = '/Inkass/InputData/PostBank/postonline'
# ���������� �������� ����������� �� �������
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
                <comment>       -- str, �������� ����

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
    # ������ ������� ������
    # ---------------------
    'fieldset'        : {
        'ID'                    : ('001', None, None, DATA_TYPE_INTEGER, None, None, (4, 20), 1, 'ID ����� � ������� Octopus'),
        'PID'                   : ('002', None, None, DATA_TYPE_INTEGER, None, None, (9,), 1, '��� �������'),
        'PAN'                   : ('003', None, None, DATA_TYPE_TEXT_NS, DATA_PERSO_TYPE_PANWIDE16, None, (19,), 1, '����� ����� (� ������� NNNN NNNN NNNN NNNN)'),
        'ExpireDate'            : ('004', 'ExpiryDate', None, DATA_TYPE_TEXT_NS, DATA_PERSO_TYPE_EXPIREDATE, None, (5,), 1, '���� ��������� �������� ����� (������ mm/yy)'),
        'CardholderName'        : ('005', 'Cardholder', None, DATA_TYPE_TEXT_ANS, DATA_PERSO_TYPE_EMBOSSNAME, None, (2, 26), 0, '��� � ������� ��������� �����'),
        'Track1CardholderName'  : ('006', 'CH_Name_Track1', None, DATA_TYPE_TEXT_ANS, DATA_PERSO_TYPE_EMBOSSNAME, None, (2, 26), 1, '��� ��������� ����� �� ������ ����� ��������� ������'),
        'Organization'          : ('007', None, None, DATA_TYPE_TEXT_ANC, None, None, (2, 26), 0, '������ ��� �������������� 4-� ������ �� ������� ������� �����'),
        'ProductDesign'         : ('008', None, None, DATA_TYPE_TEXT_AN, FILETYPE_POSTBANK_PRODUCT_DESIGNS, None, (1, 24), 1, '��� ������� ��������'),
        'BRANCHDELIVERY'        : ('009', None, None, DATA_TYPE_TEXT_NS, None, None, (0, 11), 0, '��� ������� �������� ����'),
        'BRANCH_SEND_TO'        : ('010', None, None, DATA_TYPE_TEXT_NS, None, None, (0, 11), 0, '��� ������� �������� ����'),
        'PSN'                   : ('011', None, None, DATA_TYPE_INTEGER, '0:1:90:91', None, (1, 2), 1, '�������� PAN Sequence Number'),
        'DeliveryCanalCode'     : ('012', None, None, DATA_TYPE_TEXT_AN, ('0', 'PR01'), None, (1, 4), 1, '����� ������� ����� �� ����� �������'),
        'CardholderFIO'         : ('013', None, None, DATA_TYPE_TEXT, None, ENCODING_UNICODE, (1, 250), 0, '��� �������'),
        'CardholderAddress'     : ('014', None, None, DATA_TYPE_TEXT, None, ENCODING_UNICODE, (1, 200), 0, '�������� ����� ��� �������� ����� �������'),
        'ImageName'             : ('015', 'PictureID', None, DATA_TYPE_TEXT_ANC, None, None, (0, 50), 0, '��� ��������'),
    },
    # ------------------------
    # ������� ����������� ����
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
##  ��������� � ������� ����� �����
##  -------------------------------

FILETYPE_POSTBANK_V1 = deepcopy(FILETYPE_POSTBANK_TEMPLATE)

FILETYPE_POSTBANK_V1.update({
    'tytle'           : '%s �������� ���� ������ PostBank_v1 ������ 1' % CLIENT_NAME[0],
    'filetype'        : 'PostBank_v1',
    # ------------------------------
    # ��������� ���������� ���������
    # ------------------------------
    #   product     -- PlasticType: {VP01|VP02|VP03|VP04|VP09|VP10|VP11|VP12|VP14}
    #   scode       -- ServiceCode (MSDP)
    #   pvki        -- PVKI (MSDP)
    #   d-prefix    -- ������� ������� ����� (������� ��� �� EAN-13)
    #   s-prefix    -- ������� ������� �������� �� ������������ ���������: (��� �������� ��������, � �������� ���������)
    #   pay_system  -- PAY_SYSTEM (SDC)
    #   name        -- ������������ ��������
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
##  �������������� ������
##  ---------------------

FILETYPE_POSTBANK_ID = deepcopy(FILETYPE_POSTBANK_TEMPLATE)

FILETYPE_POSTBANK_ID.update({
    'tytle'           : '%s �������� ���� ������ PostBank_ID �������������� ������' % CLIENT_NAME[0],
    'filetype'        : 'PostBank_ID',
    # ------------------------------
    # ��������� ���������� ���������
    # ------------------------------
    #   product     -- PlasticType: {VP05|VP06|VP13}
    #   scode       -- ServiceCode (MSDP)
    #   pvki        -- PVKI (MSDP)
    #   d-prefix    -- ������� ������� �����
    #   s-prefix    -- ������� ������� �������� �� ������������ ���������: (��� �������� ��������, � �������� ���������)
    #   pay_system  -- PAY_SYSTEM (SDC)
    #   name        -- ������������ ��������
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
##  �������������� ������ ���
##  -------------------------

FILETYPE_POSTBANK_IDM = deepcopy(FILETYPE_POSTBANK_TEMPLATE)

FILETYPE_POSTBANK_IDM.update({
    'tytle'           : '%s �������� ���� ������ PostBank_IDM �������������� ������' % CLIENT_NAME[0],
    'filetype'        : 'PostBank_IDM',
    # ------------------------------
    # ��������� ���������� ���������
    # ------------------------------
    #   product     -- PlasticType: {VP15}
    #   scode       -- ServiceCode (MSDP)
    #   pvki        -- PVKI (MSDP)
    #   d-prefix    -- ������� ������� �����
    #   s-prefix    -- ������� ������� �������� �� ������������ ���������: (��� �������� ��������, � �������� ���������)
    #   pay_system  -- PAY_SYSTEM (SDC)
    #   name        -- ������������ ��������
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
##  ������ ��Ҩ�����
##  ----------------

FILETYPE_POSTBANK_X5 = deepcopy(FILETYPE_POSTBANK_TEMPLATE)

FILETYPE_POSTBANK_X5.update({
    'tytle'           : '%s �������� ���� ������ PostBank_X5 ��������' % CLIENT_NAME[0],
    'filetype'        : 'PostBank_X5',
    'postfix'         : '_X5',
    # ------------------------------
    # ��������� ���������� ���������
    # ------------------------------
    #   product     -- PlasticType: {VP07|VP08|VP16}
    #   scode       -- ServiceCode (MSDP)
    #   pvki        -- PVKI (MSDP)
    #   d-prefix    -- ������� ������� �����
    #   s-prefix    -- ������� ������� �������� �� ������������ ���������: (��� �������� ��������, � �������� ���������)
    #   pay_system  -- PAY_SYSTEM (SDC)
    #   name        -- ������������ ��������
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
##  ����-������ � �������� ����������
##  ---------------------------------

FILETYPE_POSTBANK_LOYALTY = {
    'class'           : AbstractReferenceLoaderClass,
    'object_type'     : FILE_TYPE_INCOMING_LOYALTY,
    'tytle'           : '����� ���� �������� ����-������ � �������� ����������',
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
    # ������ ������� ������
    # ---------------------
    'fieldset'        : {
        'LoyaltyNumber'     : ('001', None, None, DATA_TYPE_TEXT_N, None, None, (16,), 1, '�������� ����� ����� (����� ����������)'),
        'EAN'               : ('002', None, None, DATA_TYPE_TEXT_N, None, None, (13,), 1, '����� ��� ������������ �� EAN-13'),
    },
}

##  -------------------
##  ���������� ��������
##  -------------------

FILETYPE_POSTBANK_REFERENCE = {
    'class'           : AbstractReferenceLoaderClass,
    'object_type'     : FILE_TYPE_INCOMING_REFERENCE,
    'tytle'           : '����� ���� �������� �������������� ����',
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
    # ������ ������� ������
    # ---------------------
    'fieldset'        : {
        'CompanyName'       : ('001', None, None, DATA_TYPE_TEXT, None, None, (1, 250), 1, '������������ �������������'),
        'BranchDelivery'    : ('002', None, None, DATA_TYPE_INTEGER, None, None, (1, 11), 1, '��� �������� ���������'),
        'BranchSendTo'      : ('003', None, None, DATA_TYPE_INTEGER, None, None, (1, 11), 1, '��� ������� �������� ����'),
        'NonamedPostType'   : ('004', None, None, DATA_TYPE_TEXT, ['DHL', '����', '����� 1 �����', 'EMS'], None, (1, 20), 1, '������ �������� ��������� ����'),
        'NamedPostType'     : ('005', None, None, DATA_TYPE_TEXT, ['DHL', '����', '����� 1 �����', 'EMS'], None, (1, 20), 1, '������ �������� ������� ����'),
        'Receiver'          : ('006', None, None, DATA_TYPE_TEXT, None, None, (1, 250), 0, '�����������-����������'),
        'Address'           : ('007', None, None, DATA_TYPE_TEXT, None, None, (1, 4000), 0, '�����'),
        'NonamedContact'    : ('008', None, None, DATA_TYPE_TEXT, None, None, (1, 250), 0, '������� ���������� (��������� �����)'),
        'NamedContact'      : ('009', None, None, DATA_TYPE_TEXT, None, None, (1, 250), 0, '������� ���������� (������� �����)'),
        'NonamedPhone'      : ('010', None, None, DATA_TYPE_TEXT, None, None, (1, 50), 0, '������� (���������)'),
        'NamedPhone'        : ('011', None, None, DATA_TYPE_TEXT, None, None, (1, 50), 0, '������� (�������)'),
        'Zone'              : ('012', None, None, DATA_TYPE_INTEGER, '1:2:3:4:5', None, (1,), 0, '�������� ����'),
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
        ��� ������ � ����������
    """
    return key in keys and '%02d' % (keys.index(key)+1) or code or '00'

def local_GetDeliveryCompany(value):
    """
        �������� ����������� ������������ ��������
    """
    return value == '����' and 'S' or value =='DHL' and 'D' or 'P'

def local_GetPostBarcode(value, code=None):
    """
        ��� ��� (Code128, Interleaved 2 of 5).

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
        ���������� � ��������.
        
        ���������:
            product  -- str, ���������� ��� �������� '405991XX'
        
        �������� ���������:
            filetype -- dict, ���������� ���� �����
            key      -- str, ������������� ��������� (keys)

        �������:
            list, [<��� ��������>, <������-��� MSDP>, <PVKI>, <������� �������>, <��� ����>, <name>].
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
        ������� ��� �����.
        
        ���������:
            product_design -- str, ���������� ��� �������� '405991XX'
            delivery_type  -- str, ��� �������� (������������ ��������) {EMS|DHL|...}
        
        �������� ���������:
            filetype       -- dict, ���������� ���� �����
            index          -- int, {0|1} 1:�������� ��������

        �������:
            str, ������� ��� ������: {ROL|RAL|...}, XXX - �������� �� ����������.
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
        ��� ������������� ������ (� SQL-��������)
    """
    # ��� ���� {I|N}{C}{A}
    card_type = getTag(node, 'CardType')
    # ��� �������� (VPXX)
    plastic_type = getTag(node, 'PlasticType')
    # ��� �������� (����1, ����2)
    package_type = getTag(node, 'PackageType')
    # ������ �������� (������������ ��������)
    delivery_company = local_GetDeliveryCompany(getTag(node, 'DeliveryType'))
    # ��� �������� ���������
    branch_delivery = getTag(node, 'BRANCHDELIVERY')
    # ��� ������� �������� ����
    branch_send_to = getTag(node, 'BRANCH_SEND_TO')
    return '%s:%s:%s:%s||%s:%s' % (delivery_company, branch_send_to, branch_delivery, package_type, card_type, plastic_type)

def local_GetPackageSize(node, order):
    """
        ����� ������ �� ���������� ����.
        
        �������:
            s, int -- ������������ ���-�� ���� � �������� 1-�� ������ (������ ������|��������)
            p, int -- ������������ ���-�� �����|���� � ������������ ��������
    """
    # ��� ����
    card_type = getTag(node, 'CardType')
    # ��� �������� (����1, ����2)
    package_type = getTag(node, 'PackageType')
    # ������ �������� (������������ ��������)
    delivery_company = local_GetDeliveryCompany(getTag(node, 'DeliveryType'))
    # ���-�� ���� � ������
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
        ��� ��������� �����������.

        ���������:
            ptype -- ��� �������� CASE_BOX: C1|C2-BOX|C2-LETTER|C3-LETTER
            cards -- ���-�� ���� � �����������
            s     -- ������������ ���-�� ���� � �������� 1-�� ������, default:10
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
        ������ ���� � ����������
        
        �������� ���������:
            filetype -- dict, ���������� ���� �����
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
        ����� ��������
        
        ��������� ������ � �����������:
        
        1 - ������;
        2 - ��� �������;
        3 - ������;
        4 - ��� ������;
        5 - �����;
        6 - ��� ������;
        7 - �����;
        8 - ��� ���������� ������;
        9 - ��������� �����;
        10 - ��� �����;
        11 - �����;
        12 - ����� ����;
        13 - ������;
        14 - ��������;
        15 - ��������;
        16 - ����� �����.
    """
    items = ['index', 'region', 'district', 'city', 'town', 'street', 'house', 'building', 'flat']
    x = getTag(node, key).split(',')
    return dict(zip(items, x))

def local_UpdateStampCode(node, order, connect, logger, saveback, **kw):
    """
        ��������� ������ ������ � ������������ ��������.

        ���������:
            node                -- ET.Element, ���� ���� ������� ������ ������, ��� <FileBody_Record>
            order               -- Order, �����
            connect             -- func, ������� ��� ������ � ����� ������
            logger              -- func, ������� ������ �������
            saveback            -- dict, ����������� ������ ��������� �� ���������� ���������

        �������� ���������:
            filename            -- str, ��� ������������ �����-������

        �������:
            str, stamp_code     -- ����� ������
            str, stamp_index    -- ��������� 4 ����� PAN ������ ����� � ��������
            str, package_code   -- ��� ������������ ��������
            str, post_code      -- ��� (�����������)
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

    # ������� ��� �����
    index = is_addr_delivery and 1 or 0
    stamp_prefix = local_GetPlasticSPrefix(product_design, delivery_type, index=index, filetype=filetype)

    mode = 'StampNumber'
    """
    # ��� ������� ���� � �������� ��������� ������ �� ����������� (!!!)
    if card_type in ('ICA', 'IA') and package_type in ('C2','C3'):
        mode = 'PostCode'
    """

    package_type = local_GetPackageType(node)
    stamp_limit, package_limit = local_GetPackageSize(node, order)
    params = [1, orderfile, package_type, recno, PAN4, stamp_limit, package_limit, pymssql.output(str)]

    cursor, is_error = connect(SQL[mode]['register'], params, with_commit=False, with_result=True, callproc=True)

    if is_error or not cursor or len(cursor) < 7:
        raise ProcessException('SQL Error[register], mode:%s, cursor:%s' % (mode, cursor))

    # �������� ����� ��������
    x = cursor[7].split(':')
    stamp_number, stamp_index, package_number, post_code = int(x[0] or 0), x[1], int(x[2] or 0), x[3]

    if config.IsDebug:
        config.print_to(None, '%s:%s, params:%s' % (mode, x, params[:6]))

    # --------------------
    # ����� ������ [an 10]
    # --------------------

    stamp_code = ''
    if mode == 'StampNumber':
        stamp_code = '%3s%07d' % (stamp_prefix, stamp_number)
    updateTag(node, 'StampCode', stamp_code)

    # --------------------------------
    # ����-����� ������������ ��������
    # --------------------------------

    package_code = ''
    if mode:
        x = getTag(node, 'DeliveryDate').split('.')
        delivery_date = '%s%s%s' % (x[0], x[1], x[2][-2:])

        package_code = '%1d%6s%05d' % (
            delivery_type == 'DHL' and 1 or delivery_type == '����' and 2 or 0,
            delivery_date,
            package_number or int(recno)
        )
    updateTag(node, 'PackageCode', package_code)

    return stamp_code, stamp_index, package_code, post_code

def local_RegisterPostOnline(mode, case, ids, **kw):
    """
        ������-����������� ����������� �� ������� ����� ������.

        ��. postonline.registerPostOnline

        �������� ���������:
            unload_to -- str[optional], ���������� �������� ������ �������
            send_date -- str[optional], ���� �����������, default:today
    """
    def get_destination(**kw):
        root = kw.get('unload_to') or normpath('%s%s' % (config.persostation, FILETYPE_POSTONLINE_UNLOAD))
        send_date = kw.get('send_date') or getDate(getToday(), config.DATE_STAMP)
        destination = normpath('%s/%s' % (root, send_date))
        return root, send_date, destination

    return registerPostOnline(mode, case, ids, get_destination=get_destination, **kw)

def local_ChangePostOnline(batches, send_date, **kw):
    """
        ��������������� ����������� �� ������� ����� ������.

        ��. postonline.registerPostOnline

        �������� ���������:
            unload_to -- str[optional], ���������� �������� ������ �������
            send_date -- str[optional], ���� �����������, default:today
    """
    def get_destination(**kw):
        root = kw.get('unload_to') or normpath('%s%s' % (config.persostation, FILETYPE_POSTONLINE_UNLOAD))
        send_date = getDate(kw.get('send_date'), config.DATE_STAMP)
        destination = normpath('%s/%s' % (root, send_date))
        return root, send_date, destination

    return changePostOnline(batches, send_date, get_destination=get_destination, **kw)

def local_GetDeliveryDate(**kw):
    """
        ���������� ���� �������� � ������ ��������
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
    #   �������� (�������, �����������)
    #
    x = 8 - daydelta(today, delta).isoweekday()
    if x < 3:
        delta += x
    #
    #   ������� �� �������, ���� ����� �������� ����� ��������
    #
    if daydelta(today, delta).isoweekday() == 1 and today.isoweekday() > 4:
        delta += 1

    date = daydelta(today, delta)
    #
    #   ��������� ����������� ���
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
        ���������� ���� ��������
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
        �������� ��� "ExpireDate" � ������� �� 'MMYY'
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
        ������� �����
    """
    return 'FAST' in order.filename

def local_IsAddrDelivery(node):
    """
        ����� � �������� ��������� (���������� �� �����������)
    """
    return getTag(node, 'DeliveryCanalCode') == 'PR01'

def local_IsNamedType(node):
    """
        ������� �����
    """
    return getTag(node, 'ProductDesign') not in ('40599115', '40599216', '40599219', '40599220', '220077044', '220077045',)

def local_WithCardHolder(node):
    """
        ������� "� �����������"
    """
    return getTag(node, 'ProductDesign') in ('220077045',) or local_IsNamedType(node) and local_IsAddrDelivery(node)

def local_WithIndigo(order, **kw):
    """
        �������������� ������ INDIGO
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
        ����� ����������
    """
    return order.filetype in ('PostBank_X5',) and True or False

def local_PackageNumberGroups(logger, **kw):
    """
        ������ ��� ������������ ������� ������ BatchIndex
    """
    order = kw.get('order')
    connect = kw.get('connect')

    filename = order.filename

    if not (connect and callable(connect)):
        raise ProcessException('Uncallable connect [local_PackageNumberGroups]!')

    params = (filename,)

    cursor, is_error = connect(SQL['PackageNumber']['groups'], params, with_commit=False, with_result=True)

    if is_error:
        logger('--> ������ �����������: %s' % filename)
        return []

    return cursor
