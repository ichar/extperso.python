# -*- coding: cp1251 -*-

# ---------------------- #
#   otkrytie filetypes   #
# ---------------------- #

__all__ = [
    'LOCAL_IS_CHANGE_EXPIREDATE', 'LOCAL_ID_TAG', 
    'DEFAULT_EOL',
    'FILETYPE_FOLDER', 'PRELOADER', 'FILETYPE_OTKRYTIE_V1',
    'local_GetErrorCode'
    ]

import os
import pymssql

import config
from app.core import ProcessException, AbstractPreloaderClass, AbstractIncomingLoaderClass, AbstractReferenceLoaderClass
from app.types import *
from app.mails import send_mail_with_attachment
from app.srvlib import SRV_GetValue
from app.utils import normpath, check_folder_exists, getDate, getToday, daydelta, isIterable

from ..defaults import *
from ..xmllib import *

##  ---------------
##  LOCAL CONSTANTS
##  ---------------

# ����� ������� ���� YY/MM -> MMYY
LOCAL_IS_CHANGE_EXPIREDATE = False
# ��� ID ������
LOCAL_ID_TAG = 'CardID'

##  --------
##  DEFAULTS
##  --------

# ������ ����� ������ � ������-����������
DEFAULT_EOL = '\r\n'

##  -----------
##  DESCRIPTORS
##  -----------

# �������� ������� ������� ���������� � ������
FILETYPE_FOLDER = 'Otkrytie'

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

PRELOADER = {
    'class'           : AbstractPreloaderClass,
}

FILETYPE_OTKRYTIE_V1 = {
    'class'           : AbstractIncomingLoaderClass,
    'object_type'     : FILE_TYPE_INCOMING_ORDER,                   # FILE_TYPE_FROM_SDC
    'bankname'        : ('��� ���� "�� ��������"', '��������',),
    'tytle'           : '���� �������� ���� SDC Kona 2320 Visa',
    'format'          : FILE_FORMAT_PM_PRS,                         # FILE_FORMAT_TLV
    'persotype'       : None,
    'defaults'        : {
        'field_type'        : DATA_TYPE_FIELD,
        'data_type'         : DATA_TYPE_TEXT,
        'encoding'          : ENCODING_WINDOWS,
    },
    'line_delimeter'  : crlf,
    'field_delimeter' : b'~',
    'is_trancate'     : 1,
    'is_stripped'     : 1,
    # -------------------
    # ������������ PM_PRS
    # -------------------
    'namespaces'      : {'ns':'http://namespaces.globalplatform.org/systems-messaging/1.0.0'},
    'data'            : './/ns:ApplicationDataNotification',
    'tags'            : {
        'ADD3'              : (".//ns:DataSet[@Name='ADDI']/ns:Data[@DataElement='ADD3']",),
        'PAND'              : (".//ns:DataSet[@Name='ADTA']/ns:Data[@DataElement='PAND']",),
        'EXDT'              : (".//ns:DataSet[@Name='ENCD']/ns:Data[@DataElement='EXDT']",),
        'CRDN'              : (".//ns:DataSet[@Name='EMBD']/ns:Data[@DataElement='CRDN']",),
        'ZIPC'              : (".//ns:DataSet[@Name='CRDM']/ns:Data[@DataElement='ZIPC']",),
        'CNTR'              : (".//ns:DataSet[@Name='CRDM']/ns:Data[@DataElement='CNTR']",),
        'PIN1'              : (".//ns:DataSet[@Name='CRDM']/ns:Data[@DataElement='PIN1']",),
        'PIN3'              : (".//ns:DataSet[@Name='CRDM']/ns:Data[@DataElement='PIN3']",),
        'PIN4'              : (".//ns:DataSet[@Name='CRDM']/ns:Data[@DataElement='PIN4']",),
        'LSTN'              : (".//ns:DataSet[@Name='CRDM']/ns:Data[@DataElement='LSTN']",),
        'FRSN'              : (".//ns:DataSet[@Name='CRDM']/ns:Data[@DataElement='FRSN']",),
        'ADD1'              : (".//ns:DataSet[@Name='ADDI']/ns:Data[@DataElement='ADD1']",),
        'ADD2'              : (".//ns:DataSet[@Name='ADDI']/ns:Data[@DataElement='ADD2']",),
        'ADD4'              : (".//ns:DataSet[@Name='ADDI']/ns:Data[@DataElement='ADD4']",),
        'PLSC'              : (".//ns:DataSet[@Name='ADTA']/ns:Data[@DataElement='PLSC']",),
    },
    # ---------------------
    # ������ ������� ������
    # ---------------------
    'fieldset'        : {
        # �������� ����������
        'CardID'            : ('001', 'ADD3', None, DATA_TYPE_INTEGER, None, None, (4, 20), 1, 'ID �����'),
        'PAN'               : ('002', 'PAND', None, DATA_TYPE_TEXT_NS, DATA_PERSO_TYPE_PANWIDE16, None, (16,), 1, '����� ����� (� ������� NNNNNNNNNNNNNNNN)'),
        'ExpireDate'        : ('003', 'EXDT', None, DATA_TYPE_TEXT_NS, DATA_PERSO_TYPE_EXPDATE, None, (4,), 1, '���� ��������� �������� ����� (������ YYMM)'),
        'CardholderName'    : ('004', 'CRDN', None, DATA_TYPE_TEXT_ANS, None, None, (2, 26), 1, '��� � ������� ��������� �����'),
        'CompanyName'       : ('005', 'ELN4', None, DATA_TYPE_TEXT_ANS, None, None, (0, 50), 0, 'COMPANY NAME ������ ������������ ����'),
        'Delivery_Index'    : ('006', 'ZIPC', None, DATA_TYPE_INT, DATA_PERSO_TYPE_POSTINDEX, None, (6,), 1, '�����: �������� ������'),
        'Delivery_Country'  : ('007', 'CNTR', None, DATA_TYPE_TEXT, None, None, (1, 50), 1, '�����: ������'),
        'Delivery_City'     : ('008', 'PIN1', None, DATA_TYPE_TEXT, None, None, (1, 50), 1, '�����: �����'),
        'Delivery_Street'   : ('009', 'PIN3', None, DATA_TYPE_TEXT, None, None, (1, 50), 1, '�����: �����'),
        'Delivery_House'    : ('010', 'PIN4', None, DATA_TYPE_TEXT, None, None, (1, 50), 1, '�����: ����� ����, ��������'),
        'Receiver_LastName' : ('011', 'LSTN', None, DATA_TYPE_TEXT_A, None, None, (1, 20), 1, '����������: �������'),
        'Receiver_FirstName': ('012', 'FRSN', None, DATA_TYPE_TEXT_A, None, None, (1, 20), 1, '����������: ���'),
        'BranchName'        : ('013', 'ADD1', None, DATA_TYPE_TEXT_AS, None, None, (1, 100), 1, '������������ �����'),
        'BranchCode'        : ('014', 'ADD2', None, DATA_TYPE_NUMBER, None, None, (0,), 0, '��� (?)'),
        'TagsInfo'          : ('015', 'ADD4', None, DATA_TYPE_TEXT, None, None, (0,), 0, '���������� (?)'),
        'PlasticType'       : ('016', 'PLSC', None, DATA_TYPE_TEXT, None, None, (1, 20), 1, '��� ��������')
    },
}

