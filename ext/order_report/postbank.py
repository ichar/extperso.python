# -*- coding: cp1251 -*-

__all__ = ['tags', 'activate', 'post_report', 'outgoing', 'dlv_report', 'send_mail']

import os

from config import (
    IsDebug, IsDeepDebug, IsDisableOutput, IsPrintExceptions,
    default_print_encoding, default_unicode, default_encoding, default_iso, cr,
    LOCAL_EASY_DATESTAMP, UTC_FULL_TIMESTAMP, DATE_STAMP,
    print_to, print_exception,
    email_address_list
)

from app.srvlib import checkClockActive
from app.mails import send_mail_with_attachment
from app.utils import normpath, getDate, getToday, makeXLSContent, getCurrency, getDefaultValueByKey

from ..defaults import *
from ..filetypes.postbank import *
from ..xmllib import *

# ------------------------- #

"""
    Модуль Печати отчетов заказа.

    = ORDER.REPORT =

    Назначение модуля:
        1. Печать выходных файлов-отчетов.
"""

# ========================= #

def ToBank():
    return '%s/%s/ToBank' % (DEFAULT_OUTGOING_ROOT, FILETYPE_FOLDER)

def tags():
    return ('FileBody_Record',)

# ------------------------- #

CARD_WEIGHT = 5

def activate(logger, saveback, **kw):
    order = kw.get('order')
    #print_to(None, '%s: %s' % (str(getToday()), repr(order)))
    return order and '$P' not in order.filename and True or checkClockActive('postbank_active', **kw)

def gen_post_reportname(order, stamp_prefix, package_type, index):
    """
        ИСХОДЯЩИЙ ФАЙЛ-РЕЕСТР ДЛЯ СПОСОБА ОТПРАВКИ "ПОЧТА 1 КЛАСС" (SMTP)
    """
    today = getDate(getToday(), LOCAL_EASY_TIMESTAMP)
    report_name = '%s_%s_%s_%03d_Post1Class' % (stamp_prefix, today, package_type, index)
    return report_name

def post_report(n, node, logger, saveback, **kw):
    """
        Расчет данных для отчета
    """
    if node.tag != 'FileBody_Record':
        return None

    order = kw.get('order')
    params = kw.get('params')

    # -----------------------------------
    # КОНТРОЛЬ СТАТУСА ОТГРУЗОЧНОГО ФАЙЛА
    # -----------------------------------

    if not order or not order.status_id or order.status_id not in LOCAL_FILESTATUS_READY:
        return None

    today = getDate(getToday(), LOCAL_DATESTAMP)

    # Тип файла
    filetype = order.filetype
    # Тип доставки/отгрузки
    delivery_type = getTag(node, 'DeliveryType')
    # Дизайн продукта
    product_design = getTag(node, 'ProductDesign')

    # -------------------
    # ТОЛЬКО ПОЧТА РОССИИ
    # -------------------

    if local_GetDeliveryCompany(delivery_type) not in LOCAL_DELIVERY_WITH_POSTONLINE:
        return None

    # ------------------
    # БЛОКИРОВКА ДИЗАЙНА
    # ------------------

    #if local_IsPlasticDisabled(product_design, filetype=filetype):
    #    return None

    # Номер записи
    recno = getTag(node, 'FileRecNo')
    # Дата доставки/отгрузки
    delivery_date = getTag(node, 'DeliveryDate')
    # Номер транспортной упаковки
    package_code = getTag(node, 'PackageCode')
    # Транспортный ШПИ на отправление
    barcode = getTag(node, 'PostBarcode')
    # Вид упаковки
    package_type = getINCRecordValue(node, 'PackageType')
    # Упаковка для пластиковых карт
    case_box = getTag(node, 'CASE_BOX')
    # Вложение
    case_enclosure = getTag(node, 'CASE_ENCLOSURE')
    # Номер пломбы
    stamp_code = getINCRecordValue(node, 'StampCode')
    # Стоимость отправления (вся транспортная упаковка)
    #price = str(int(getTag(node, 'PostRate') or '0') / 100)
    #price = getCurrency(int(getTag(node, 'PostRate') or '0') / 100, points=True) or '0.00'
    price = '%.2f' % (int(getTag(node, 'PostRate') or '0') / 100)
    # Вес (одна карта)
    weight = CARD_WEIGHT

    is_report_today = getDefaultValueByKey('is_report_today', params, LOCAL_IS_REPORT_TODAY)

    # -------------------------------
    # Дата отчета по карте - текущая!
    # -------------------------------

    #if is_report_today and delivery_date != today:
    #    return

    # Ключ отчета: <префикс пломбы>:<вид упаковки>
    key = '%s:%s' % (stamp_code[:3], package_type)

    if 'reports' not in saveback:
        saveback['reports'] = {}
    if key not in saveback['reports']:
        saveback['reports'][key] = {}
    if package_code not in saveback['reports'][key]:
        saveback['reports'][key][package_code] = {}
    if stamp_code not in saveback['reports'][key][package_code]:
        row = [not is_report_today and delivery_date or today, 0, price, barcode, package_type, case_box, case_enclosure]
    else:
        row = saveback['reports'][key][package_code][stamp_code]

    # Рассчитываем вес пломпы (упаковки с картами)
    row[1] += weight

    saveback['reports'][key][package_code][stamp_code] = row

    return None

