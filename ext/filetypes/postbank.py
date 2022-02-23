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
#   20191204: ����������� �������� local_GetPackageType, �������� 5-� ���� 'plastic_type' (������������ ������������ ��������)
#   20191211: ������ 41826203 Visa Platinum Green World VP18
#   20200110: ��� 405991 'pay_system' ������������ 'LongRSA' (���� RSA, ����������)
#   20200114: ���� 'plastic_types'... disabled, ���������� ��������: local_IsPlasticDisabled, 
#   20200114: ���������� ������������ ��������: 40599112
#   20200117: �������� ������ 40599223, Visa Classic Express Name (�������)
#   20200117: ������ 220077014, ������� �������� PAY_SYSTEM:KONA_2320_NSPK_701
#   20200421: ������������ �� 1.3.0:
#   20200421: ��������� ������� ��������� Mir EagleDual NoName: 22007702C, 22007702D, 22007702E
#   20200421: ���������� ������������ ��������: 40599211
#   20200422: ����������� ����� ����, s-prefix:S (None)
#   20200422: ��������� ����� ����� ������ �������� EMS, s-prefix:E
#   20200424: �������� ������� "�������� ����" (FILETYPE_POSTBANK_CASECOVER_PRODUCTS, ��� CASE_COVER): 22007702D
#   20200518: WebPerso Command: RepeatUnloadedReport (RUR)
#   20200603: ��������� EMS, local_IsDeliveryWithPostonline
#   20200904: ��������� ��������: 22007702C, 22007702D, 22007702E
#   20201007: ����� �������� 22007702 �� ��� 22007706 (!) ��������� ��������� �� ��� (���������� 2. ������������ ����� �������� � ����� ����)
#   20201022: �������� ������ 220077043, MirGreenWorld (�������)
#   20201130: ������ 41826201 Visa Marki Vip VP24
#   20201130: ������ "��������" ������� 40599212, 40599213, 40599214, 40599215 Visa Cyberlab VP25,VP26,VP27,VP28
#   20201204: �������� ��� ����� PostBank_CL (��������): FILETYPE_POSTBANK_CYBERLAB
#   20210114: ���� LOCAL_CHECK_POSTONLINE_FREE
#   20210116: �������� �������� ������� config.IsCheckSuspendedDates
#   20210209: ������ 220077012 Mir Eagle Dual Name VP29
#   20210312: ������ 220077014, ������� �������� PAY_SYSTEM:KONA_2350_NSPK_701 (��������)
#   20210407: ������ 41826101 Visa Business Corporate VP30
#   20210412: local_CaseEnvelope, local_CaseLeaflet - �������, ��������, ��������� ���� �����: 'envelope', 'leaflet'
#   20210423: AREPRecord root record definitions (special for VP30)
#   20210430: ������ 40599124 Visa �������� 120 KONA_2320 VP31
#   20210430: ������ 40599125 Visa �������� 120 NoName KONA_2320 VP32
#   20210528: ������ 220077071 ��� Supreme KONA_2350 VP33
#   20210628: ��� �������� EMS, mail-type:EMS_TENDER, transport-mode:EXPRESS (������ ����� �� 17.06.2021)
#   20210823: �������� ���� ������ CRDSRT ����� ������: local_GetIssueNumber
#   20210914: ����� ���� 'MICRON_706' �� 'KONA_2350' ��� �������� 22007702C, 22007702D, 22007702E
#   20210924: ������ 220077071 (VP33, Supreme): �������, ��������
#   20211014: ������ 40599126 (������������� ����������� ����� � ���� � ����� �� �����) Visa Platinum Individual KONA_2350 VP34
#   20211204: ���������� ������� 40599113, ������ ���� 1.50
#   20211211: ������������ ������� ����������� core.srvlib: resumeSeen
#   20211213: �������� �������� �������: LOCAL_FILESTATUS_READY
#   20220124: ������ 52731701 (VP35, MC World Elite Debit)
#   20220208: ������ 220077071 (VP33, Supreme): �������� ���������� (�������� C2)
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

