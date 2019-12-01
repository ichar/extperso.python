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
from app.utils import normpath, getDate, getToday, makeXLSContent

from ..defaults import *
from ..filetypes.postbank import *
from ..xmllib import *

# ------------------------- #

"""
    ������ ������ ������� ������.

    = ORDER.REPORT =

    ���������� ������:
        1. ������ �������� ������-�������.
"""

# ========================= #

def ToBank():
    return '%s/%s/ToBank' % (DEFAULT_OUTGOING_ROOT, FILETYPE_FOLDER)

def tags():
    return ('FileBody_Record',)

# ------------------------- #

def activate(logger, saveback, **kw):
    order = kw.get('order')
    #print_to(None, '%s: %s' % (str(getToday()), repr(order)))
    return order and '$P' not in order.filename and True or checkClockActive('postbank_active', **kw)

def gen_post_reportname(order, stamp_prefix, package_type, index):
    """
        ��������� ����-������ ��� ������� �������� "����� 1 �����" (SMTP)
    """
    today = getDate(getToday(), LOCAL_EASY_TIMESTAMP)
    report_name = '%s_%s_%s_%03d_Post1Class' % (stamp_prefix, today, package_type, index)
    return report_name

def post_report(n, node, logger, saveback, **kw):
    """
        ������ ������ ��� ������
    """
    if node.tag != 'FileBody_Record':
        return None

    # ��� ��������/��������
    delivery_type = getTag(node, 'DeliveryType')
    if local_GetDeliveryCompany(delivery_type) != 'P':
        return None

    today = getDate(getToday(), LOCAL_DATESTAMP)

    # ����� ������
    recno = getTag(node, 'FileRecNo')
    # ���� ��������/��������
    delivery_date = getTag(node, 'DeliveryDate')
    # ����� ������������ ��������
    package_code = getTag(node, 'PackageCode')
    # ������������ ��� �� �����������
    barcode = getTag(node, 'PostBarcode')
    # ��� ��������
    package_type = getINCRecordValue(node, 'PackageType')
    # �������� ��� ����������� ����
    case_box = getTag(node, 'CASE_BOX')
    # ��������
    case_enclosure = getTag(node, 'CASE_ENCLOSURE')
    # ����� ������
    stamp_code = getINCRecordValue(node, 'StampCode')
    # ��������� ����������� (��� ������������ ��������)
    price = str(int(getTag(node, 'PostRate') or '0') / 100)
    # ��� (���� �����)
    weight = 5

    # ���� ������: <������� ������>:<��� ��������>
    key = '%s:%s' % (stamp_code[:3], package_type)

    #if 'reports' not in saveback:
    #    saveback['reports'] = {}
    if key not in saveback['reports']:
        saveback['reports'][key] = {}
    if package_code not in saveback['reports'][key]:
        saveback['reports'][key][package_code] = {}
    if stamp_code not in saveback['reports'][key][package_code]:
        row = [today, 0, price, barcode, package_type, case_box, case_enclosure] #delivery_date
    else:
        row = saveback['reports'][key][package_code][stamp_code]

    # ������������ ��� ������ (�������� � �������)
    row[1] += 5

    saveback['reports'][key][package_code][stamp_code] = row

    return None

def outgoing(logger, saveback, is_error, **kw):
    """
        ��������� �����-������ (Excel)
    """
    order = kw.get('order')
    tmp = kw.get('tmp')
    actions = kw.get('actions')
    service = kw.get('service')

    subject = '����� %s' % order.filename.split(LOCAL_FILE_DELIVERY_SPLITTER)[0]
    addr_to = service is not None and service('postbank_mail_to') or email_address_list.get('postbank')

    headers = ['� �/�', '����� ������', '���� ��������', '���', '���', '����']
    title = '������ ����� 1 �����'

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
                # ������ ��� � ��� ������������ ��������
                if not barcode in weights:
                    weights[barcode] = [0, 0]
                # ��� �����
                weights[barcode][0] += weight
                n += 1
            if package_type and barcode:
                # ��� ������
                weights[barcode][1] += local_GetPackageWeight(case_box, weights[barcode][0]/5, enclosure=case_enclosure)

        # ������������� ���� ��������
        for row in rows:
            row[4] = weights.get(row[3])[1]

        rows.insert(0, headers)

        filename = gen_post_reportname(order, stamp_prefix, package_type, index)

        document = makeXLSContent(rows, title, True)

        message = '<html><body><h3>����-������ ��� ������� �������� "����� 1 �����"</h3></body></html>'
        
        if not send_mail_with_attachment(subject, message, addr_to, attachments=[(document, filename, 'xls'),]):
            logger('������ �������� ������� %s ����� 1 ����� %s: %s, rows: %s' % (
                order.filename, filename, addr_to, len(rows)), is_warning=True)
            continue
        
        logger('����-������ %s ����� 1 ����� %s ���������: %s, rows: %s' % (
            order.filename, filename, addr_to, len(rows)), force=True)

# ------------------------- #

def gen_dlv_reportname(order, key):
    """
        ��������� �� �������� DHL, ���� (SMTP)
    """
    today = getDate(getToday(), LOCAL_EASY_TIMESTAMP)
    report_name = '%s.csv' % order.filename.split('.')[0]
    return report_name

def delivery_report(n, node, logger, saveback, **kw):
    """
        ������ ������ ��� ���������
    """
    if node.tag != 'FileBody_Record':
        return

    # ��� ��������/��������
    delivery_type = getTag(node, 'DeliveryType')
    if local_GetDeliveryCompany(delivery_type) == 'P':
        return

    # ����� ������
    recno = getTag(node, 'FileRecNo')
    # ��� �������� ���������
    branch_delivery = getTag(node, 'BRANCHDELIVERY')
    # ������ ��������
    branch_send_to = getTag(node, 'BRANCH_SEND_TO')
    # ��� ������������ ��������
    package_code = getTag(node, 'PackageCode')

    # ���� ������: <������������ ��������>
    key = '%s' % delivery_type

    if key not in saveback['reports']:
        saveback['reports'][key] = {'items' : [], 'report' : []}
    report = saveback['reports'][key]
    if len(report['items']) == 0 or package_code != report['items'][-1]: # or branch_send_to != report['report'][-1][0]
        report['report'].append([branch_send_to,])
        report['items'].append(package_code)

def send_mail(logger, saveback, is_error, **kw):
    """
        �������� ��������� (CSV)
    """
    order = kw.get('order')
    tmp = kw.get('tmp')
    actions = kw.get('actions')
    service = kw.get('service')

    subject = CLIENT_NAME[2] + ' ��������� �� �������� %s'
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
          <h1 class="center">���� ������:</h1>
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
                fo.write(';'.join(row)+cr)

        rows = len(report)
        props['DeliveryType'] = key

        if not send_mail_with_attachment(subject % key, html % props, addr_to, attachments=[(tmp, filename, 'csv'),]):
            logger('������ �������� ��������� %s: %s, rows: %s' % (filename, addr_to, rows), is_warning=True)
            continue

        logger('��������� %s ����������: %s, rows: %s' % (filename, addr_to, rows), force=True)
