# -*- coding: cp1251 -*-

import os
import requests
import urllib
import base64
import json
import io
import time

#from PIL import Image

try:
    from config import (
         IsDebug, IsDeepDebug, IsTrace, IsDisableOutput, IsPrintExceptions, IsNoEmail, 
         IsCheckConnect, IsForcedCleanAddress, IsCheckF103Sent, IsCheckSSL, 
         default_print_encoding, default_unicode, default_encoding, default_iso, cr, 
         LOCAL_EASY_DATESTAMP, UTC_FULL_TIMESTAMP, DATE_STAMP, 
         print_to, print_exception, setErrorlog, 
         postonline
    )
    from app.mails import send_mail_with_attachment
    from app.utils import normpath, unzip, check_folder_exists, isIterable, getDate

    from ext.xmllib import clean_address

    #setErrorlog('traceback.log')

except:
    IsDebug = 1
    IsDeepDebug = 1
    IsPrintExceptions = 0
    IsCheckConnect = 1
    IsForcedCleanAddress = 0
    IsCheckF103Sent = 0

    print_exception = None
    clean_address = None

## =============================
## EXT: POCHTA.RU ONLINE SERVICE
## =============================

def to_base64(str):
    return base64.b64encode(str.encode()).decode("utf-8")

def set_error(msg, **kw):
    kw.get('errors', []).append(msg)

def check_errors(**kw):
    return kw.get('errors') and True or False

def register_errors(point, items, **kw):
    if items:
        kw.get('errors', []).extend([{'point':point, 'items':items}])


_URL = {
    'clean_address'            : ('/%(api)s/clean/address', 'POST',),
    'create_order'             : ('/%(api)s/user/backlog', 'PUT',),
    'search_order'             : ('/%(api)s/backlog/%(id)s', 'GET',),
    'remove_orders'            : ('/%(api)s/backlog', 'DELETE',),
    'create_batch'             : ('/%(api)s/user/shipment', 'POST',),
    'change_send_date'         : ('/%(api)s/batch/%(name)s/sending/', 'POST',),
    'move_order_to_batch'      : ('/%(api)s/batch/%(name)s/shipment', 'POST',),
    'add_order_to_batch'       : ('/%(api)s/batch/%(name)s/shipment', 'PUT',),
    'remove_order_from_batch'  : ('/%(api)s/shipment', 'DELETE',),
    'list_of_batch'            : ('/%(api)s/batch/%(name)s/shipment', 'GET',),
    'make_batch_f103'          : ('/%(api)s/batch/%(name)s/checkin', 'POST',),
    'print_batch_f103'         : ('/%(api)s/forms/%(name)s/f103pdf', 'GET',),
    'print_order_forms'        : ('/%(api)s/forms/%(id)s/forms', 'GET',),
    'print_order_forms_before' : ('/%(api)s/forms/backlog/%(id)s/forms', 'GET',),
    'print_batch_all'          : ('/%(api)s/forms/%(name)s/zip-all', 'GET',),
    'settings'                 : ('/%(api)s/settings', 'GET',),
}

_DEFAULT_CONTENT_TYPE = 'application/json'
_DEFAULT_ACCEPT = 'application/json;charset=UTF-8'
_DEFAULT_APP_VERSION = '1.0'
_DEFAULT_BLOCK_SIZE = 1024
_DEFAULT_PHONE = '88005500770'
_DEFAULT_GOOD_QUALITY_CODE = ['GOOD', 'POSTAL_BOX', 'ON_DEMAND', 'UNDEF_05',]
_DEFAULT_GOOD_VALIDATION_CODE = ['VALIDATED', 'OVERRIDDEN', 'CONFIRMED_MANUALLY']
_DEFAULT_WARNINGS_CODE = ['NOT_VALIDATED_HAS_AMBI', 'NOT_VALIDATED_HAS_UNPARSED_PARTS']

_DEFAULT_FORCED_CODES = [ 
    ('UNDEF_06', 'NOT_VALIDATED_HAS_ASSUMPTION'),
]

_DEFAULT_SEND_DATE = '%Y/%m/%d'

_EXCEPTIONS_LIMIT = 10