# ����� ������� ���� YY/MM -> MMYY
LOCAL_IS_CHANGE_EXPIREDATE = False
# ���������� �� ���� ��������
LOCAL_IS_PLASTIC_BATCHSORT = False
# ���������� �� ���� ��������
LOCAL_IS_PACKAGE_BATCHSORT = True
# ���������� ������������ ���� ��������
LOCAL_IS_MAX_DELIVERY_DATE = True
# ������������ ������� ���� � ����������: 0 - ������ ����������
LOCAL_IS_REPORT_TODAY = 1
# ��������� �������� ��������� ����� ��� ������ ����������� ��������
LOCAL_CHECK_DELIVERY_ZONE = False
# �������������� ������ �����(������) ����������� �����������
LOCAL_CHECK_POSTONLINE_FREE = 0
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
# �������� ������������ ������ ���������� �� ��������: 0 - ����� ������������ �� ���������, 1 - ����������� �����
LOCAL_POSTONLINE_WITH_FORMS = 0
# ��� ������: 'THERMO' - �������� (������������� �����), 'PAPER' - �������� ����� E-1
LOCAL_PRINT_TYPE = 'PAPER'
# �������� ������������ �������� � ����� ��������
LOCAL_DELIVERY_WITH_DATE = ('P', 'E')
# �������� ������������ �������� � ���
LOCAL_DELIVERY_WITH_BARCODE = ('P', 'E')
# �������� ������������ �������� � ������������ �����������
LOCAL_DELIVERY_WITH_POSTONLINE = ('P', 'E')
# ������� ������ ��� �������� �������
LOCAL_FILESTATUS_READY = (28, 61, 62, 71, 198)

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
##  ��������� � ������� ����� �����
##  -------------------------------

FILETYPE_POSTBANK_V1 = deepcopy(FILETYPE_POSTBANK_TEMPLATE)

