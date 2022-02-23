# -*- coding: utf-8 -*-

__all__ = ['BaseIncomingLoader', 'BaseReferenceLoader']

import re

from . import (
    IsDebug, IsDeepDebug, IsTrace, IsDisableOutput, IsPrintExceptions,
    default_print_encoding, default_unicode, default_encoding, default_iso, cr,
    LOCAL_EASY_DATESTAMP, UTC_FULL_TIMESTAMP, DATE_STAMP,
    print_to, print_exception
    )

from app.core import ET, ProcessException, AbstractIncomingLoaderClass, AbstractReferenceLoaderClass
from app.types.errors import *

## =======================
## CORE: DATA LOADER CLASS
## =======================

class BaseIncomingLoader(AbstractIncomingLoaderClass):

    _mod_name = 'incoming_loader'

    def _init_state(self, attrs=None, service=None, set_error=None):
        super(BaseIncomingLoader, self)._init_state(attrs=attrs, service=service)

        self.check()

        # Root `set_error` function
        self._set_error = set_error

    def check(self):
        fieldset = self.ordered_fieldset()

        if IsDeepDebug:
            print('fieldset:\n%s' % '\n'.join([repr(fieldset[x]) for x in list(fieldset.keys())]))

    def record_iter(self, n, data, **kw):
        """
            Custom output node iterator.

            Arguments:
                n        -- Int, record number
                data     -- String, line incoming data (XML)

            Keyword arguments:
                encoding -- String, data encoding type
                option   -- String, decoder option {ignore|...}
                fieldset -- Dict, filetype fields descriptor [fieldset]
                keys     -- Tuple, line fields list

            Class attributes:
                _logger   -- Func, logger function
                _saveback -- Dict, customr's saveback area
                _connect  -- Func, database operational method

            Returns:
                output[node]: node as str (unicode).
        """
        encoding = kw.get('encoding') or default_encoding
        option = kw.get('option', 'ignore')

        line = self.decode_input(data, encoding, option=option)
        node = ET.fromstring(line)

        self._logger('--> Record[%s] len:%s' % (n, len(line)))

        line = None
        del line

        code = self.custom(n, node, **kw)
        if code is not None and self.code != HANDLER_CODE_ERROR or code == HANDLER_CODE_ERROR:
            self.code = code

        return re.sub(r'<\?xml.*?\?>', '', ET.tostring(node, 'unicode'))

    def run(self, statuses):
        self.on_before()

        try:
            self.main()

        except ProcessException as ex:
            is_error = True

            self._logger('[%s] %s. %s' % (self.class_info(), ex.__class__.__name__, ex), is_error=is_error)

            if IsPrintExceptions:
                print_exception(1)

            if callable(self._set_error):
                self._set_error(self._mod_name, str(ex))

        is_error = (self.code == HANDLER_CODE_ERROR or len(self._saveback['errors']) > 0) and True or False

        self.on_after(statuses, with_body_update=True, is_error=is_error)

        self.outgoing(is_error)


class BaseReferenceLoader(AbstractReferenceLoaderClass):

    _mod_name = 'reference_loader'

    def _init_state(self, attrs=None, service=None, set_error=None):
        super(BaseReferenceLoader, self)._init_state(attrs=attrs, service=service)

        self.check()

    def check(self):
        fieldset = self.ordered_fieldset()

        if IsDeepDebug:
            print('fieldset:\n%s' % '\n'.join([repr(fieldset[x]) for x in list(fieldset.keys())]))

    def record_iter(self, n, data, **kw):
        """
            Custom output node iterator.

            Arguments:
                n        -- Int, record number
                data     -- Dict, line's data

            Keyword arguments:
                encoding -- String, data encoding type
                option   -- String, decoder option {ignore|...}
                fieldset -- Dict, filetype fields descriptor [fieldset]
                keys     -- Tuple, line fields list

            Class attributes:
                _logger   -- Func, logger function
                _saveback -- Dict, customr's saveback area
                _connect  -- Func, database operational method

            Custom returns:
                code: HANDLER_CODE_UNDEFINED | HANDLER_CODE_ERROR

            Returns:
                None
        """
        encoding = kw.get('encoding') or default_encoding
        option = kw.get('option') or 'ignore'

        self._logger('--> Record[%s] len:%s' % (n, len(data)))

        code = self.custom(n, data, **kw)
        if code is not None and self.code != HANDLER_CODE_ERROR or code == HANDLER_CODE_ERROR:
            self.code = code

        return None

    def run(self):
        self.on_before()

        try:
            self.main()

        except ProcessException as ex:
            is_error = True

            self.set_exception(ex)

            self._logger('[%s] %s. %s' % (self.class_info(), ex.__class__.__name__, ex), is_error=is_error)

            if IsPrintExceptions:
                print_exception(1)

            if callable(self._set_error):
                self._set_error(self._mod_name, str(ex))

        is_error = (self.code == HANDLER_CODE_ERROR or len(self._saveback['errors']) > 0) and True or False

        self.on_after(is_error=is_error)

        self.outgoing(is_error)