def outgoing(logger, saveback, is_error, **kw):
    """
        Генерация файла-отчета (Excel)
    """
    order = kw.get('order')
    tmp = kw.get('tmp')
    actions = kw.get('actions')
    service = kw.get('service')
    params = kw.get('params')

    subject = 'РОЗАН %s' % order.filename.split(LOCAL_FILE_DELIVERY_SPLITTER)[0]
    addr_to = service is not None and service('postbank_mail_to') or email_address_list.get('postbank')

    headers = ['№ п/п', 'Номер пакета', 'Дата отгрузки', 'ШПИ', 'Вес', 'Цена']
    title = 'Реестр ПОЧТА 1 КЛАСС'

    report_name = getDefaultValueByKey('report_name', params, '')

    for index, key in enumerate(sorted(saveback['reports'])):
        stamp_prefix, package_type = key.split(':')

        rows = []
        n = 1
        weights = {}

        for package_code in sorted(saveback['reports'][key]):
            barcode = package_type = case_box = case_enclosure = None

            for stamp_code in sorted(saveback['reports'][key][package_code]):
                delivery_date, weight, price, barcode, package_type, case_box, case_enclosure = \
                    saveback['reports'][key][package_code][stamp_code]

                rows.append([n, stamp_code, delivery_date, barcode, weight, price])
                # Всегда ШПИ и вес транспортной упаковки
                if not barcode in weights:
                    weights[barcode] = [0, 0]
                # Вес НЕТТО
                weights[barcode][0] += weight

                n += 1

            if package_type and barcode:
                # Вес БРУТТО
                weights[barcode][1] += local_GetPackageWeight(case_box, weights[barcode][0] / CARD_WEIGHT, enclosure=case_enclosure)

        if not rows:
            continue

        # Корректировка веса упаковки
        for row in rows:
            row[4] = weights.get(row[3])[1]

        rows.insert(0, headers)

        filename = gen_post_reportname(order, stamp_prefix, package_type, index)

        document = makeXLSContent(rows, title, True)

        message = '<html><body><h3>ФАЙЛ-РЕЕСТР ДЛЯ СПОСОБА ОТПРАВКИ "ПОЧТА 1 КЛАСС"</h3></body></html>'

        if not send_mail_with_attachment(subject, message, addr_to, attachments=[(document, filename, 'xls'),]):
            logger('Ошибка рассылки реестра %s ПОЧТА 1 КЛАСС %s: %s, rows: %s [%s]' % (
                order.filename, filename, addr_to, len(rows), report_name), 
                is_warning=True)
            continue
        
        logger('Файл-реестр %s ПОЧТА 1 КЛАСС %s отправлен: %s, rows: %s [%s]' % (
            order.filename, filename, addr_to, len(rows), report_name), 
            force=True)

# ------------------------- #

def gen_dlv_reportname(order, key):
    """
        НАКЛАДНЫЕ НА ОТГРУЗКУ DHL (SMTP)
    """
    today = getDate(getToday(), LOCAL_EASY_TIMESTAMP)
    report_name = '%s.csv' % order.filename.split('.')[0]
    return report_name

