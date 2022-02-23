# -*- coding: cp1251 -*-

__all__ = ['tags', 'csv', 'sort_report', 'check_access']

import os

from config import (
    IsDebug, IsDeepDebug, IsDisableOutput, IsPrintExceptions,
    default_print_encoding, default_unicode, default_encoding, default_iso, cr,
    LOCAL_EASY_DATESTAMP, UTC_FULL_TIMESTAMP, DATE_STAMP,
    print_to, print_exception
)

from app.core import ProcessException
from app.srvlib import getSeen, resumeSeen
from app.utils import normpath, getDate, getToday, mkdir, getDefaultValueByKey

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
    return ('FileInfo', 'FileBody_Record', 'ProcessInfo')

# ------------------------- #

class CrdSrtDeliveryName:

    def __init__(self):
        self._value = ['', '']

    @property
    def delivery_date(self):
        return self._value[0]
    @property
    def delivery_type(self):
        return self._value[1]

    def check(self, x):
        if LOCAL_FILE_DELIVERY_SPLITTER in x:
            self._value = x.split(LOCAL_FILE_DELIVERY_SPLITTER)
            return None
        elif getDate(x, format=DATE_STAMP, is_date=1):
            return x
        elif len(x) == 2 and x.isdigit():
            return x

    def parse(self, ordername):
        dates = 'xxx'

        for w in ordername.split('_'):
            if w == '005':
                pass
            elif '.' in w:
                self.check(w.split('.')[0])
                break
            elif w == 'CRDEMB':
                dates = ''
            elif dates != 'xxx':
                x = self.check(w)
                if x:
                    dates += '%s%s' % (dates and '_' or '', x)

        return dates


def csv(order, logger, saveback, **kw):
    """
        ИСХОДЯЩИЙ ФАЙЛ ОТЧЁТА СОРТИРОВКИ (CRDSRT)
    """
    service = kw.get('service')
    params = kw.get('params')

    today = getDate(getToday(), format=DATE_STAMP)

    ordername = order.filename

    crd = CrdSrtDeliveryName()

    dates = crd.parse(ordername)

    root = '%s/%s/DlvReports' % (DEFAULT_OUTGOING_ROOT, FILETYPE_FOLDER)
    seen = '%s/%s' % (root, service is not None and service('seen') or 'seen')

    index = '%03d' % getSeen(seen)

    is_report_today = getDefaultValueByKey('is_report_today', params, LOCAL_IS_REPORT_TODAY)

    filename = 'VBEX_CRDSRT_005_%s_%s_%s' % (dates, 
        is_report_today and today or 
            max(getDate(order.ready_date, format=DATE_STAMP), crd.delivery_date) or 
            today, 
        index)
    destination = '%s/%s.csv' % (root, filename)

    saveback['destination'] = destination
    saveback['seen'] = (seen, index)

    logger('SortReport started: %s' % destination, force=True)

    return destination

def sort_report(n, node, logger, saveback, **kw):
    """
        Расчет данных для отчета и пересылка файла в системе инфообмена (CSV)
    """
    actions = kw.get('actions')
    order = kw.get('order')
    connect = kw.get('connect')
    params = kw.get('params')

    if node.tag == 'FileInfo':
        saveback['total'] = 0
        return

    if node.tag == 'ProcessInfo':
        destination = saveback.get('destination')
        if actions is not None and destination:
            info = '%s(%s) [%s]' % (order.filename, order.id, getDefaultValueByKey('report_name', params, ''))

            try:
                total = saveback['total']
            except Exception as ex:
                msg = 'unloader[sort_report]: %s Unexpected error[%s], recno:%s' % (info, ex, n)
                logger(msg, is_error=True)
                raise

            if total > 0:
                actions.add('unloader.postbank', 'move', (destination, ToBank()), info)
            else:
                actions.add('unloader.postbank', 'remove', (destination,), info)

            if IsDebug:
                print_to(None, 'unloader.postbank [sort_report]: %s ID:%s %s [%s] OK' % (
                    getToday(), 
                    order.id, 
                    order.filename,
                    total,
                    ))

        return None

    # -----------------------------------
    # КОНТРОЛЬ СТАТУСА ОТГРУЗОЧНОГО ФАЙЛА
    # -----------------------------------

    if not order or not order.status_id or order.status_id not in LOCAL_FILESTATUS_READY:
        return None

    today = getDate(getToday(), LOCAL_DATESTAMP)

    # Тип файла
    filetype = order.filetype
    # Дизайн продукта
    product_design = getTag(node, 'ProductDesign')

    # ------------------
    # БЛОКИРОВКА ДИЗАЙНА
    # ------------------

    #if local_IsPlasticDisabled(product_design, filetype=filetype):
    #    return None

    delivery_type = getTag(node, 'DeliveryType')
    delivery_company = local_GetDeliveryCompany(delivery_type)
    delivery_date = getTag(node, 'DeliveryDate')

    is_delivery_with_date = local_IsDeliveryWithDate(node)
    is_delivery_with_barcode = local_IsDeliveryWithBarcode(node)

    is_report_today = getDefaultValueByKey('is_report_today', params, LOCAL_IS_REPORT_TODAY)

    # -------------------------------
    # Дата отчета по карте - текущая!
    # -------------------------------

    #if is_report_today and is_delivery_with_date and delivery_date != today:
    #    return None

    saveback['total'] += 1

    out = '%s;%s;%s;%s;%s;%s;%s;%s' % (
        getTag(node, 'StampCode'), 
        getTag(node, 'BRANCHDELIVERY'), 
        getTag(node, 'PAN'), 
        product_design, 
        (not is_report_today or is_delivery_with_date) and delivery_date or today,
        is_delivery_with_barcode and getTag(node, 'PostBarcode') or '',
        getTag(node, 'LoyaltyNumber'),
        getTag(node, 'EAND'),
    )

    mifare = ''
    app_trans = ''

    out += ';%s;%s;%s' % (
        mifare,
        app_trans,
        local_GetIssueNumber(node, order, connect, logger, saveback),
    )

    return out

# ========================= #

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