FILETYPE_POSTBANK_V1.update({
    'tytle'           : '%s �������� ���� ������ PostBank_v1 ������ 1' % CLIENT_NAME[0],
    'filetype'        : 'PostBank_v1',
    # ------------------------------------------------
    # ��������� ���������� ��������� (�� ���� �������)
    # ------------------------------------------------
    #   product     -- PlasticType: {VP01|VP02|VP03|VP04|VP09|VP10|VP11|VP12|VP18|VP20|VP21|VP22|VP23|VP24|VP29}
    #   scode       -- ServiceCode (MSDP)
    #   pvki        -- PVKI (MSDP)
    #   d-prefix    -- ������� ������� ����� (������� ��� �� EAN-13)
    #   s-prefix    -- ������� ������� �������� �� ������������ ���������: (��� �������� ��������, � �������� ���������)
    #   pay_system  -- PAY_SYSTEM (SDC)
    #   name        -- ������������ ��������
    #   disabled    -- ������� ���������� ������� (�� ������������ � ��������)
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
            'name'       : 'Visa �������� 120',
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
            'name'       : 'Visa �������� 120 NoName',
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
##  �������������� ������
##  ---------------------

FILETYPE_POSTBANK_ID = deepcopy(FILETYPE_POSTBANK_TEMPLATE)

FILETYPE_POSTBANK_ID.update({
    'tytle'           : '%s �������� ���� ������ PostBank_ID �������������� ������' % CLIENT_NAME[0],
    'filetype'        : 'PostBank_ID',
    # ------------------------------
    # ��������� ���������� ���������
    # ------------------------------
    #   product     -- PlasticType: {VP05|VP06|VP13|VP17}
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
                'E'         : ('REN', 'ROL'),
            },
            'pay_system' : 'KONA_2320_NSPK_701', # KONA_2320_NSPK
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
##  ������ ��������
##  ---------------

FILETYPE_POSTBANK_CYBERLAB = deepcopy(FILETYPE_POSTBANK_TEMPLATE)

FILETYPE_POSTBANK_CYBERLAB.update({
    'tytle'           : '%s �������� ���� ������ PostBank_CL ��������' % CLIENT_NAME[0],
    'filetype'        : 'PostBank_CL',
    'postfix'         : '_CL',
    # ------------------------------
    # ��������� ���������� ���������
    # ------------------------------
    #   product     -- PlasticType: {VP25|VP26|VP27|VP28}
    #   scode       -- ServiceCode (MSDP)
    #   pvki        -- PVKI (MSDP)
    #   d-prefix    -- ������� ������� �����
    #   s-prefix    -- ������� ������� �������� �� ������������ ���������: (��� �������� ��������, � �������� ���������)
    #   pay_system  -- PAY_SYSTEM (SDC)
    #   name        -- ������������ ��������
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
    'CyberLabNumber' : {
        'register' : '[dbo].[REGISTER_PostBankCyberLabNumber_sp]',
    },
    'IssueNumber' : {
        'get'      : 'SELECT PValue FROM [BankDB].[dbo].[WEB_FileTZs_vw] '
                        'WHERE FileType=%s and TagValue=%s and PName=\'����� ������\''
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
        ��� ������ � ����������
    """
    return key in keys and '%02d' % (keys.index(key)+1) or code or '00'

def local_GetDeliveryCompany(delivery_type):
    """
        �������� ����������� ������������ �������� �� ������� ��������
    """
    return delivery_type == '����' and 'S' or delivery_type == 'EMS' and 'E' or delivery_type =='DHL' and 'D' or 'P'

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

def local_IsPlasticDisabled(product_design, **kw):
    """
        �������� ���������� ������� (disabled).
        
        ���������:
            product_design -- str, ���������� ��� �������� '405991XX'
        
        �������� ���������:
            filetype       -- str, ��� �����

        �������:
            bool, ���� ����������: 1/0.
    """
    filetype = local_filetypes.get(kw.get('filetype')) or DEFAULT_FILETYPE
    value = filetype['plastic_types'].get(product_design)

    if not value:
        return False

    return value.get('disabled') and True or False

def local_GetPlasticInfo(product_design, **kw):
    """
        ���������� � ��������.
        
        ���������:
            product_design -- str, ���������� ��� ������� '405991XX[X]'
        
        �������� ���������:
            filetype       -- str, ��� �����
            key            -- str, ������������� ��������� (keys)

        �������:
            list, [<��� �������>, <������-��� MSDP>, <PVKI>, <������� �������>, <��� ����>, <name>].
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
        ������� ��� �����.
        
        ���������:
            product_design -- str, ���������� ��� �������� '405991XX'
            delivery_type  -- str, ��� �������� (������������ ��������) {����|EMS|DHL|...}, default:����������� ('P')
        
        �������� ���������:
            orderfile      -- str, ��� �����
            filetype       -- str, ��� �����
            index          -- int, {0|1} 1:�������� ��������

        �������:
            str, ������� ��� ������: {ROL|RAL|...}, XXX - �������� �� ����������.
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
    #return '%s:%s:%s:%s:%s||%s:%s' % (delivery_company, branch_send_to, branch_delivery, package_type, plastic_type, card_type, plastic_type)
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
    # ������������� ��������
    delivery_company = getTag(node, 'DeliveryCompany')
    # ���-�� ���� � ������
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
        ��� ��������� �����������.

        ���������:
            ptype -- ��� �������� CASE_BOX: C1|C2-BOX|C2-LETTER|C3-LETTER
            cards -- ���-�� ���� � �����������
            s     -- ������������ ���-�� ���� � �������� 1-�� ������, default:10

        �������� ���������:
            delivery_company -- str, ��� ������������ ��������: D|S|P
            enclosure        -- str, ������-�������� (������������)
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
            filetype       -- str, ��� �����
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
    return FMT_ParseAddress(getTag(node, key), as_dict=True)

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
            filetype            -- str, ��� �����

        �������:
            str, stamp_code     -- ����� ������
            str, stamp_index    -- ��������� 4 ����� PAN ������ ����� � ��������
            str, package_code   -- ��� ������������ ��������
            str, post_code      -- ��� (�����������)
    """
    orderfile = kw.get('filename') or order.filename
    filetype = kw.get('filetype') or order.filetype
    
    recno = getTag(node, 'FileRecNo')

    # ������ ��������
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

    # ������� ��� �����
    index = is_addr_delivery and 1 or 0
    stamp_prefix = local_GetPlasticSPrefix(product_design, delivery_type, index=index, filetype=filetype, filename=orderfile)

    mode = 'StampNumber'
    """
    # ��� ������� ���� � �������� ��������� ������ �� ����������� (!!!)
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

    # �������� ����� ��������
    x = cursor[7].split(':')
    stamp_number, stamp_index, package_number, post_code = int(x[0] or 0), x[1], int(x[2] or 0), x[3]

    if config.IsDebug:
        config.print_to(None, '%s:%s, params:%s' % (mode, x, params[:7]))

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
    #   �������� (�������, �����������)
    #
    x = 8 - daydelta(today, delta).isoweekday()
    if x < 3:
        delta += x
    #
    #   ������� �� �������, ���� ����� �������� ����� ��������
    #
    if not is_fastfile and daydelta(today, delta).isoweekday() == 1 and today.isoweekday() > 4:
        delta += 1

    date = daydelta(today, delta)
    #
    #   ��������� ����������� ���
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
        ���������� ���� ��������
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

def local_GetIssueNumber(node, order, connect, logger, saveback, **kw):
    """
        ����� ������
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
##  ���������� ��������� �������
##  ----------------------------

def local_IsCyberLab(order):
    """
        ������ "��������"
    """
    return order.filetype == FILETYPE_POSTBANK_CYBERLAB['filetype']

def local_UpdateCyberLabNumber(node, order, connect, logger, saveback, **kw):
    """
        ������ "��������". ��������� ������ ��������� ��� (RESF).

        ���������:
            node                -- ET.Element, ���� ���� ������� ������ ������, ��� <FileBody_Record>
            order               -- Order, �����
            connect             -- func, ������� ��� ������ � ����� ������
            logger              -- func, ������� ������ �������
            saveback            -- dict, ����������� ������ ��������� �� ���������� ���������

        �������� ���������:
            filename            -- str, ��� ������������ �����-������
            filetype            -- str, ��� �����
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

    # �������� ����� ���������
    x = cursor[4].split(':')
    tid, number = x[0], int(x[1] or 0)

    if config.IsDebug:
        config.print_to(None, '%s:%s, params:%s' % (mode, x, params[:4]))

    if number == 0:
        raise ProcessException('SQL Error[number over limit], mode:%s, cursor:%s' % (mode, cursor))

    return 'RESF 1%06d' % number

##  --------------------------------
##  �������������� ��������� �������
##  --------------------------------

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
    return getTag(node, 'ProductDesign') not in FILETYPE_POSTBANK_NONAME_PRODUCTS

def local_IsDeliveryWithDate(node, delivery_company=None):
    """
        ���������� � ��������� ���� ��������
    """
    return (delivery_company or getTag(node, 'DeliveryCompany')) in LOCAL_DELIVERY_WITH_DATE

def local_IsDeliveryWithBarcode(node, delivery_company=None):
    """
        ���������� � ���
    """
    return (delivery_company or getTag(node, 'DeliveryCompany')) in LOCAL_DELIVERY_WITH_BARCODE

def local_IsDeliveryWithPostOnline(node, delivery_company=None):
    """
        ���������� � ������������ �����������
    """
    return (delivery_company or getTag(node, 'DeliveryCompany')) in LOCAL_DELIVERY_WITH_POSTONLINE

def local_WithBarcode(product_design, **kw):
    """
        ������� "���"
    """
    return _get_product_param(kw.get('filetype'), product_design, 'no_barcode', default=0) == 0

def local_WithCardHolder(node):
    """
        ������� "� �����������"
    """
    return getTag(node, 'ProductDesign') in FILETYPE_POSTBANK_WITHCARDHOLDER_PRODUCTS or local_IsNamedType(node) and local_IsAddrDelivery(node)

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
    return order.filetype in ('PostBank_X5',)

def local_CaseCover(node):
    """
        ������� "������� ����"
    """
    return getTag(node, 'ProductDesign') in FILETYPE_POSTBANK_CASECOVER_PRODUCTS

def local_WithEnclosure(product_design, **kw):
    """
        ������������ "��������"
    """
    return product_design in FILETYPE_POSTBANK_GREENWORLD_PRODUCTS and kw.get('is_named_type') and 'GREENWORLD' or ''

def local_PlasticFrontPrintType(product_design, **kw):
    """
        ��� ������ ����
    """
    return _get_product_param(kw.get('filetype'), product_design, 'front_print') or 'EMBOSSING'

def local_PlasticBackPrintType(product_design, **kw):
    """
        ��� ������ ������
    """
    return _get_product_param(kw.get('filetype'), product_design, 'back_print') or 'INDENT'

def local_CaseEnvelope(product_design, **kw):
    """
        ������� � ��������
    """
    return _get_product_param(kw.get('filetype'), product_design, 'envelope')

def local_CaseLeaflet(product_design, **kw):
    """
        ����� ��������
    """
    return _get_product_param(kw.get('filetype'), product_design, 'leaflet')

def local_CheckDesignIsInvalid(product_design, **kw):
    """
        �������������� ������� �������� ���������� �������
    """
    if product_design in ('220077012',) and not kw.get('is_named_type'):
        raise ProcessException('Invalid Design:[%s]' % product_design)