class PochtaRuOnline:
    """
        ���������� � ������-�������� ���� "����� ������" (��������).
        https://otpravka.pochta.ru/specification#/main
    """

    def __init__(self, access_token, key=None, login=None, password=None):
        self._access_token = access_token
        self._key = key
        self._login = login
        self._password = password
        self._exceptions = 0

        if not key:
            self._key = to_base64('%s:%s' % (self._login, self._password))

        self.protocol = postonline.get('protocol')
        self.host = postonline.get('host')

        self._attrs = {}

    def _loads(self, response):
        return response is not None and json.loads(response.text) or None

    @property
    def access_token(self):
        return self._access_token

    @property
    def login_password(self):
        return self._key

    def _get_bool(self, key):
        return self._attrs.get(key) and "true" or "false"

    def _get_int(self, key):
        x = self._attrs.get(key)
        return x and str(x).isdigit() and int(x) or 0

    def _get_string(self, key):
        return self._attrs.get(key) or ''

    def _get_list(self, key):
        items = self._attrs.get(key) or []
        return ', '.join(items)

    @staticmethod
    def _unload_image(response, filename):
        f = open(normpath(filename, 1), 'wb')

        for block in response.iter_content(_DEFAULT_BLOCK_SIZE):
            if not block:
                break
            f.write(block)

        f.close()

    @staticmethod
    def _make_querystring(args):
        x = '&'.join(['%s=%s' % (key, value) for key, value in args if value])
        return x and '?' + x or ''

    def responseIsValid(self, response, is_printable=False):
        is_text = not is_printable and True or response is not None and response.text is not None
        return not (response is None or not response.status_code is 200 or not is_text)

    def checkResponse(self, response):
        r = self._loads(response)
        errors = isinstance(r, dict) and r.get('errors') or None
        return r, errors

    def connect(self, command, data=None, qs=None, stream=None, **kw):
        response = None

        headers = {
            "Content-Type": _DEFAULT_CONTENT_TYPE,
            "Authorization": "AccessToken %s" % self.access_token,
            "X-User-Authorization": "Basic %s" % self.login_password,
        }

        is_printable = not kw.get('is_image') and True or False
        is_check_exception = kw.get('is_check_exception') and True or False

        path, method, accept = '', '', _DEFAULT_ACCEPT
        x = _URL.get(command)

        if len(x) == 3:
            path, method, accept = x
        elif len(x) == 2:
            path, method = x

        headers["Accept"] = accept

        attrs = {'api' : _DEFAULT_APP_VERSION, 'id' : kw.get('id'), 'name' : kw.get('name')}
        url = '%s%s%s%s' % (self.protocol, self.host, path % attrs, qs or '')

        if IsDeepDebug:
            print('headers:', headers)
            print('method:', method)
            print('data:', data)
            print('URL:', url)

        if IsTrace:
            print_to(None, '%s%s' % ('headers:', headers))
            print_to(None, '%s%s' % ('method:', method))
            print_to(None, '%s%s' % ('data:', data))
            print_to(None, '%s%s' % ('URL:', url))

        package = data and json.dumps(data) or None

        is_checked_error = False
        verify = IsCheckSSL and True or False

        try:
            if not method:
                pass

            elif method == 'GET':
                response = requests.get(url, headers=headers, stream=stream, verify=verify)

            elif method == 'PUT':
                response = requests.put(url, headers=headers, data=package, verify=verify)

            elif method == 'POST':
                response = requests.post(url, headers=headers, data=package, stream=stream, verify=verify)

            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, data=package, verify=verify)

            response.raise_for_status()

        except Exception as ex:
            if is_check_exception and response is not None and response.status_code >= 400:
                raise

            if IsPrintExceptions:
                print_to(None, ['', 'PochtaRuOnline.connect Error[%s:%s:%d]: URL[%s], method:%s, data:%s' % (
                    command, ex, self._exceptions, url, method, repr(data))])
                print_exception()

            if IsCheckConnect and self._exceptions < _EXCEPTIONS_LIMIT:
                if isinstance(ex, requests.exceptions.ConnectionError) or isinstance(ex, requests.exceptions.HTTPError):
                    is_checked_error = True
            else:
                raise

        if is_checked_error:
            time.sleep(30)
            self._exceptions += 1
            return self.connect(command, data=data, qs=qs, stream=stream, **kw)

        if IsDeepDebug:
            print("Status code: ", response.status_code)
            
            if is_printable:
                print("Response body: ", response is not None and response.text or None)

        if IsTrace:
            code, text = -1, ''
            if response is not None:
                code = response.status_code
                text = response.text
            
            print_to(None, '--> connect: command:%s, url:%s, code:%s, response:%s' % (command, url, code, text))

        if not self.responseIsValid(response, is_printable=is_printable):
            pass

        return response

    def cleanAddress(self, attrs, **kw):
        """
            ������������ ������ �������� �� �����������.

            https://otpravka.pochta.ru/specification#/nogroup-normalization_adress

            ���������:
                attrs           -- dict, �������� ������� (����� ��������)

            ������������ �������� ������� (����� attrs):
                id              -- ID ������� (������������ ���� �������)
                address         -- ������������ �����

            �������� ���������:
                forced_address  -- bool, ����� "��� ����"
                self_clean      -- bool, ����� "��� ������������", clean_address - ���������� ������ ������

            �������:
                address         -- dict, ��������������� ����� ��������

            ����� (str):
                index           -- ������
                region          -- ������, �������
                area            -- �����
                location        -- ����������
                place           -- �����, ���������� �����
                street          -- �����
                building        -- ��������
                house           -- ���
                corpus          -- ������
                room            -- ��������
        """
        self._attrs = attrs

        data = [{
            "id"               : self._get_string("id"),
            "original-address" : self._get_string("address"),
        }]

        response = self.connect('clean_address', data=data, **kw)

        if not self.responseIsValid(response, is_printable=True):
            return None
        
        r, errors = self.checkResponse(response)

        register_errors('cleanAddress.before', errors, **kw)

        if r is None or errors:
            return None
        
        if len(r) == 0 or not (isinstance(r[0], dict) and r[0].keys()):
            return None

        address = r[0]
        quality_code = address.get('quality-code')
        validation_code = address.get('validation-code')

        code = quality_code in _DEFAULT_GOOD_QUALITY_CODE and ( 
            validation_code in _DEFAULT_GOOD_VALIDATION_CODE or validation_code in _DEFAULT_WARNINGS_CODE) and 1 or 0

        forced_address = kw.get('forced_address')

        number = kw.get('number')
        self_clean = kw.get('self_clean')

        if not forced_address:
            errors = None if code == 1 else [(quality_code, validation_code)]

        if not code:
            if errors and isIterable(errors) and errors[0] in _DEFAULT_FORCED_CODES or not IsCheckF103Sent:
                if IsForcedCleanAddress:
                    code = 1
                else:
                    if IsDebug:
                        print_to(None, 'cleanAddress.posterror: %s %s, errors:%s, self_clean:%s' % (number, repr(address), errors, self_clean))

                    if callable(clean_address) and self_clean:
                        x = clean_address(self._get_string("address"), **kw)

                        if x:
                            address.update(x)
                            errors = []
                    else:
                        address = None

        if address and not address.get('index'):
            if not errors:
                errors = []
            errors.append('Post index is empty, address: %s' % address)

        if IsDebug:
            print_to(None, 'cleanAddress, code[%s]: %s %s, errors:%s' % (code, number, repr(address), errors))

        register_errors('cleanAddress.after', errors, **kw)

        return address

    def createOrder(self, attrs, **kw):
        """
            �������� ����������� (�����).

            ���������:
                attrs       -- dict, �������� ������� (������������ ��������� �����������)

            �������� ���������:
                cleaned     -- bool, ������� ��������� ������ cleanAddress

            ����� �������:
                response    -- list:

            �������:
                id          -- int, ID ������
        """
        self._attrs = attrs

        data = None

        def _add(words, with_to=False):
            for keyword in words.split(':'):
                key = keyword
                if with_to:
                    key = '%s-to' % keyword
                data[0][key] = attrs.get(keyword)

        if not kw.get('cleaned'):
            data = [{
                "address-type-to" : self._get_string("address-type-to") or "DEFAULT",       # ��� ������
                "area-to"         : self._get_string("area-to"),                            # �����:�����
                "building-to"     : self._get_string("building-to"),                        # �����:��������
                "corpus-to"       : self._get_string("corpus-to"),                          # �����:������
                "fragile"         : self._get_bool("fragile") or False,                     # ������� "�������"
                "given-name"      : self._get_string("given-name"),                         # ����������:���
                "house-to"        : self._get_string("house-to"),                           # �����:���
                "index-to"        : self._get_int("index-to"),                              # �����:������
                "location-to"     : self._get_string("location-to"),                        # �����:����������
                "mail-category"   : self._get_string("mail-category") or "SIMPLE",          # ��������� ���
                "mail-direct"     : self._get_int("mail-direct") or 643,                    # ��� ������
                "mail-type"       : self._get_string("mail-type") or "PARCEL_CLASS_1",      # ��� ���
                "mass"            : self._get_int("mass"),                                  # ��� ��� (� �������)
                "middle-name"     : self._get_string("middle-name"),                        # ����������:��������
                "order-num"       : self._get_string("order-num"),                          # ����� ������ ����������� (���)
                "place-to"        : self._get_string("place-to"),                           # �����:���������� �����
                "region-to"       : self._get_string("region-to"),                          # �����:�������, ������
                "street-to"       : self._get_string("street-to"),                          # �����:�����
                "room-to"         : self._get_string("room-to"),                            # �����:��������
                "surname"         : self._get_string("surname"),                            # ����������:�������
                "tel-address"     : self._get_string("phone"),                              # ������� ����������
            }]
        else:
            data = [{
                "address-type-to" : "DEFAULT",
                "mail-category"   : self._get_string("category"),
                "mail-type"       : self._get_string("type"),
                "mail-direct"     : 643,
                "mass"            : self._get_int("mass"),
                "tel-address"     : self._get_string("phone") or _DEFAULT_PHONE,
            }]

            _add('area:building:corpus:house:index:location:place:region:street:room', with_to=True)
            _add('given-name:middle-name:surname')

        if data and data[0].get("mail-type") == 'EMS_TENDER':                               # ��� ��� (EMS_TENDER)
            _add('transport-mode')

        # ID ������
        data[0]["id"] = attrs.get('id')
        # ������� ����� ������
        data[0]["order-num"] = attrs.get('number')
        # ��� �����
        data[0]["comment"] = attrs.get('comment')

        r, errors = self.checkResponse(self.connect('create_order', data=data, **kw))

        register_errors('createOrder', errors, **kw)

        if r is None or errors:
            return None

        codes = r.get("result-ids")

        return codes and len(codes) == 1 and codes[0] or None

    def searchOrderById(self, id, **kw):
        """
            ����� ������ � �������� ID.

            ���������:
                id          -- str, ID ������

            ����� �������:
                response    -- list:

            �������:
                data        -- tuple, (barcode, rate):

                               barcode: str, ��� ����������� (14)
                               rate: int, �������� ���� � ��� (� ��������)
        """
        r, errors = self.checkResponse(self.connect('search_order', id=urllib.parse.quote_plus(str(id)), **kw))

        register_errors('searchOrderById', errors, **kw)

        if r is None or errors:
            return None

        barcode = r.get("barcode")
        rate = r.get("mass-rate-with-vat")
        
        return barcode, rate

    def removeOrders(self, ids, **kw):
        """
            �������� ������� �� ������ ID.

            ���������:
                ids         -- list, ������ ID ������� (int|str)

            ����� �������:
                response    -- list:

            �������:
                data        -- list, [id,...]: 
                               ID ���������� ������
        """
        data = [x for x in ids if x]

        if not data:
            return

        r, errors = self.checkResponse(self.connect('remove_orders', data=data, **kw))

        register_errors('removeOrders', errors, **kw)

        if r is None or errors:
            return None

        data = r.get("result-ids")

        return data

    def createBatch(self, ids, send_date=None, **kw):
        """
            �������� ������ ������� �� ������ ID.

            https://otpravka.pochta.ru/specification#/batches-create_batch_from_N_orders

            ���������:
                ids         -- list, ������ ID ������� (int|str)
                send_date   -- str, ���� �������� yyyy-MM-dd (�����������)

            ����� �������:
                response    -- list, [batches, result-ids]:

                               batches: list, ������ ��������� ������ - dict: [batch,...]
                               result-ids: list, ������ ID �������, ���������� � ������

            �������:
                names       -- list, ������ ������

            ������:
                batch-name          -- str, ����� ������
                batch-status        -- str, ������ ������
                batch-status-date   -- str, ���� ���������� ������� ("2018-10-08T09:34:58.495Z")
                mail-category       -- str, ��������� ���
                mail-category-text  -- str, ��������� ��� (�����)
                mail-type           -- str, ��� ���
                mail-type-text      -- str, ��� ��� (�����)
                shipment-count      -- int, ���������� ������� � ������
                ...
        """
        data = [x for x in ids if x]

        if not data:
            set_error('No data', **kw)
            return None

        qs = self._make_querystring([('sending-date', send_date),])

        r, errors = self.checkResponse(self.connect('create_batch', data=data, qs=qs, **kw))

        register_errors('createBatch', errors, **kw)

        if r is None or errors:
            return None

        batches = r.get("batches")
        ids = r.get("result-ids")

        names = None

        if batches and len(batches) > 0:
            names = [x.get("batch-name") for x in batches]

        return names

    batch = createBatch

    def listOfBatch(self, name, **kw):
        """
            ������ ������ � ������� � ������.

            https://otpravka.pochta.ru/specification#/batches-get_info_about_orders_in_batch

            ���������:
                name        -- str, ����� ������

            ����� �������:
                response    -- list: [{'id':<>, 'order_num':<>, ...}, ...] ������ �����������, ������� ����������

            �������:
                code        -- int, ��� ����������: 1|0 (success|error)
                errors      -- list, ������ ������
        """
        r, errors = self.checkResponse(self.connect('list_of_batch', name=name, **kw))

        register_errors('listOfBatch', errors, **kw)

        if r is None:
            set_error('No data in batch', **kw)
            return None

        batches = r

        ids = []

        if batches and len(batches) > 0:
            ids = [str(x.get("id")) for x in batches]

        orders = {name : ids}

        return orders

    def changeBatchSendDate(self, name, date, **kw):
        """
            ���������(�����) ���� �������� ��� ������ � �������� �������.

            https://otpravka.pochta.ru/specification#/batches-sending_date

            ���������:
                name        -- str, ����� ������
                date        -- datetime, ���� ��������

            ����� �������:
                response    -- list:

                               error-code: str, ��� ������
                               f103-sent: bool, �������� �� ����������� ������ �103/�103� � ���?

            �������:
                code        -- int, ��� ����������: 1|0 (success|error)
                errors      -- list, ������ ������
        """
        qs = getDate(date, format=_DEFAULT_SEND_DATE)
        
        r, errors = self.checkResponse(self.connect('change_send_date', name=name, qs=qs, **kw))

        register_errors('changeBatchSendDate.before', errors, **kw)

        if r is None and not errors:
            return 1

        if r is None:
            set_error('Response is empty!', **kw)
            return None

        code = r.get("f103-sent") and 1 or 0
        errors = "error-code" in r and [r["error-code"]] or []

        register_errors('changeBatchSendDate.after', errors, **kw)

        return code

    change_date = changeBatchSendDate

    def makeBatchF103(self, name, **kw):
        """
            ���������� � �������� ����������� ����� 103 ��� ������ � �������� �������.

            https://otpravka.pochta.ru/specification#/documents-checkin

            ���������:
                name        -- str, ����� ������

            ����� �������:
                response    -- list:

                               error-code: str, ��� ������
                               f103-sent: bool, �������� �� ����������� ������ �103/�103� � ���?

            �������:
                code        -- int, ��� ����������: 1|0 (success|error)
                errors      -- list, ������ ������
        """
        if IsTrace:
            print_to(None, '--> register.before: name:%s' % name)

        r, errors = self.checkResponse(self.connect('make_batch_f103', name=name, **kw))

        register_errors('makeBatchF103', errors, **kw)

        if r is None or errors:
            return None

        if IsCheckF103Sent:
            code = r.get("f103-sent") and 1 or 0
        else:
            code = 1

        if IsTrace:
            print_to(None, '--> register.after: code:%s, errors:%s' % (code, errors))

        return code

    checkin = makeBatchF103

    def printBatchF103(self, name, destination, **kw):
        """
            ��������� �������� ����� 103 ��� ������ � �������� �������.

            https://otpravka.pochta.ru/specification#/documents-create_f103

            ���������� � ���������� pdf ���� � ������ �103 ��� ��������� ������. 

            ���������:
                name        -- str, ����� ������
                destination -- str, ������� ��� �������� pdf-�����

            ����� �������:
                response    -- bytes: ������� pdf-�����

            �������:
                code        -- int, ��� ����������: 1|0 (success|error)
        """
        response = self.connect('print_batch_f103', name=name, stream=True, is_image=True, **kw)

        if response is None:
            return 0

        self._unload_image(response, os.path.join(destination, '%s-F103.pdf' % name))

        return 1

    def printOrderForms(self, id, destination, send_date=None, print_type=None, **kw):
        """
            ��������� �������� ���� ��� ������ c �������� ID.

            https://otpravka.pochta.ru/specification#/documents-create_forms

            ���������� � ���������� pdf ����, ������� ��������, ����:
            - ����� �7� (�������, �������-������, ���������, ������-������);
            - ����� �-1 (EMS, EMS-�����������, ������ ������, ������ ������ ��������)
            - ������� (������ ��������).
            ����������� ������������� �����: �112�� (����������� � ���������� ��������), �22 (������� ������), 
            ����������� (��� ��������� ������ ��� ���������). 

            ���������:
                id          -- str, ID ������
                destination -- str, ������� ��� �������� pdf-�����
                send_date   -- str, ���� �������� yyyy-MM-dd (�����������)
                print_type  -- str, ��� ������ (�����������)

            ����� �������:
                response    -- bytes: ������� pdf-�����

            �������:
                code        -- int, ��� ����������: 1|0 (success|error)
        """
        qs = self._make_querystring([('sending-date', send_date), ('print-type', print_type),])

        response = self.connect('print_order_forms', id=id, qs=qs, stream=True, is_image=True, **kw)

        if response is None:
            return 0

        self._unload_image(response, os.path.join(destination, '%s-forms.pdf' % id))

        return 1

    def printOrderFormsBefore(self, id, destination, send_date=None, **kw):
        """
            ��������� �������� ���� ��� ������ c �������� ID (�� ������������ ������).

            https://otpravka.pochta.ru/specification#/documents-create_forms_backlog

            ���������� � ���������� pdf ����, ������� ����� ��������� � ����������� �� ���� �����������:
            - ����� �7� (�������, �������-������, ���������, ������-������);
            - ����� �-1 (EMS, EMS-�����������, ������ ������, ������ ������ ��������)
            - ������� (������ ��������).
            ����������� ������������� �����: �112�� (����������� � ���������� ��������), �22 (������� ������), 
            ����������� (��� ��������� ������ ��� ���������). 

            ���������:
                id          -- str, ID ������
                destination -- str, ������� ��� �������� pdf-�����
                send_date   -- str, ���� �������� yyyy-MM-dd (�����������)

            ����� �������:
                response    -- bytes: ������� pdf-�����

            �������:
                code        -- int, ��� ����������: 1|0 (success|error)
        """
        qs = self._make_querystring([('sending-date', send_date),])

        response = self.connect('print_order_forms_before', id=id, qs=qs, stream=True, is_image=True, **kw)

        if response is None:
            return 0

        self._unload_image(response, os.path.join(destination, '%s-forms-before.pdf' % id))

        return 1

    def printBatchZip(self, name, destination, **kw):
        """
            ��������� ������ ������������ ��� ������ � �������� �������.

            https://otpravka.pochta.ru/specification#/documents-create_all_docs

            ���������� � ���������� zip ����� � 4-�� �������:
            - Export.xls , Export.csv - ������ � ��������� ������� �� ������� � ������� ������
            - F103.pdf - ����� �103 �� ������� � ������� ������
            - ���� ����������� � ������� zip, ��������:F003232005484932300015.zip (?)
            - � ����������� �� ���� � ��������� �����������, ����������� ���������� �� ���������������� ���������� 
            � ������� pdf ( �����: f7, f112, f22).

            ���������:
                name        -- str, ����� ������
                destination -- str, ������� ��� �������� pdf-�����

            ����� �������:
                response    -- bytes: ������� zip-�����

            �������:
                code        -- int, ��� ����������: 1|0 (success|error)
        """
        response = self.connect('print_batch_all', name=name, stream=True, is_image=True, **kw)

        if response is None:
            return 0

        src = os.path.join(destination, '%s.zip' % name)

        self._unload_image(response, src)

        unzip(src, destination=name, is_relative=True)

        return 1

    all = printBatchZip

    def unload_documents(self, orders, destination, send_date=None, print_type=None, **kw):
        """
            �������� ������������ ������ ���������� �� ��������.

            ���������:
                orders      -- dict, {'name' : [id, ...]} ������ � �������� �� �������
                destination -- str, ������� ��� �������� ������
                send_date   -- str[optional], ���� �����������
                print_type  -- str[optional], ��� ������: 'THERMO', 'PAPER'

            �������:
                data        -- list, ������ ������������ ������
        """
        data, errors = [], []

        for name in orders:
            code = self.printBatchZip(name, destination, **kw)
            if not code:
                errors.append('Error in printBatchZip, batch: %s' % name)

            # Unzipped folder for a batch with given `name` made by printBatchZip
            folder = os.path.join(destination, name)

            code = self.printBatchF103(name, folder, **kw)
            if not code:
                errors.append('Error in printBatchF103, batch: %s, folder: %s' % (name, folder))

            for id in orders[name]:
                code = self.printOrderForms(id, folder, send_date=send_date, print_type=print_type, **kw)
                if not code:
                    errors.append('Error in printOrderForms, order: %s, folder: %s' % (id, folder))

            data.append(name)

        register_errors('unload_documents', errors, **kw)

        return data

    def register(self, attrs, **kw):
        """
            ����������� �����������.

            ���������:
                attrs           -- dict, �������� ������� (����� �������� + ������������ ��������� �����������)

            �������� ���������:
                forced_address  -- bool, �������������� ����������� ��� ����� ���� �������� ������

            ������������ �������� ������� (����� attrs):
                id              -- str, ID ������� (������������ ���� �������)
                address         -- str, ������������ �����
                receiver        -- str, ����������: ��� ����� ������ ��� ������������ �����������
                contact         -- str, ������� ���������� ��� ��������� �����������
                phone           -- int, ������� ����������
                mass            -- int, ����� ����������� � �������
                category        -- str, ��������� ���: SIMPLE|ORDERED|ORDINARY|...COMBINED
                type            -- str, ��� ���: LETTER_CLASS_1|PARCEL_CLASS_1

            �������:
                data            -- tuple, (id, barcode, rate):

                                   id: str, ID ������
                                   barcode: str, ��� ����������� (14)
                                   rate: int, �������� ���� � ��� (� ��������)
        """
        address = self.cleanAddress(attrs, **kw)

        if not address:
            set_error('ADDRESS IS INVALID', **kw)
            return None

        if check_errors(**kw):
            return None

        if IsTrace:
            print_to(None, '--> register.before: attrs:%s, address:%s' % (attrs, address))

        attrs.update(address)

        contact = attrs.get('contact')
        receiver = attrs.get('receiver')

        if contact:
            fio = dict(zip(['surname'], [contact]))
        elif receiver:
            fio = dict(zip('surname:given-name:middle-name'.split(':'), receiver.split()))
        else:
            set_error('RECEIVER IS EMPTY', **kw)
            return None

        attrs.update(fio)

        id = self.createOrder(attrs, cleaned=True, **kw)

        if IsTrace:
            print_to(None, '--> register.after: id:%s' % id)

        if not id or check_errors(**kw):
            return None

        r = self.searchOrderById(id, **kw)

        if not r or check_errors(**kw):
            return None

        barcode, rate = r

        return id, barcode, rate

    def unload(self, names, get_destination, **kw):
        """
            ��������� ���������.

            ���������:
                names  -- list, ������ ������� �����������

            �������� ���������:
                get_destination -- callable, ������� ������������� �������� �������� ������ �������� �����������
                with_forms      -- bool, �������� �������� ���� ��� �������

            �������:
                data: list -- ���������� ��������
        """
        data, errors = [], []

        if callable(get_destination):
            root, send_date, destination = get_destination(**kw)

            if IsDebug:
                print_to(None, 'unload destination:%s, root:%s' % (destination, root))

            check_folder_exists(destination, root)

            if not isIterable(names):
                names = [names]

            with_forms = kw.get('with_forms', None) and True or False

            for name in names:
                if with_forms:
                    # Get list of ids for the given batch
                    orders = self.listOfBatch(name, **kw)
                    # Unload document forms
                    if orders:
                        self.unload_documents(orders, destination, **kw)
                else:
                    code = self.all(name, destination, **kw)
                    if not code:
                        continue

                data.append(name)

            if not names:
                errors.append('No data to upload!')

        else:
            errors.append('upload: no destination callable!')

        register_errors('unload', errors, **kw)

        return data

    @staticmethod
    def send(ids, get_destination, **kw):
        """
            ��������� �������� F103-������ � ���.

            ���������:
                ids  -- list, ������ ������� �����������

            �������� ���������:
                get_destination -- callable, ������� ������������� �������� �������� ������ �������� �����������

            �������:
                data: list -- ���������� ��������
        """
        data, errors = [], []

        if callable(get_destination):
            addr_to = kw.get('addr_to')

            if not addr_to:
                set_error('No address to mail', **kw)
                return data

            client_title = kw.get('client_title') or ''
            filename = kw.get('filename') or ''

            root, send_date, destination = get_destination(**kw)

            if not isIterable(ids):
                ids = [ids]

            for id in ids:
                source = '%s/%s' % (destination, id)

                if not (os.path.exists(source) and os.path.isdir(source)):
                    errors.append('No source exists[%s]' % source)
                    continue

                subject = '%s%sF103:%s' % (client_title, client_title and ' ' or '', id)
                message = '����� � ��������� �����������%s. �����: %s' % (send_date and ' �� %s' % send_date or '', filename or str(id))
                attachments = [(source, x, 'zip') for x in os.listdir(source) if os.path.splitext(x)[1] == '.zip']

                if attachments:
                    if send_mail_with_attachment(subject, message, addr_to, attachments=attachments):
                        data.append('%s to %s' % (subject, addr_to))
                    else:
                        errors.append('No emailed, id:%s' % id)
                else:
                    errors.append('No attachments to email, id:%s, source:%s' % (id, source))

            if not ids:
                errors.append('No data to send!')

        else:
            errors.append('send: no destination callable!')

        register_errors('send', errors, **kw)

        return data


