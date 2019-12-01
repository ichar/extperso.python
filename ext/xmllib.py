# -*- coding: cp1251 -*-

from config import (
     default_print_encoding, default_unicode, default_encoding, default_iso
     )

from app.xmllib import *

## ==========================
## EXT: XML PRIVATE FUNCTIONS
## ==========================

def FMT_PinTag(key, value):
    """
        Создать текст тега плоского формата для вставки в XML-контент: PinTag.

        Тег вида: RECID#00000023#;

        Аргументы:
            key     -- str, имя тега элемента
            value   -- str|int|bool|None, значение элемента

        Возврат:
            str, текст тега.
    """
    if not key or value is None:
        return ''
    return '%s#%s#;' % (key, 
        isinstance(value, bool) and (value and '1' or '0') or
        not value in ('', None,) and str(value) or 
        ' '
        )

def FMT_PanMask_4_4(value):
    if value is None:
        return None
    elif len(value) == 16:
        return '%s **** **** %s' % (value[:4], value[-4:])
    return None

def FMT_PanMask_6_4(value):
    if value is None:
        return None
    elif len(value) == 19:
        return '%s** **** %s' % (value[:7].replace(' ', ''), value[-4:])
    elif len(value) == 16:
        return '%s******%s' % (value[:6], value[-4:])
    elif len(value) == 18:
        return '%s********%s' % (value[:6], value[-4:])
    return None

def EAN_13Digit(v):
    if len(v) != 12:
        return None
    c = int(str(3*sum([int(v[n:n+1]) for n in range(1,12,2)]) + sum([int(v[n:n+1]) for n in range(0,12,2)]))[-1:])
    if c == 0:
        c = 10
    return '%s%s' % (v, 10 - c)

## -------------
## New Functions
## -------------

def FMT_ParseFIO(node, key):
    items = ['surname', 'firstname', 'lastname', 'other']
    x = getTag(node, key)
    if not x:
        return dict(zip(items, ['']*4))
    x = x.split(' ')
    n = len(x)
    n = n > 2 and 3 or n
    return dict(zip(items, x[:n]+[' ' for i in range(n,4)]))

def FMT_ParseAddress(node, key):
    items = ['index', 'region', 'district', 'city', 'town', 'street', 'house', 'building', 'flat']
    x = getTag(node, key).split(',')
    return dict(zip(items, x))

def FMT_CleanAddress(value):
    return value and ', '.join([x for x in value.split(',') if x]) or ''

def FMT_Limitstrlist(words, limit=20, comma=',', max_items=0):
    items = []
    s = ''
    for n, w in enumerate(words):
        if not w:
            continue
        if len(s)+len(w) < limit:
            s += ('%s%s' % (s and comma or '', w))
        else:
            items.append(s.strip())
            s = w
    if s:
        items.append(s.strip())
    n = len(items)
    if max_items and n < max_items:
        items += ['']* (max_items - n)
    return items

def GEN_DLV_Record(node, values, delimeter=None):
    name = 'DLV_Record'
    if not delimeter:
        delimeter = '|'
    record = getTag(node, name)
    if record:
        current_values = record.split(delimeter)
        for n, x in enumerate(values):
            if x is not None:
                if n < len(current_values):
                    current_values[n] = x
                else:
                    current_values.append(x)
        values = [x for x in current_values]
    return updateTag(node, name, delimeter.join(values))

def getDLVRecordValue(node, index):
    name = 'DLV_Record'
    record = getTag(node, name)
    if record:
        values = record.split('|')
        return index > -1 and index < len(values) and values[index]
    return None

def GEN_PIN_Record(node, values, **kw):
    name = 'PIN_Record'
    record = getTag(node, name)
    if record:
        items = record.split(';')
        current_values = [x.split('#')[0:2] for x in items if x]
        if kw.get('remove_empty'):
            n = 0
            while n < len(current_values):
                item = current_values[n]
                if not item[0].strip():
                    del current_values[n]
                else:
                    n += 1
        for x in values:
            for n, item in enumerate(current_values):
                if item[0] == x[0]:
                    current_values[n] = tuple(x)
        values = [tuple(x) for x in current_values]
    return updateTag(node, name, ''.join([FMT_PinTag(key, value) for key, value in values]))

