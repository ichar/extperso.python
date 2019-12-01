# -*- coding: utf-8 -*-

__all__ = ['BaseProcess']

from . import (
    IsDebug, IsDeepDebug, IsDisableOutput, IsPrintExceptions,
    default_print_encoding, default_unicode, default_encoding, default_iso, cr,
    LOCAL_EASY_DATESTAMP, UTC_FULL_TIMESTAMP, DATE_STAMP,
    print_to, print_exception
    )

from app.core import ET, ProcessException, AbstractOrderClass
from app.types.errors import *

## ========================
## CORE: ORDER REPORT CLASS
## ========================

class BaseProcess(AbstractOrderClass):

    _mod_name = 'order_report'

    def _init_state(self, order, attrs=None, factory=None, service=None, set_error=None):
        super(BaseProcess, self)._init_state(order, attrs=attrs, factory=factory, service=service)

        # Tags to custom
        self._tags = hasattr(self, 'mod_tags') and callable(self.mod_tags) and self.mod_tags() or \
            ('FileInfo', 'FileBody_Record', 'ProcessInfo',)

        self._saveback['reports'] = {}

        # Root `set_error` function
        self._set_error = set_error

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
                _logger   -- Func, logger function

            Returns:
                output[value]: bytes encoded with the given `encoding`.
            
            Undefined charmaps will be forced ignored!!!
        """
        encoding = kw.get('encoding') or default_encoding
        option = kw.get('option') or 'ignore'

        try:
            line = self.decode_input(data, encoding, option=option)
        except:
            raise

        node = ET.fromstring(line)

        self._logger('--> Record[%s] len:%s' % (n, len(line)))

        line = None
        del line

        value = self.custom(n, node, **kw)

        return value and value.encode(default_encoding) or None

    def genXml(self):
        if self.code == HANDLER_CODE_ERROR:
            return

        output = None
        if self.mod_output is not None and callable(self.mod_output):
            output = self.mod_output(self._order, self._logger)

        self.generate(output)
        
        if IsDeepDebug:
            self._logger('>>> %s' % output)

    main = genXml

    def run(self):
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

        is_error = self.code == HANDLER_CODE_ERROR and True or False

        self.on_after(is_error=is_error)

        self.outgoing(is_error)
