# -*- coding: cp1251 -*-

import re
import xml.etree.ElementTree as ET

from .types import *
from .utils import isIterable

## ==========================
## CORE: XML PUBLIC FUNCTIONS
## ==========================

def getTag(node, name):
    """
        �������� �������� ���� � �������� ������ �� ������� ����.

        ���������:
            node    -- ET.Element, ����-��������
            name    -- String, ��� ���� �������� ��������

        �������:
            String, ����� ����.
    """
    item = node.find(name)
    return item is not None and item.text and str(item.text) or ''

def updateTag(node, name, value):
    """
        ��������(��������) ��� � �������� ���������.

        ���������:
            node    -- ET.Element, ����-��������
            name    -- String, ��� ���� �������� ��������
            value   -- String, �������� (�����) ��������

        �������:
            ET.Element, ����������� �������.
    """
    item = node.find(name)
    if item is None:
        item = ET.SubElement(node, name)
    item.text = value and str(value) or ''
    return item

def removeTag(node, name):
    """
        ������� ��� � �������� ������.

        ���������:
            node    -- ET.Element, ����-��������
            name    -- String, ��� ���� �������� ��������
    """
    item = node.find(name)
    if item is None:
        return
    node.remove(item)

def setBooleanTag(node, name, value):
    """
        ��������(��������) ��� � �������� �������� ���������.

        ���������:
            node    -- ET.Element, ����-��������
            name    -- String, ��� ���� �������� ��������
            value   -- any, True or False
    """
    updateTag(node, name, value and '1' or '0')

def getBooleanTag(node, name):
    """
        �������� �������� ��������� ���� � �������� ������ �� ������� ����.

        ���������:
            node    -- ET.Element, ����-��������
            name    -- String, ��� ���� �������� ��������

        �������:
            Boolean, �������� �������� ����.
    """
    return getTag(node, name) == '1' and True or False

def FMT_XmlTag(node, name, value=None):
    """
        ������� � �������� � ���� XML-������� � �������� ������ � ���������.
        
        ���������:
            node    -- ET.Element, ����-��������
            name    -- String, ��� ���� ������������ ��������
            value   -- String, �������� (�����) ��������
        
        �������:
            ET.Element, ��������� ���� � ������� ����-��������.
    """
    item = ET.SubElement(node, name)
    if value:
        item.text = value
    return item

addTag = FMT_XmlTag

def FMT_UnpackChecker(checker):
    """
        ����������� ������ �� ������ �� CHECK-������.
        
        ���������:
            checker -- Tuple: (keys, codes), ���������� ��������� ������� ������ �����
        
            keys  : List, Base.ordered_fieldset.keys(), ��������� ��������� �����
            codes : Dict, <key> : <error code>, ��� ������ � ���� ������
        
        �������:
            res     -- String, ������ � ����������� �� ������� � ������ �����
            errors  -- List, ������ ����� ������ � �����.
    """
    errors = None
    res = None

    if checker and isIterable(checker) and len(checker) == 2:
        keys, codes = checker
        res = ','.join(['%s:%s' % (key, codes[key]) for key in keys])
        errors = [(key, codes[key]) for key in keys if codes[key] != CHECKER_OK]
    else:
        res = 'undefined'
        errors = [('CRC', CHECKER_CRCERROR)]

    return res, errors

def FMT_XMLErrorRecord(node, errors):
    """
        ������������ XML ������ �� ������ �� �������� �����.
        
        ���������:
            node    -- ET.Element, ����-��������
            errors  -- List, ��� ���� ������������ ��������
        
        �������:
            ET.Element, ��������� ���� � ������� ����-��������.
    """
    item = ET.SubElement(node, 'RPT_Record')
    FMT_XmlTag(item, 'PROCESS_ERR_MSG', 
        '[%s %s]%s' % (
            MSG_ERROR_RECORD_HEADER,
            getTag(node, 'FileRecNo'),
            ''.join(['[%s:%s]' % (key, code) for key, code in errors])
        ))

    return item

def FMT_GetChildren(nodes, key):
    """
        PM_PRS: data node children
    """
    values = {}
    for x in nodes:
        data, value = x.get('DataElement'), x.get('Value')
        if data not in values:
            values[data] = []
        if value not in values[data]:
            values[data].append(value)
    return values and values.get(key) or None
