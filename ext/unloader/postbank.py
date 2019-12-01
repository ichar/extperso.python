# -*- coding: cp1251 -*-

__all__ = ['tags', 'csv', 'sort_report', 'check_access']

import os

from config import (
    IsDebug, IsDeepDebug, IsDisableOutput, IsPrintExceptions,
    default_print_encoding, default_unicode, default_encoding, default_iso, cr,
    LOCAL_EASY_DATESTAMP, UTC_FULL_TIMESTAMP, DATE_STAMP,
    print_to, print_exception
)

from app.srvlib import getSeen
from app.utils import normpath, getDate, getToday, mkdir

from ..defaults import *
from ..filetypes.postbank import *
from ..xmllib import *

# ------------------------- #

"""
    Модуль выгрузки данных заказа.

    = UNLOADER =

    Назначение модуля:
        1. Выгрузка данных выходных файлов.
"""

# ========================= #

def ToBank():
    return '%s/%s/ToBank' % (DEFAULT_OUTGOING_ROOT, FILETYPE_FOLDER)

def tags():
    return ('FileBody_Record', 'ProcessInfo')

# ------------------------- #

def csv(order, logger, saveback, **kw):
    """
        ИСХОДЯЩИЙ ФАЙЛ ОТЧЁТА СОРТИРОВКИ
    """
    service = kw.get('service')

    today = getDate(getToday(), DATE_STAMP)
    ordername = order.filename

    delivery_date = ''
    delivery_type = ''
    dates = 'xxx'

    for w in ordername.split('_'):
        if w == '005':
            pass
        elif '.' in w:
            x = w.split('.')
            if LOCAL_FILE_DELIVERY_SPLITTER in x[0]:
                delivery_date, delivery_type = x[0].split(LOCAL_FILE_DELIVERY_SPLITTER)
            break
        elif w == 'CRDEMB':
            dates = ''
        elif dates != 'xxx':
            dates += '%s%s' % (dates and '_' or '', w)

    root = '%s/%s/DlvReports' % (DEFAULT_OUTGOING_ROOT, FILETYPE_FOLDER)
    seen = '%s/%s' % (root, service is not None and service('seen') or 'seen')

    index = '%03d' % getSeen(seen)

    filename = 'VBEX_CRDSRT_005_%s_%s_%s' %(dates, today, index) # delivery_date
    destination = '%s/%s.csv' % (root, filename)

    saveback['destination'] = destination

    logger('SortReport started: %s' % destination, force=True)

    return destination

def sort_report(n, node, logger, saveback, **kw):
    """
        Расчет данных для отчета и пересылка файла в системе инфообмена (CSV)
    """
    actions = kw.get('actions')

    if node.tag == 'ProcessInfo':
        destination = saveback.get('destination')
        if actions is not None and destination:
            order = kw.get('order')
            info = '%s(%s)' % (order.filename, order.id)
            actions.add('unloader.postbank', 'move', (destination, ToBank()), info)
        return None

    today = getDate(getToday(), LOCAL_DATESTAMP)

    delivery_type = getTag(node, 'DeliveryType')
    delivery_company = local_GetDeliveryCompany(delivery_type)

    return '%s;%s;%s;%s;%s;%s;%s;%s' % (
        getTag(node, 'StampCode'), 
        getTag(node, 'BRANCHDELIVERY'), 
        getTag(node, 'PAN'), 
        getTag(node, 'ProductDesign'), 
        today, # getTag(node, 'DeliveryDate')
        delivery_company == 'P' and getTag(node, 'PostBarcode') or '',
        getTag(node, 'LoyaltyNumber'),
        getTag(node, 'EAND'),
    )

def check_access(logger, saveback, **kw):
    service = kw.get('service')

    root = service('postbank_unload_to') # or '//172.19.12.4/BankApplicationsOTK/!Pers2.0'
    
    folder = '999'
    src = '%s/20181025/%s' % (root, folder) # /PersoStation/Inkass/InputData/PostBank/postonline
    src = normpath(src, share=1)

    print_to(None, src)

    if not (os.path.exists(src) and os.path.isdir(src)):
        mkdir(src)

    rows = [1,2,3,]

    print_to(None, len(rows))

    print(src)

    try:
        with open(src+r'/test.txt', 'w') as fi:
            for row in rows:
                fi.write(str(row)+'\n')
    except:
        raise

    print_to(None, '--> OK')

    return False