def registerPostOnline(mode, case, ids, get_destination=None, **kw):
    """
        ������-����������� ����������� �� ������� ����� ������.

        ���������:
            mode -- int, ����� ���������� {1|2|3|4}, default:1
            case -- str, ������������� ���� ����������� (���� ������� ������)
            ids  -- list, ������ ������� �����������

        �������� ���������:
            get_destination -- callable, ������� ������������� �������� �������� ������ �������� �����������
        
        �������������� �������� ��������� (kw):
            addr_to         -- str[optional]:mode=3,4, ������ ������� �������� zip-������ F103 (Emails)
            send_date       -- str[optional]:mode=3,4, ���� �����������
            print_type      -- str[optional]:mode=3, ��� ������
            client_title    -- str[optional]:mode=4, ������������ ������� � �������� ����������
            filename        -- str[optional]:mode=4, ��� �����-������
            with_forms      -- bool:mode=3, �������� �������� ���� ��� �������

        ������ ����������:
            errors          -- list (kw), �������� ��������(!)

        �������:
            data: list or dict or None -- ���������� ����������� � �������
    """
    data = []

    if not case in postonline:
        set_error('No account', **kw)
        return data

    if mode in (3, 4) and (get_destination is None or not callable(get_destination)):
        set_error('No destination', **kw)
        return data

    token, key = postonline[case]

    p = PochtaRuOnline(token, key)

    try:
        if not mode or mode == 1:

            # ----------------------------
            # ������� �������� �����������
            # ----------------------------

            attrs = {'id' : ids[0]}
            attrs.update(kw)

            data = p.register(attrs, **kw)

        elif mode == 2:

            # --------------
            # ������� ������
            # --------------

            names = p.batch(ids, **kw)
            if names:
                data = []
                for name in names:
                    code = p.checkin(name, **kw)
                    if not code or check_errors(**kw):
                        break
                    data.append(name)
            else:
                data = None

        elif mode == 3:

            # --------------------------------------------------
            # ��������� ��������� (����� 103, �7�, E-1, �������)
            # --------------------------------------------------

            data = p.unload(ids, get_destination, **kw)

        elif mode == 4:

            # ------------------------------------
            # ��������� �������� F103-������ � ���
            # ------------------------------------

            if not IsNoEmail:
                data = p.send(ids, get_destination, **kw)
            else:
                data = ['no emailed: %s' % id for id in ids]

    except Exception as ex:
        if IsPrintExceptions:
            print_to(None, ['', 'PochtaRuOnline.registerPostOnline: [%s,%s] Exception: %s, ids:%s' % (
                mode, case, str(ex), repr(ids))])
            print_exception()

    return data