def getPINRecordValue(node, name):
    name = 'PIN_Record'
    record = getTag(node, name)
    if record:
        items = dict([tuple(x.split('#')) for x in record.split(';')])
        return items.get(name)
    return None

def GEN_INC_Record(node, values, root=None):
    name = 'INC_Record'
    item = node.find(name)
    if not root:
        root = 'Record'
    if item is None:
        inc_record = ET.SubElement(node, name)
        record = FMT_XmlTag(inc_record, root)
    else:
        inc_record = item
        record = item.find(root)
    for key, value in values:
        updateTag(record, key, value)
    return inc_record

def getINCRecordValue(node, tag, root=None):
    name = 'INC_Record'
    item = node.find(name)
    if not root:
        root = 'Record'
    if item:
        record = item.find(root)
        return record and getTag(record, tag)
    return None

def GEN_OTK_Record(node, values, root=None):
    name = 'OTK_Record'
    item = node.find(name)
    if not root:
        root = 'Record'
    if item is None:
        inc_record = ET.SubElement(node, name)
        record = FMT_XmlTag(inc_record, root)
    else:
        inc_record = item
        record = item.find(root)
    for key, value in values:
        updateTag(record, key, value)
    return inc_record

def getOTKRecordValue(node, tag, root=None):
    name = 'OTK_Record'
    item = node.find(name)
    if not root:
        root = 'Record'
    if item:
        record = item.find(root)
        return record and getTag(record, tag)
    return None

def GEN_AREP_Record(node, values, root=None):
    name = 'AREP_Record'
    item = node.find(name)
    if not root:
        root = 'Record'
    if item is None:
        arep_record = ET.SubElement(node, name)
        record = FMT_XmlTag(arep_record, root)
    else:
        arep_record = item
        record = item.find(root) # [0]
    for key, value in values:
        updateTag(record, key, value)
    return arep_record

def getAREPRecordValue(node, tag, root=None):
    name = 'AREP_Record'
    item = node.find(name)
    if not root:
        root = 'Record'
    if item:
        record = item.find(root) # [0]
        return record and getTag(record, tag)
    return None

def FMT_CreateMICValue(key, value, locale):
    """
        Создать текст тега плоского формата для вставки в XML-контент: TLV-item.

        Тег вида: ~RECNO#000000800000023

        Аргументы:
            key     -- str, имя тега элемента
            value   -- str|int|bool|None, значение элемента
            locale  -- WIN|DOS

        Возврат:
            str, текст тега.
    """
    if not key:
        return ''
    if isinstance(value, bool):
        value = value and 'Y' or 'N'
    else:
        value = str(value)
    out = '~%s#%07d%s' % (key, len(value), value)
    if locale == 'DOS':
        out = out.encode(default_print_encoding).decode(default_encoding)
    return out

def GEN_DTC_Record(node, values, locale='WIN'):
    name = 'DTC_Record'
    item = node.find(name)
    if item is None:
        record = ET.SubElement(node, name)
    else:
        record = item
    out = ''
    for key, value in values:
        out += FMT_CreateMICValue(key, value, locale)
    record.text = out and str(out) or ''
    return record

def FMT_PanWide(value):
    v = value and str(value).strip() or value
    if not v:
        return ''
    return ' '.join([v[:4], v[4:8], v[8:12], v[12:16]])

def FMT_BILN(cvv2, **kw):
    PAN = kw.get('PAN')
    if len(cvv2) > 3:
        return '%23s' % cvv2
    elif PAN and PAN[0] in '2:4':
        return ' '*15 + PAN[12:16] + ' ' + cvv2
    return ' '*20 + cvv2

def FMT_ExpireDate(value):
    return ' '*11 + str(value) + ' '*3
