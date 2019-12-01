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
         IsDebug, IsDeepDebug, IsDisableOutput, IsPrintExceptions, IsNoEmail, 
         default_print_encoding, default_unicode, default_encoding, default_iso, cr,
         LOCAL_EASY_DATESTAMP, UTC_FULL_TIMESTAMP, DATE_STAMP,
         print_to, print_exception, setErrorlog,
         postonline
    )
    from app.mails import send_mail_with_attachment
    from app.utils import normpath, unzip, check_folder_exists, isIterable, getDate
    
    #setErrorlog('traceback.log')

except:
    IsDebug = 1
    IsDeepDebug = 1
    IsPrintExceptions = 0
    print_exception = None

## =============================
## EXT: POCHTA.RU ONLINE SERVICE
## =============================

def to_base64(str):
    return base64.b64encode(str.encode()).decode("utf-8")

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
_DEFAULT_GOOD_QUALITY_CODE = ['GOOD', 'POSTAL_BOX', 'ON_DEMAND', 'UNDEF_05',]
_DEFAULT_GOOD_VALIDATION_CODE = ['VALIDATED', 'OVERRIDDEN', 'CONFIRMED_MANUALLY']
_DEFAULT_WARNINGS_CODE = ['NOT_VALIDATED_HAS_AMBI', 'NOT_VALIDATED_HAS_UNPARSED_PARTS']

_DEFAULT_FORCED_CODES = [ 
    ('UNDEF_06', 'NOT_VALIDATED_HAS_ASSUMPTION'),
]

_DEFAULT_SEND_DATE = '%Y/%m/%d'

_EXCEPTIONS_LIMIT = 10

# XXX Move these flags into config
IsCheckConnect = 1
IsForcedCleanAddress = 1