def delivery_report(n, node, logger, saveback, **kw):
    """
        Расчет данных для накладных
    """
    if node.tag != 'FileBody_Record':
        return

    order = kw.get('order')

    # -----------------------------------
    # КОНТРОЛЬ СТАТУСА ОТГРУЗОЧНОГО ФАЙЛА
    # -----------------------------------

    if not order or not order.status_id or order.status_id not in LOCAL_FILESTATUS_READY:
        return None

    # Тип файла
    filetype = order.filetype
    # Тип доставки/отгрузки
    delivery_type = getTag(node, 'DeliveryType')

    # ----------------------------------
    # Тип доставки/отгрузки (только DHL)
    # ----------------------------------

    if local_GetDeliveryCompany(delivery_type) not in ('D',):
        return None

    # Дизайн продукта
    product_design = getTag(node, 'ProductDesign')

    # ------------------
    # БЛОКИРОВКА ДИЗАЙНА
    # ------------------

    #if local_IsPlasticDisabled(product_design, filetype=filetype):
    #    return None

    # Номер записи
    recno = getTag(node, 'FileRecNo')
    # Код элемента структуры
    branch_delivery = getTag(node, 'BRANCHDELIVERY')
    # Филиал доставки
    branch_send_to = getTag(node, 'BRANCH_SEND_TO')
    # Код транспортной упаковки
    package_code = getTag(node, 'PackageCode')
    # Номер пломбы
    stamp_code = getTag(node, 'StampCode')

    # Ключ отчета: <транспортная компания>
    key = '%s' % delivery_type

    if key not in saveback['reports']:
        saveback['reports'][key] = {'items' : [], 'report' : []}
    report = saveback['reports'][key]
    if len(report['items']) == 0 or package_code != report['items'][-1]: # or branch_send_to != report['report'][-1][0]
        report['report'].append([branch_send_to, 0, []])
        report['items'].append(package_code)

    # Чистый вес карт в упаковке
    report['report'][-1][1] += CARD_WEIGHT

    # Список пломб в составе транспортной упаковки
    package = report['report'][-1][2]
    if stamp_code and stamp_code not in package:
        package.append(stamp_code)

def send_mail(logger, saveback, is_error, **kw):
    """
        Отправка накладных (CSV)
    """
    order = kw.get('order')
    tmp = kw.get('tmp')
    actions = kw.get('actions')
    service = kw.get('service')

    subject = CLIENT_NAME[2] + ' Накладные на отгрузку %s'
    addr_to = service is not None and service('delivery_mail_to') or email_address_list.get('dhperso')

    html = '''
        <html>
        <head>
          <style type="text/css">
            h1 { font-size:18px; padding:0; margin:0 0 10px 0; }
            td { font-size:16px; font-weight:bold; line-height:24px; padding:0; color:#468; margin-left:0px; }
            div.line { border-top:1px dotted #888; width:100%%; height:1px; margin:10px 0 10px 0; }
            div.line hr { display:none; }
          </style>
        </head>
        <body>
          <h1 class="center">Файл заказа:</h1>
          <table>
          <tr><td class="value">%(ClientName)s</td><tr>
          <tr><td class="value">%(FileName)s</td></tr>
          <tr><td class="value">%(DeliveryType)s</td></tr>
          </table>
          <div class="line"><hr></div>
        </body>
        </html>
    '''

    headers = ['BRANCHDELIVERY']
    props = {'ClientName' : CLIENT_NAME[0], 'FileName' : order.filename}

    for key in saveback['reports']:
        report = saveback['reports'][key]['report']
        if not report:
            continue

        filename = gen_dlv_reportname(order, key)
        destination = normpath(os.path.join(tmp, filename))

        with open(destination, 'w') as fo:
            for row in report:
                fo.write(';'.join([
                    row[0],
                    str(row[1]),
                    '|'.join(row[2]),
                ])+cr)

        rows = len(report)
        props['DeliveryType'] = key

        code, canal, smtphost = send_mail_with_attachment(
            subject % key, 
            html % props, 
            addr_to, 
            attachments=[(tmp, filename, 'csv'),], 
            with_info=True
            )

        if not code:
            logger('Ошибка рассылки накладных %s: %s, rows: %s, canal:%s, smtphost:%s' % (
                filename, addr_to, rows, canal, smtphost), 
                is_warning=True)
            continue

        logger('Накладные %s отправлены: %s, rows: %s, code:%s, canal:%s, smtphost:%s' % (
            filename, addr_to, rows, code, canal, smtphost), 
            force=True)