def changePostOnline(batches, send_date, get_destination=None, **kw):
    """
        ��������������� ����������� �� ������� ����� ������.

        ������ ������ ����: <PostOnlineBatches>C1-A1:1540;C2-LETTER:251</PostOnlineBatches>

        ���������:
            batches   -- str, ������ ������� ������
            send_date -- datetime, ���� �������� � �������� ���������

        �������� ���������:
            get_destination -- callable, ������� ������������� �������� �������� ������ �������� �����������
            no_email        -- bool, �� ���������� �������� ����� � ���
            no_break        -- bool, �� ��������� ���������� ��������� ��� ��������� ������

        �������:
            data    -- list: ���������� ����������� � �������
            errors: -- dict: ������ ���������� �� �������
    """
    data, errors = [], {}

    is_no_email = (IsNoEmail or kw.get('no_email')) and True or False
    is_no_break = kw.get('no_break') and True or False
    
    try:
        for batch in batches:
            if not batch:
                continue

            case, name = batch.split(':')
            token, key = postonline[case]

            errors[batch] = []

            p = PochtaRuOnline(token, key)

            code = p.change_date(name, send_date, is_check_exception=True, errors=errors[batch], **kw)

            if IsDebug:
                print_to(None, 'changePostOnline.change_date, batch:%s, code[%s], errors:%s' % (batch, code, errors[batch]))

            if not code and 'ALL_SHIPMENTS_SENT' not in errors[batch] and not is_no_break:
                break

            code = p.checkin(name, errors=errors[batch])

            if IsDebug:
                print_to(None, 'changePostOnline.checkin, batch:%s, code[%s], errors:%s' % (batch, code, errors[batch]))

            if 'BATCH_NOT_CHANGED' in errors[batch]:
                data.append(name)
                continue

            if not code and not is_no_break:
                break

            items = p.unload(name, get_destination, send_date=send_date, errors=errors[batch], **kw)
            if items:
                data += items

            if not is_no_email:
                emails = p.send(name, get_destination, send_date=send_date, errors=errors[batch], **kw)

    except:
        if IsPrintExceptions:
            print_exception()

        raise

    return data, errors