class PochtaRuOnline:
    """
        Интеграция с онлайн-сервисом ФГУП "Почта России" (Отправка).
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

        if IsDeepDebug:
            print_to(None, '%s%s' % ('headers:', headers))
            print_to(None, '%s%s' % ('method:', method))
            print_to(None, '%s%s' % ('data:', data))
            print_to(None, '%s%s' % ('URL:', url))

        package = data and json.dumps(data) or None

        is_checked_error = False

        try:
            if not method:
                pass

            elif method == 'GET':
                response = requests.get(url, headers=headers, stream=stream)

            elif method == 'PUT':
                response = requests.put(url, headers=headers, data=package)

            elif method == 'POST':
                response = requests.post(url, headers=headers, data=package, stream=stream)

            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, data=package)

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

        if not self.responseIsValid(response, is_printable=is_printable):
            pass

        return response

    def cleanAddress(self, attrs, **kw):
        """
            Нормализация адреса доставки по отправлению.

            https://otpravka.pochta.ru/specification#/nogroup-normalization_adress

            Аргументы:
                attrs       -- dict, атрибуты запроса (адрес доставки)

            Обязательные атрибуты запроса (ключи attrs):
                id          -- ID запроса (произвольный ключ запроса)
                address     -- оригинальный адрес

            Возврат:
                address     -- dict, нормализованный Адрес доставки
                errors      -- list, список ошибок

            Адрес (str):
                index       -- индекс
                region      -- регион, область
                location    -- микрорайон
                place       -- город, населенный пункт
                street      -- улица
                house       -- дом
                corpus      -- корпус
                room        -- квартира
        """
        self._attrs = attrs

        data = [{
            "id"               : self._get_string("id"),
            "original-address" : self._get_string("address"),
        }]

        response = self.connect('clean_address', data=data, **kw)

        if not self.responseIsValid(response, is_printable=True):
            return None, None
        
        r, errors = self.checkResponse(response)

        if r is None or errors:
            return None, errors
        
        if len(r) == 0 or not (isinstance(r[0], dict) and r[0].keys()):
            return None, None

        address = r[0]
        quality_code = address.get('quality-code')
        validation_code = address.get('validation-code')

        code = quality_code in _DEFAULT_GOOD_QUALITY_CODE and ( \
            validation_code in _DEFAULT_GOOD_VALIDATION_CODE or validation_code in _DEFAULT_WARNINGS_CODE) and 1 or 0

        if IsDebug:
            print_to(None, 'cleanAddress, code[%s]: %s %s' % (code, kw.get('number'), repr(address)))

        if not code and IsForcedCleanAddress:
            if(quality_code, validation_code) in _DEFAULT_FORCED_CODES:
                code = 1

        if not kw.get('forced_address'):
            errors = None if code == 1 else [quality_code, validation_code]
            address = code == 1 and address or None

        return address, errors

    def createOrder(self, attrs, **kw):
        """
            Создание отправления (Заказ).

            Аргументы:
                attrs       -- dict, атрибуты запроса (обязательные параметры отправления)

            Ключевые аргументы:
                cleaned     -- bool, словарь атрибутов метода cleanAddress

            Ответ сервера:
                response    -- list:

            Возврат:
                id          -- int, ID заказа
                errors      -- list, список ошибок
        """
        self._attrs = attrs

        if not kw.get('cleaned'):
            data = [{
                "address-type-to" : self._get_string("address-type-to") or "DEFAULT",       # Тип адреса
                "area-to"         : self._get_string("area-to"),                            # Адрес:Район
                "building-to"     : self._get_string("building-to"),                        # Адрес:Строение
                "corpus-to"       : self._get_string("corpus-to"),                          # Адрес:Корпус
                "fragile"         : self._get_bool("fragile") or False,                     # Признак "Хрупкое"
                "given-name"      : self._get_string("given-name"),                         # Получатель:Имя
                "house-to"        : self._get_string("house-to"),                           # Адрес:Дом
                "index-to"        : self._get_int("index-to"),                              # Адрес:Индекс
                "location-to"     : self._get_string("location-to"),                        # Адрес:Микрорайон
                "mail-category"   : self._get_string("mail-category") or "SIMPLE",          # Категория РПО
                "mail-direct"     : self._get_int("mail-direct") or 643,                    # Код страны
                "mail-type"       : self._get_string("mail-type") or "PARCEL_CLASS_1",      # Вид РПО
                "mass"            : self._get_int("mass"),                                  # Вес РПО (в граммах)
                "middle-name"     : self._get_string("middle-name"),                        # Получатель:Отчество
                "order-num"       : self._get_string("order-num"),                          # Номер заказа отправителя (наш)
                "place-to"        : self._get_string("place-to"),                           # Адрес:Населенный пункт
                "region-to"       : self._get_string("region-to"),                          # Адрес:Область, регион
                "street-to"       : self._get_string("street-to"),                          # Адрес:Улица
                "room-to"         : self._get_string("room-to"),                            # Адрес:Квартира
                "surname"         : self._get_string("surname"),                            # Получатель:Фамилия
                "tel-address"     : self._get_int("phone"),                                 # Телефон получателя
            }]
        else:
            data = [{
                "address-type-to" : "DEFAULT",
                "mail-category"   : self._get_string("category"),
                "mail-type"       : self._get_string("type"),
                "mail-direct"     : 643,
                "mass"            : self._get_int("mass"),
                "tel-address"     : self._get_int("phone"),
            }]

            def _add(words, with_to=False):
                for keyword in words.split(':'):
                    key = keyword
                    if with_to:
                        key = '%s-to' % keyword
                    data[0][key] = attrs.get(keyword)

            _add('area:building:corpus:house:index:location:place:region:street:room', with_to=True)
            _add('given-name:middle-name:surname')

        # ID заказа
        data[0]["id"] = attrs.get('id')
        # Внешний номер заказа
        data[0]["order-num"] = attrs.get('number')
        # Имя файла
        data[0]["comment"] = attrs.get('comment')

        r, errors = self.checkResponse(self.connect('create_order', data=data, **kw))

        if r is None or errors:
            return None, errors

        codes = r.get("result-ids")
        return codes and len(codes) == 1 and codes[0] or None, None

    def searchOrderById(self, id, **kw):
        """
            Поиск заказа с заданным ID.

            Аргументы:
                id          -- str, ID заказа

            Ответ сервера:
                response    -- list:

            Возврат:
                data        -- tuple, (barcode, rate):
                               barcode: str, ШПИ отправления (14)
                               rate: int, Почтовый сбор с НДС (в копейках)
                errors      -- list, список ошибок
        """
        r, errors = self.checkResponse(self.connect('search_order', id=urllib.parse.quote_plus(str(id)), **kw))

        if r is None or errors:
            return None, errors

        barcode = r.get("barcode")
        rate = r.get("mass-rate-with-vat")
        
        return (barcode, rate), None

    def removeOrders(self, ids, **kw):
        """
            Удаление заказов по списку ID.

            Аргументы:
                ids         -- list, список ID заказов (int|str)

            Ответ сервера:
                response    -- list:

            Возврат:
                data        -- list, [id,...]: 
                               ID удаленного заказа
                errors      -- list, список ошибок
        """
        data = [x for x in ids if x]

        if not data:
            return

        r, errors = self.checkResponse(self.connect('remove_orders', data=data, **kw))

        if r is None or errors:
            return None, errors

        data = r.get("result-ids")

        return data, None

    def createBatch(self, ids, send_date=None, **kw):
        """
            Создание партии заказов по списку ID.

            https://otpravka.pochta.ru/specification#/batches-create_batch_from_N_orders

            Аргументы:
                ids         -- list, список ID заказов (int|str)
                send_date   -- str, дата отправки yyyy-MM-dd (опционально)

            Ответ сервера:
                response    -- list, [batches, result-ids]:

                               batches: list, список созданных партий - dict: [batch,...]
                               result-ids: list, список ID заказов, включенных в партию

            Возврат:
                name        -- str, Номер партии
                errors      -- list, список ошибок

            Партия:
                batch-name          -- str, Номер партии
                batch-status        -- str, Статус партии
                batch-status-date   -- str, Дата обновления статуса ("2018-10-08T09:34:58.495Z")
                mail-category       -- str, Категория РПО
                mail-category-text  -- str, Категория РПО (текст)
                mail-type           -- str, Вид РПО
                mail-type-text      -- str, Вид РПО (текст)
                shipment-count      -- int, Количество заказов в партии
                ...
        """
        data = [x for x in ids if x]

        if not data:
            return None, None

        qs = self._make_querystring([('sending-date', send_date),])

        r, errors = self.checkResponse(self.connect('create_batch', data=data, qs=qs, **kw))

        if r is None or errors:
            return None, errors

        batches = r.get("batches")
        ids = r.get("result-ids")

        names = None

        if batches and len(batches) > 0:
            names = [x.get("batch-name") for x in batches]

        return names, None

    batch = createBatch

    def changeBatchSendDate(self, name, date, **kw):
        """
            Установка(смена) даты отправки для партии с заданным номером.

            https://otpravka.pochta.ru/specification#/batches-sending_date_py

            Аргументы:
                name        -- str, Номер партии
                date        -- datetime, Дата отправки

            Ответ сервера:
                response    -- list:

                               error-code: str, Код ошибки
                               f103-sent: bool, Отослана ли электронная версия ф103/ф103п в ОПС?

            Возврат:
                code        -- int, код завершения: 1|0 (success|error)
                errors      -- list, список ошибок
        """
        qs = getDate(date, format=_DEFAULT_SEND_DATE)
        
        r, errors = self.checkResponse(self.connect('change_send_date', name=name, qs=qs, **kw))

        # XXX service returns empty response !!!
        if r is None and not errors:
            return 1, []

        if r is None or errors:
            return None, errors or []

        code = r.get("f103-sent") and 1 or 0
        errors = "error-code" in r and [r["error-code"]] or []

        return code, errors

    change_date = changeBatchSendDate

    def makeBatchF103(self, name, **kw):
        """
            Подготовка и отправка электронной формы 103 для партии с заданным номером.

            https://otpravka.pochta.ru/specification#/documents-checkin

            Аргументы:
                name        -- str, Номер партии

            Ответ сервера:
                response    -- list:

                               error-code: str, Код ошибки
                               f103-sent: bool, Отослана ли электронная версия ф103/ф103п в ОПС?

            Возврат:
                code        -- int, код завершения: 1|0 (success|error)
                errors      -- list, список ошибок
        """
        r, errors = self.checkResponse(self.connect('make_batch_f103', name=name, **kw))

        if r is None or errors:
            return None, errors

        code = r.get("f103-sent") and 1 or 0
        errors = "error-code" in r and [r["error-code"]] or []

        return code, errors

    checkin = makeBatchF103

    def printBatchF103(self, name, destination, **kw):
        """
            Генерация печатной формы 103 для партии с заданным номером.

            https://otpravka.pochta.ru/specification#/documents-create_f103

            Генерирует и возвращает pdf файл с формой Ф103 для указанной партии. 

            Аргументы:
                name        -- str, Номер партии
                destination -- str, маршрут для выгрузки pdf-файла

            Ответ сервера:
                response    -- bytes: контент pdf-файла

            Возврат:
                code        -- int, код завершения: 1|0 (success|error)
        """
        response = self.connect('print_batch_f103', name=name, stream=True, is_image=True, **kw)

        if response is None:
            return 0

        self._unload_image(response, os.path.join(destination, '%s-f103.pdf' % name))

        return 1

    def printOrderForms(self, id, destination, send_date=None, print_type=None, **kw):
        """
            Генерация печатных форм для заказа c заданным ID.

            https://otpravka.pochta.ru/specification#/documents-create_forms

            Генерирует и возвращает pdf файл, который содержит, либо:
            - форму ф7п (посылка, посылка-онлайн, бандероль, курьер-онлайн);
            - форму Е-1 (EMS, EMS-оптимальное, Бизнес курьер, Бизнес курьер экспресс)
            - конверт (письмо заказное).
            Опционально прикрепляются формы: Ф112ЭК (отправление с наложенным платежом), Ф22 (посылка онлайн), 
            уведомление (для заказного письма или бандероли). 

            Аргументы:
                id          -- str, ID заказа
                destination -- str, маршрут для выгрузки pdf-файла
                send_date   -- str, дата отправки yyyy-MM-dd (опционально)
                print_type  -- str, тип печати (опционально)

            Ответ сервера:
                response    -- bytes: контент pdf-файла

            Возврат:
                code        -- int, код завершения: 1|0 (success|error)
        """
        qs = self._make_querystring([('sending-date', send_date), ('print-type', print_type),])

        response = self.connect('print_order_forms', id=id, qs=qs, stream=True, is_image=True, **kw)

        if response is None:
            return 0

        self._unload_image(response, os.path.join(destination, '%s-f7.pdf' % id))

        return 1

    def printOrderFormsBefore(self, id, destination, send_date=None, **kw):
        """
            Генерация печатных форм для заказа c заданным ID (до формирования партии).

            https://otpravka.pochta.ru/specification#/documents-create_forms_backlog

            Генерирует и возвращает pdf файл, который может содержать в зависимости от типа отправления:
            - форму ф7п (посылка, посылка-онлайн, бандероль, курьер-онлайн);
            - форму Е-1 (EMS, EMS-оптимальное, Бизнес курьер, Бизнес курьер экспресс)
            - конверт (письмо заказное).
            Опционально прикрепляются формы: Ф112ЭК (отправление с наложенным платежом), Ф22 (посылка онлайн), 
            уведомление (для заказного письма или бандероли). 

            Аргументы:
                id          -- str, ID заказа
                destination -- str, маршрут для выгрузки pdf-файла
                send_date   -- str, дата отправки yyyy-MM-dd (опционально)

            Ответ сервера:
                response    -- bytes: контент pdf-файла

            Возврат:
                code        -- int, код завершения: 1|0 (success|error)
        """
        qs = self._make_querystring([('sending-date', send_date),])

        response = self.connect('print_order_forms_before', id=id, qs=qs, stream=True, is_image=True, **kw)

        if response is None:
            return 0, None

        self._unload_image(response, os.path.join(destination, '%s.pdf' % id))

        return 1, None

    def printBatchZip(self, name, destination, **kw):
        """
            Генерация пакета документации для партии с заданным номером.

            https://otpravka.pochta.ru/specification#/documents-create_all_docs

            Генерирует и возвращает zip архив с 4-мя файлами:
            Export.xls , Export.csv - список с основными данными по заявкам в составе партии
            F103.pdf - форма ф103 по заявкам в составе партии
            В зависимости от типа и категории отправлений, формируется комбинация из сопроводительных документов 
            в формате pdf ( формы: f7, f112, f22).

            Аргументы:
                name        -- str, Номер партии
                destination -- str, маршрут для выгрузки pdf-файла

            Ответ сервера:
                response    -- bytes: контент zip-файла

            Возврат:
                code        -- int, код завершения: 1|0 (success|error)
        """
        response = self.connect('print_batch_all', name=name, stream=True, is_image=True, **kw)

        if response is None:
            return 0

        src = os.path.join(destination, '%s.zip' % name)

        self._unload_image(response, src)

        unzip(src, destination=name, is_relative=True)

        return 1
    
    all = printBatchZip

    def unload_documents(self, attrs, destination, send_date=None, print_type=None, **kw):
        """
            Выгрузка документов на отгрузку.

            Аргументы:
                attrs       -- dict, {'name' : {id,...}} заказы в разбивке по партиям

            Возврат:
                data        -- list, список обработанных партий
                errors      -- list, список ошибок
        """
        data, errors = [], []
        
        for name in attrs:
            code = self.printBatchF103(name, destination, **kw)
            if not code:
                errors.append('Error in printBatchF103, batch: %s' % name)

            for id in attrs[name]:
                code = self.printOrderForms(id, destination, send_date=send_date, print_type=print_type, **kw)
                if not code:
                    errors.append('Error in printOrderForms, order: %s' % id)

            code = self.printBatchZip(name, destination, **kw)
            if not code:
                errors.append('Error in printBatchZip, batch: %s' % name)
            
            data.append(name)
        
        return data, errors

    def register(self, attrs, **kw):
        """
            Регистрация отправления.

            Аргументы:
                attrs           -- dict, атрибуты запроса (адрес доставки + обязательные параметры отправления)

            Ключевые аргументы:
                forced_address  -- bool, регистрировать отправление при любом коде проверки адреса

            Обязательные атрибуты запроса (ключи attrs):
                id              -- str, ID запроса (произвольный ключ запроса)
                address         -- str, оригинальный адрес
                receiver        -- str, получатель: ФИО через пробел или спецификация отправителя
                contact         -- str, контакт получателя для неименных отправлений
                phone           -- int, телефон получателя
                mass            -- int, масса отправления в граммах
                category        -- str, Категория РПО: SIMPLE|ORDERED|ORDINARY|...COMBINED
                type            -- str, Вид РПО: LETTER_CLASS_1|PARCEL_CLASS_1

            Возврат:
                data            -- tuple, (order_id, barcode, rate):
                                   order_id: str, ID заказа
                                   barcode: str, ШПИ отправления (14)
                                   rate: int, Почтовый сбор с НДС (в копейках)
        """
        address, errors = self.cleanAddress(attrs, **kw)

        if address is None or not address:
            return None, errors or ["ADDRESS IS INVALID"]

        attrs.update(address)

        contact = attrs.get('contact')
        receiver = attrs.get('receiver')

        if contact:
            fio = dict(zip(['surname'], [contact]))
        elif receiver:
            fio = dict(zip('surname:given-name:middle-name'.split(':'), receiver.split()))
        else:
            return None, errors or ["RECEIVER IS EMPTY"]

        attrs.update(fio)

        order_id, errors = self.createOrder(attrs, cleaned=True, **kw)

        if not order_id or errors:
            return None, errors

        r, errors = self.searchOrderById(order_id)

        if not r or errors:
            return None, errors

        barcode, rate = r

        return (order_id, barcode, rate), None

    def unload(self, ids, get_destination, **kw):
        """
            Выгрузить документы.

            Аргументы:
                ids  -- list, список номеров отправлений

            Ключевые аргументы:
                get_destination -- callable, функция маршрутизации каталога выгрузки файлов почтовых отправлений

            Возврат:
                data, errors: (list, list) -- результаты процесса
        """
        data, errors = [], []

        if callable(get_destination):
            root, send_date, destination = get_destination(**kw)

            if IsDebug:
                print_to(None, 'unload destination:%s, root:%s' % (destination, root))

            check_folder_exists(destination, root)

            if not isIterable(ids):
                ids = [ids]

            for id in ids:
                code = self.printBatchZip(id, destination, **kw)
                if not code:
                    break
                data.append(id)

        return data, errors

    @staticmethod
    def send(ids, get_destination, **kw):
        """
            Выполнить отправку F103-архива в ОПС.

            Аргументы:
                ids  -- list, список номеров отправлений

            Ключевые аргументы:
                get_destination -- callable, функция маршрутизации каталога выгрузки файлов почтовых отправлений

            Возврат:
                data, errors: (list, list) -- результаты процесса
        """
        data, errors = [], []

        if callable(get_destination):
            addr_to = kw.get('addr_to')

            if not addr_to:
                return data, ['No address to mail']

            client_title = kw.get('client_title') or ''
            filename = kw.get('filename') or ''

            root, send_date, destination = get_destination(**kw)

            if not isIterable(ids):
                ids = [ids]

            for id in ids:
                source = '%s/%s' % (destination, id)

                if not (os.path.exists(source) and os.path.isdir(source)):
                    break

                subject = '%s%sF103:%s' % (client_title, client_title and ' ' or '', id)
                message = 'Пакет к почтовому отправлению%s. Заказ: %s' % (send_date and ' от %s' % send_date or '', filename or str(id))
                attachments = [(source, x, 'zip') for x in os.listdir(source) if os.path.splitext(x)[1] == '.zip']

                if attachments and send_mail_with_attachment(subject, message, addr_to, attachments=attachments):
                    data.append('%s to %s' % (subject, addr_to))

        return data, errors


def registerPostOnline(mode, case, ids, get_destination=None, **kw):
    """
        Онлайн-регистрация отправлений на портале ПОЧТА РОССИИ.

        Аргументы:
            mode -- int, режим исполнения {1|2|3|4}, default:1
            case -- str, идентификатор типа отправления (ключ учетной записи)
            ids  -- list, список номеров отправлений

        Ключевые аргументы:
            get_destination -- callable, функция маршрутизации каталога выгрузки файлов почтовых отправлений
        
        Дополнительные ключевые аргументы (kw):
            addr_to         -- str[optional]:mode=3,4, список адресов рассылки zip-архива F103 (Emails)
            send_date       -- str[optional]:mode=3,4, дата отправления
            client_title    -- str[optional]:mode=4, наименование клиента в почтовых сообщениях
            filename        -- str[optional]:mode=4, имя файла-заказа

        Возврат:
            data, errors: (list or dict or None, list) -- результаты регистрации в сервисе
    """
    data, errors = [], []

    if not case in postonline:
        return data, ['No account'], res

    if mode in (3, 4) and (get_destination is None or not callable(get_destination)):
        return data, ['No destination'], res

    token, key = postonline[case]

    p = PochtaRuOnline(token, key)

    try:
        if not mode or mode == 1:

            # ----------------------------
            # Создать почтовое отправление
            # ----------------------------

            attrs = {'id' : ids[0]}
            attrs.update(kw)

            data, errors = p.register(attrs, **kw)

        elif mode == 2:

            # --------------
            # Создать партию
            # --------------

            names, errors = p.batch(ids, **kw)
            if names and not errors:
                data = []
                for name in names:
                    code, errors = p.checkin(name)
                    if not (code and not errors):
                        break
                    data.append(name)
            else:
                data = None

        elif mode == 3:

            # -------------------------------
            # Выгрузить документы (форму 103)
            # -------------------------------

            data, errors = p.unload(ids, get_destination, **kw)

        elif mode == 4:

            # ------------------------------------
            # Выполнить отправку F103-архива в ОПС
            # ------------------------------------

            if not IsNoEmail:
                data, errors = p.send(ids, get_destination, **kw)
            else:
                data = ['no emailed: %s' % id for id in ids]

    except Exception as ex:
        if IsPrintExceptions:
            print_to(None, ['', 'PochtaRuOnline.registerPostOnline: [%s,%s] Exception: %s, ids:%s' % (
                mode, case, str(ex), repr(ids))])
            print_exception()

    return data, errors


def changePostOnline(batches, send_date, get_destination=None, **kw):
    """
        Перерегистрация отправлений на портале ПОЧТА РОССИИ.

        Формат данных тега: <PostOnlineBatches>C1-A1:1540;C2-LETTER:251</PostOnlineBatches>

        Аргументы:
            batches   -- str, список номеров партий
            send_date -- datetime, дата отправки в почтовое отделение

        Ключевые аргументы:
            get_destination -- callable, функция маршрутизации каталога выгрузки файлов почтовых отправлений

        Возврат:
            data, errors: (list, list) -- результаты регистрации в сервисе
    """
    data, errors = [], []
    
    try:
        for batch in batches:
            if not batch:
                continue

            case, name = batch.split(':')
            token, key = postonline[case]

            p = PochtaRuOnline(token, key)

            code, errs = p.changeBatchSendDate(name, send_date, is_check_exception=True, **kw)
            if not code:
                break

            errors += errs

            code, errs = p.makeBatchF103(name)
            if not code and 'BATCH_NOT_CHANGED' not in errs:
                break

            errors += errs

            items, errs = p.unload(name, get_destination, send_date=send_date)
            if not items:
                break
            else:
                data += items

            if not IsNoEmail:
                emails, errs = p.send(name, get_destination, send_date=send_date, **kw)

                errors += errs

    except:
        if IsPrintExceptions:
            print_exception()

        raise

    return data, errors
