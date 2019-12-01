# -*- coding: cp1251 -*-

# ------------------ #
#   postbank.merge   #
# ------------------ #

__all__ = ['interval', 'clock', 'activate', 'deactivate', 'make_filename', 'custom']

import re

from config import (
     IsDebug, IsDeepDebug, IsDisableOutput, IsPrintExceptions,
     default_print_encoding, default_unicode, default_encoding, default_iso, cr,
     LOCAL_EASY_DATESTAMP, UTC_FULL_TIMESTAMP, DATE_STAMP,
     print_to, print_exception
)

from app.types.encodings import *
from app.types.statuses import *
from app.srvlib import *
from app.utils import getToday, getTime, getDate, getDateOnly, daydelta, rfind

from ..defaults import *
from ..filetypes.postbank import *
from ..xmllib import *

# ------------------------- #

"""
    Модуль Слияния файлов заказов.

    = ORDER.MERGE =

    Назначение модуля:
        1. Будильник активации функции слияния.
        2. Формирование объединенных данных входящих файлов.
"""

# ------------------------- #

def interval():
    return 'postbank_merge'

def clock(value):
    now = getTime().split()[1]
    x = value and value.split('-') or DEFAULT_MERGE_INTERVAL
    return now >= x[0] and now < x[1]

def activate(orders, saveback, is_error=False):
    today = getDate(getToday(), DATE_STAMP)

    def _get_date(filename):
        for w in filename.split('_'):
            if w.isdigit() and w[:4] == today[:4]:
                return w
        return ''

    dates = sorted(set([_get_date(order.filename) for order in orders]))
    lowerdate = dates[0]
    days = ''.join(['_'+x[6:] for x in dates if x != lowerdate])

    local_delivery_date = SRV_tomorrow()
    filename = 'VBEX_CRDEMB_%s%s_005_%s.TXT' % (lowerdate, days, local_delivery_date) #
    status = is_error and STATUS_REJECTED_INVALID or STATUS_ON_GROUPED

    saveback['FILENAME'] = filename

    return filename, status, ENCODING_WINDOWS

def deactivate(files, saveback, is_error=False):
    basename = saveback['FILENAME']
    name = basename.split('.')[0]
    n = rfind(name, '_')
    name = name[:n]

    for key in files:
        ext = files[key]['filename'].split(LOCAL_FILE_DELIVERY_SPLITTER)[1]
        local_delivery_date = local_GetDeliveryDate(size=files[key]['count'], format=DATE_STAMP)
        filename = '%s_%s%s%s' % (name, local_delivery_date, LOCAL_FILE_DELIVERY_SPLITTER, ext)

        files[key]['filename'] = filename

def make_filename(basename, key, filetype):
    n = rfind(basename, '.') or len(basename)
    name, ext = basename[:n], basename[n:]

    postfix = local_GetMergePostfix(filetype=filetype)

    return '%s%s%s%s%s' % (name, LOCAL_FILE_DELIVERY_SPLITTER, key, postfix, ext)

def custom(n, node, logger, saveback, **kw):
    if node.tag != 'FileBody_Record':
        return

    recno = '%08d' % n

    # Сквозной номер записи
    updateTag(node, 'FileRecNo', recno)

    # Способ доставки
    delivery_type = getTag(node, 'DeliveryType')
    # Условное обозначение транспортной компании
    delivery_company = local_GetDeliveryCompany(delivery_type)
    # Именные/Неименные
    is_named_type = local_IsNamedType(node)

    # Ключ записи текущего файла - транспортная компания
    #saveback['key'] = delivery_company
    # Тип карт - именные и неименные
    saveback['key'] = '%s%s' % (delivery_company, is_named_type and 'I' or 'N')

    logger('--> Merge Node: %s' % node.tag)

