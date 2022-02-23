# -*- coding: cp1251 -*-

import sys

def _address_default(value):
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
    # Корпус
    # ** если 8.Корпус не пустое, конкатенируем <, корп.> и значение из 7.Дом.
    address['corpus'] = ','.join([x for x in [address['corpus'], address['x1'], address['x2']] if x])
    # Микрорайон
    address['location'] = ''

    for x in 'TR:TA:TL:TP:TS:x1:x2'.split(':'):
        del address[x]

    return address

def _address_type_pr01(value):
    values = value.split(',')

    items = ['index', 'region', 'area', 'location', 'place', 'street', 'house', 'corpus', 'room']

    return dict(zip(items, values))

def clean_address(value, **kw):
    if not value:
        return {}

    if kw.get('delivery_canal_code') == 'PR01':
        return _address_type_pr01(value)

    return _address_default(value)


if __name__ == '__main__':
    argv = sys.argv

    value = argv[1]
    delivery_canal_code = len(argv) > 2 and argv[2] or None

    address = clean_address(value, delivery_canal_code=delivery_canal_code)

    for x in sorted(address.keys()):
        print('%-20s: %s' % (x, address[x]))
