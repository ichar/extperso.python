# -*- coding: cp1251 -*-

from config import (
     IsDebug, UTC_FULL_TIMESTAMP,
     default_print_encoding, default_unicode, default_encoding, default_iso, print_to
     )

from app.utils import getDate, getToday
from app.xmllib import *

def print_log_space(info=None):
    if IsDebug:
        print_to(None, '\n>>> %s %s\n' % (getDate(getToday(), format=UTC_FULL_TIMESTAMP), info or ''))

## ==========================
## EXT: XML PRIVATE FUNCTIONS
## ==========================

_DEFAULT_CORPUS = 'корп.'
_DEFAULT_X1 = 'стр.'
_DEFAULT_X2 = 'вл.'


def checkTagExists(node, name):
    """
        Проверить существование тега с заданным именем в составе узла.

        Аргументы:
            node    -- ET.Element, узел-родитель
            name    -- str, имя тега искомого элемента

        Возврат:
            Boolean, флаг True/False.
    """
    try:
        item = node.find(name).text or None
        return True
    except:
        return False

def checkSetExists(ob, key, value=None, node=None):
    """
        Проверить существование элемента набора в словаре с заданным ключом.
        
        Аргументы:
            ob      -- dict
            key     -- str, имя ключа
        
        Ключевые аргументы:
            value   -- any, значение элемента набора
            node    -- ET.Element, текущий узел структуры

        Возврат:
            any, значение элемента.
    """
    if key not in ob:
        ob[key] = set()
    if value is None and node is not None:
        value = getTag(node, key)
    if value not in ob[key]:
        ob[key].add(value)
    return value

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

def FMT_ParseAddress(value, as_dict=None):
    items = ['index', 'region', 'district', 'city', 'town', 'street', 'house', 'building', 'flat']
    x = [x.strip() for x in value.split(',')]
    # ** если 8.Корпус не пустое, конкатенируем <, корп.> и значение из 7.Дом.
    if len(x) > 7 and x[7]:
        x[7] = '%s%s' % (_DEFAULT_CORPUS, x[7])
    if as_dict:
        return dict(zip(items, x))
    return ','.join(x)

def FMT_CleanAddress(value):
    return value and ', '.join([x for x in value.split(',') if x]) or ''

def _address_default(value, is_original=None):
    if not value:
        return {}

    values = value.split(',')

    items = [
        (0, 'index'), 
        (1, 'TR'), (2, 'region'), 
        (3, 'TA'), (4, 'area'), 
        (5, 'TL'), (6, 'location'), 
        (7, 'TP'), (8, 'place'), 
        (9, 'TS'), (10, 'street'), 
        (11, 'house'), 
        (12, 'corpus'), (13, 'x1'), (14, 'x2'), 
        (15, 'room'),
        ]
    address = dict(zip([x[1] for x in items], [values[n].strip() for n, x in items]))

    # Регион, область
    address['region'] = ','.join(['.'.join([address['TR'], address['region']])])
    # Район
    address['area'] = ','.join([' '.join([address['TA'], address['area']])])
    # Город, населенный пункт
    # * если 4.Город и 5.Населённый пункт оба не пустые, конкатенируем через запятую. Если одно из них пустое, то в place не пустое значение.
    address['place'] = ','.join([x for x in ['.'.join([address['TL'], address['location']]), '.'.join([address['TP'], address['place']])] if x and x != '.'])
    # Улица
    address['street'] = ','.join(['.'.join([address['TS'], address['street']])])

    if is_original:
        remove_tags = 'TR:TA:TL:TP:TS'
        # Корпус
        if address['corpus']:
            address['corpus'] = '%s%s' % (_DEFAULT_CORPUS, address['corpus'])
        # Строение
        if address['x1']:
            address['x1'] = '%s%s' % (_DEFAULT_X1, address['x1'])
        # Владение
        if address['x2']:
            address['x2'] = '%s%s' % (_DEFAULT_X2, address['x2'])
    else:
        remove_tags = 'TR:TA:TL:TP:TS:x1:x2'
        # Корпус
        address['corpus'] = ','.join([x for x in [address['corpus'], address['x1'], address['x2']] if x])
        # Микрорайон
        address['location'] = ''

    for x in remove_tags.split(':'):
        del address[x]

    return address

def _address_type_pr01(value):
    items = ['index', 'region', 'area', 'location', 'place', 'street', 'house', 'corpus', 'room']
    values = value.split(',')
    address = dict(zip(items, values))
    # Город, Населенный пункт
    # * если 4.Город и 5.Населённый пункт оба не пустые, конкатенируем через запятую. Если одно из них пустое, то в place не пустое значение.
    location = address['location'].strip()
    place = address['place'].strip()
    if location and place:
        address['place'] = ','.join([location, place])
    else:
        address['place'] = location or place or ''
    address['location'] = ''
    # Корпус
    corpus = address['corpus']
    if corpus.startswith(_DEFAULT_CORPUS):
        address['corpus'] = corpus[len(_DEFAULT_CORPUS):]
    return address

def clean_address(value, **kw):
    if not value:
        return {}

    if kw.get('delivery_canal_code') == 'PR01':
        return _address_type_pr01(value)

    return _address_default(value)

def FMT_ParseDefaultAddress(value):
    items = ['index', 'region', 'area', 'location', 'place', 'street', 'house', 'corpus', 'x1', 'x2', 'room']
    address = _address_default(value, is_original=True)
    return address and ','.join([address[x] for x in items if address.get(x)]) or ''

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
