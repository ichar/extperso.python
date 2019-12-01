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
        Получить значение тега с заданным именем из состава узла.

        Аргументы:
            node    -- ET.Element, узел-родитель
            name    -- String, имя тега искомого элемента

        Возврат:
            String, текст тега.
    """
    item = node.find(name)
    return item is not None and item.text and str(item.text) or ''

def updateTag(node, name, value):
    """
        Обновить(добавить) тег с заданным значением.

        Аргументы:
            node    -- ET.Element, узел-родитель
            name    -- String, имя тега искомого элемента
            value   -- String, значение (текст) элемента

        Возврат:
            ET.Element, обновленный элемент.
    """
    item = node.find(name)
    if item is None:
        item = ET.SubElement(node, name)
    item.text = value and str(value) or ''
    return item

def removeTag(node, name):
    """
        Удалить тег с заданным именем.

        Аргументы:
            node    -- ET.Element, узел-родитель
            name    -- String, имя тега искомого элемента
    """
    item = node.find(name)
    if item is None:
        return
    node.remove(item)

def setBooleanTag(node, name, value):
    """
        Обновить(добавить) тег с заданным двоичным значением.

        Аргументы:
            node    -- ET.Element, узел-родитель
            name    -- String, имя тега искомого элемента
            value   -- any, True or False
    """
    updateTag(node, name, value and '1' or '0')

def getBooleanTag(node, name):
    """
        Получить значение двоичного тега с заданным именем из состава узла.

        Аргументы:
            node    -- ET.Element, узел-родитель
            name    -- String, имя тега искомого элемента

        Возврат:
            Boolean, двоичное значение тега.
    """
    return getTag(node, name) == '1' and True or False

def FMT_XmlTag(node, name, value=None):
    """
        Создать и добавить к узлу XML-элемент с заданным именем и значением.
        
        Аргументы:
            node    -- ET.Element, узел-родитель
            name    -- String, имя тега создаваемого элемента
            value   -- String, значение (текст) элемента
        
        Возврат:
            ET.Element, созданный узел в составе узла-родителя.
    """
    item = ET.SubElement(node, name)
    if value:
        item.text = value
    return item

addTag = FMT_XmlTag

def FMT_UnpackChecker(checker):
    """
        Распаковать данные об ошибке из CHECK-модуля.
        
        Аргументы:
            checker -- Tuple: (keys, codes), результаты обработки текущей записи файла
        
            keys  : List, Base.ordered_fieldset.keys(), структура входящего файла
            codes : Dict, <key> : <error code>, код ошибки в поле записи
        
        Возврат:
            res     -- String, строка с информацией об ошибках в записи файла
            errors  -- List, список кодов ошибок в полях.
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
        Сформировать XML запись об ошибке во входящем файле.
        
        Аргументы:
            node    -- ET.Element, узел-родитель
            errors  -- List, имя тега создаваемого элемента
        
        Возврат:
            ET.Element, созданный узел в составе узла-родителя.
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
