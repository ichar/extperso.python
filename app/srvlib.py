# -*- coding: utf-8 -*-

import os
from config import default_encoding, DATE_STAMP, cr

from .types import *
from .utils import isIterable, getToday, getTime, getDate, getDateOnly, daydelta

## ==============================
## CORE: SERVICE PUBLIC FUNCTIONS
## ==============================

def makeFileTypeIndex(filetype):
    return dict([(x[0], n+1) for n, x in enumerate(sorted(filetype['fieldset'].items(), key=lambda x: x[1][0]))])

def checkClockActive(key, **kw):
    service = kw.get('service')
    order = kw.get('order')
    ready_date = order is not None and order.ready_date or None
    if not ready_date:
        return True
    clock = getTime().split()[1]
    if getToday().date() >= ready_date.date():
        try:
            active = service is not None and key and service(key)
            s, f = active.split('-')
        except:
            s, f = '03:00', '21:00'
        if clock > s and clock < f:
            return True
    return False

## ------------------------------

def SRV_Encode(data, encoding=default_encoding):
    return data.encode(encoding)

srvEncode = SRV_Encode

def SRV_Write(fo, data, encoding=default_encoding, eol=None):
    fo.write(SRV_Encode('%s%s' % (str(data), eol or cr), encoding))

srvWrite = SRV_Write

def SRV_GetErrorCode(keys, key, code):
    return '%02d' % (key in keys and keys.index(key)+1 or 0)

srvGetErrorCode = SRV_GetErrorCode

def SRV_GetValue(value, is_error=False, index=0):
    return not is_error and value and len(value) > 0 and index < len(value[0]) and value[0][index] or None

srvGetValue = SRV_GetValue

def SRV_tomorrow(format=DATE_STAMP):
    return getDate(daydelta(getToday(), 1), format)

srvTomorrow = SRV_tomorrow

def SRV_GetSeen(source):
    if not (os.path.exists(source) and os.path.isfile(source)):
        fo = open(source, 'w')
        fo.close()

    today = getDate(getToday(), DATE_STAMP)
    index = 1
    p = 0

    with open(source, 'r+') as fo:
        line = fo.read()
        s = line and line.strip().split(':') or None

        if not (s and len(s) == 2 and s[0] == today and s[1].isdigit()):
            pass
        else:
            index = int(s[1]) + 1

        fo.seek(p, 0)
        fo.write('%s:%03d' % (today, index))

    return index

getSeen = SRV_GetSeen

def SRV_ResumeSeen(source, check_index):
    if not source:
        return

    if not (os.path.exists(source) and os.path.isfile(source)):
        fo = open(source, 'w')
        fo.close()

    today = getDate(getToday(), DATE_STAMP)
    index = 1
    p = 0

    with open(source, 'r+') as fo:
        line = fo.read()
        s = line and line.strip().split(':') or None

        if not (s and len(s) == 2 and s[0] == today and s[1].isdigit()):
            pass
        else:
            index = int(s[1]) - 1

        if check_index == index:
            fo.seek(p, 0)
            fo.write('%s:%03d' % (today, index))

resumeSeen = SRV_ResumeSeen

def SRV_Outgoing(logger, saveback, is_error, **kw):
    """
        Файл-квитанция
    """
    filename = kw.get('filename')
    saveback_errors = kw.get('saveback_errors')
    fieldset = kw.get('fieldset')
    keys = kw.get('keys')
    total = kw.get('total')

    accept = kw.get('accept')
    error = kw.get('error')
    ok = kw.get('ok')
    get_error_code = kw.get('get_error_code')

    if not (callable(accept) or callable(error) or callable(ok)) or is_error and not callable(get_error_code):
        return 0

    encoding = kw.get('encoding') or default_encoding
    eol = kw.get('eol') or cr

    # Квитанция без расширения
    if kw.get('no_ext') and '.' in filename:
        filename = filename.split('.')[0]

    output = is_error and error(filename) or accept is not None and accept(filename) or ok(filename)

    fo = open(output, 'wb')
    params = {'encoding' : encoding, 'eol' : eol}

    if is_error:
        if saveback_errors:
            for recno, id, errors in saveback_errors:
                srvWrite(fo, '%s: %s' % (id, ','.join([get_error_code(keys, key, code) for key, code in errors])), **params)
        elif kw.get('with_full_reject'):
            srvWrite(fo, filename, **params)
            srvWrite(fo, kw.get('error_code') or '00', **params)
    elif kw.get('empty_file'):
        pass
    else:
        srvWrite(fo, filename, **params)
        srvWrite(fo, total, **params)

    fo.close()

    logger('Файл-квитанция: %s' % output, True, is_error=is_error)
    
    return 1

makeOutgoing = SRV_Outgoing