"""
        # �������� ��������� SDC
        'CardID'            : ('001', 'CARDID', None, DATA_TYPE_INTEGER, None, None, (4, 20), 1, 'ID �����'),
        'PAN'               : ('002', 'ELN1', None, DATA_TYPE_TEXT_NS, DATA_PERSO_TYPE_PANWIDE19, None, (19,), 1, '����� ����� (� ������� NNNN NNNN NNNN NNNN)'),
        'ExpireDate'        : ('003', 'ELN2', None, DATA_TYPE_TEXT_NS, DATA_PERSO_TYPE_EXPIREDATE, None, (5,), 1, '���� ��������� �������� ����� (������ mm/yy)'),
        'CardholderName'    : ('004', 'ELN3', None, DATA_TYPE_TEXT_ANS, None, None, (2, 26), 1, '��� � ������� ��������� �����'),
        'CompanyName'       : ('005', 'ELN4', None, DATA_TYPE_TEXT_ANS, None, None, (0, 50), 0, 'COMPANY NAME ������ ������������ ����'),
        'CRDM'              : ('006', 'CRDM', None, DATA_TYPE_TEXT, None, None, (0,), 0, '����� ��� �������� ����')
        'ADDI'              : ('007', 'ADDI', None, DATA_TYPE_TEXT, None, None, (0,), 0, '�������� ����� ������ ADDI')
        'BILN'              : ('008', 'BILN', None, DATA_TYPE_TEXT_ANS, None, None, (0, 23), 1, '���������� �� ������ ��� �������'),
        'PlasticType'       : ('009', 'PLSC', None, DATA_TYPE_TEXT, None, None, (0,), 0, '��� ��������')
        'Track1'            : ('010', 'T1', None, DATA_TYPE_TEXT, None, None, (0, 70), 1, '���� 1'),
        'Track2'            : ('011', 'T2', None, DATA_TYPE_TEXT, None, None, (0, 39), 1, '���� 2'),
        'Track3'            : ('012', 'T3', None, DATA_TYPE_TEXT, None, None, (0, 70), 0, '���� 3'),
        'DUMPE'             : ('013', 'DUMPE', None, DATA_TYPE_TEXT, None, None, (0, 6000), 1, '������� ����'),
"""

# ========================= #

def local_GetErrorCode(keys, key, code):
    """
        ��� ������ � ����������
    """
    return '%02d' % (key in keys and keys.index(key)+1 or 0)
