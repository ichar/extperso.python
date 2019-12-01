# -*- coding: utf-8 -*-

__all__ = ['BaseProcess']

import re

from . import (
    IsDebug, IsDeepDebug, IsTrace, IsDisableOutput, IsPrintExceptions,
    default_print_encoding, default_unicode, default_encoding, default_iso, cr,
    LOCAL_EASY_DATESTAMP, UTC_FULL_TIMESTAMP, DATE_STAMP,
    print_to, print_exception
    )

from app.core import ET, ProcessException, AbstractOrderClass
from app.types.errors import *

## =======================
## CORE: ORDER CHECK CLASS
## =======================

class BaseProcess(AbstractOrderClass):

    _mod_name = 'order_check'

    def _init_state(self, order, attrs=None, factory=None, service=None, set_error=None):
        super(BaseProcess, self)._init_state(order, attrs=attrs, factory=factory, service=service)

        # Tags to custom
        self._tags = hasattr(self, 'mod_tags') and callable(self.mod_tags) and self.mod_tags() or \
            ('FileBody_Record',)

        # Root `set_error` function
        self._set_error = set_error

    def auto_preload(self, node):
        super(BaseProcess, self).auto_preload(node)

        if IsDeepDebug and IsTrace:
            print('>>> order_check.BaseProcess.auto_preload')

    def auto_check_parameters(self, node):
        super(BaseProcess, self).auto_check_parameters(node)

        if IsDeepDebug and IsTrace:
            print('>>> order_check.BaseProcess.auto_check_parameters')

    def auto_check_data(self, node):
        super(BaseProcess, self).auto_check_data(node)

        if IsDeepDebug and IsTrace:
            print('>>> order_check.BaseProcess.auto_check_data')

    def record_iter(self, n, data, **kw):
        """
            Custom output node iterator.

            Arguments:
                n         -- Int, record number
                data      -- bytes, line incoming data (XML)

            Keyword arguments:
                encoding  -- String, data encoding type
                option    -- String, decoder option {ignore|...}

            Class attributes:
                _order    -- Order, order instance
                _logger   -- Func, logger function
                _checker  -- Tuple, current record check results: (keys, codes,)
                _saveback -- Dict, customr's saveback area
                _connect  -- Func, database operational method

            Returns:
                output[node]: bytes.
        """
        encoding = kw.get('encoding') or default_encoding
        option = kw.get('option', 'ignore')

        line = self.decode_input(data, encoding, option=option)
        node = ET.fromstring(line)

        self._logger('--> Record[%s] len:%s' % (n, len(line)))

        line = None
        del line

        # ---------
        # Run check
        # ---------

        self._checker = None

        if self.mod_auto is not None:
            self.mod_auto(node)

        code = self.custom(n, node, **kw)

        if code is not None and self.code != HANDLER_CODE_ERROR or code == HANDLER_CODE_ERROR:
            self.code = code

        return re.sub(r'<\?xml.*?\?>', '', ET.tostring(node, 'unicode')).encode(encoding)

    def run(self):
        self.on_before()

        is_error = False

        try:
            self.main()

        except ProcessException as ex:
            is_error = True
            self._logger('[%s] %s. %s' % (self.class_info(), ex.__class__.__name__, ex), is_error=is_error)

            if IsPrintExceptions:
                print_exception(1)

            if callable(self._set_error):
                self._set_error(self._mod_name, str(ex))

        if not is_error:
            is_error = (self.code == HANDLER_CODE_ERROR or len(self._saveback['errors']) > 0) and True or False

        self.on_after(with_body_update=True, is_error=is_error)

        self.outgoing(is_error)
