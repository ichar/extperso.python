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
from app.types.constants import EMPTY_NODE

## ==========================
## CORE: ORDER GENERATE CLASS
## ==========================

class BaseProcess(AbstractOrderClass):

    _mod_name = 'order_generate'

    def _init_state(self, order, attrs=None, factory=None, service=None, set_error=None):
        super(BaseProcess, self)._init_state(order, attrs=attrs, factory=factory, service=service)

        # Tags to custom
        self._tags = hasattr(self, 'mod_tags') and callable(self.mod_tags) and self.mod_tags() or \
            ('FileBody_Record',)

        # Custom break code: -1 - don't call `custom` function
        self._break = None

        # Root `set_error` function
        self._set_error = set_error

    def record_iter(self, n, data, **kw):
        """
            Custom output node iterator.

            Arguments:
                n         -- Int, record number
                data      -- bytes, line incoming data (XML)
                parent    -- Object, parent class

            Keyword arguments:
                encoding  -- String, data encoding type
                option    -- String, decoder option {ignore|...}

            Class attributes:
                _order    -- Order, order instance
                _logger   -- Func, logger function
                _saveback -- Dict, customr's saveback area
                _connect  -- Func, database operational method

            Returns:
                output[node]: bytes.
        """
        if self._break == -1:
            return data

        encoding = kw.get('encoding') or default_encoding
        option = kw.get('option', 'ignore')

        line = self.decode_input(data, encoding, option=option)
        node = ET.fromstring(line)

        self._logger('--> Record[%s] len:%s' % (n, len(line)))

        line = None
        del line

        self._break = self.custom(n, node, **kw)

        if self._break == -1:
            self._logger('--> %s[record_iter]: break[%s]' % (self._mod_name, n), is_warning=True)

        if self._saveback.get(EMPTY_NODE):
            self._empty_nodes += 1
            node = None

        if not node:
            self._logger('--> %s[record_iter]: node is empty[%s]' % (self._mod_name, n), is_warning=True)
            return None

        try:
            return re.sub(r'<\?xml.*?\?>', '', ET.tostring(node, 'unicode')).encode(encoding)
        except Exception as ex:
            raise ProcessException('%s %s, record: %s' % (str(ex), self.order.filename, n))

    def run(self, phase=None):
        self.phase = phase

        self.on_before()

        with_body_update = True
        is_error = False

        try:
            self.main()

        except ProcessException as ex:
            with_body_update = False
            is_error = True

            self.set_exception(ex)

            self._logger('[%s] %s: %s %s' % (self.class_info(), ex.__class__.__name__, self.order.filename, ex), is_error=is_error)

            if IsPrintExceptions:
                print_exception(1)

            if callable(self._set_error):
                self._set_error(self._mod_name, str(ex))

        self.on_after(with_body_update=with_body_update, is_error=is_error)
