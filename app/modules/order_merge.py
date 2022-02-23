# -*- coding: utf-8 -*-

__all__ = ['BaseProcess']

import re

from . import (
    IsDebug, IsDeepDebug, IsTrace, IsDisableOutput, IsPrintExceptions,
    default_print_encoding, default_unicode, default_encoding, default_iso, cr,
    LOCAL_EASY_DATESTAMP, UTC_FULL_TIMESTAMP, DATE_STAMP,
    print_to, print_exception
    )

from app.core import ET, ProcessException, AbstractMergeClass
from app.types.errors import *

## =======================
## CORE: ORDER MERGE CLASS
## =======================

class BaseProcess(AbstractMergeClass):

    _mod_name = 'order_merge'

    def _init_state(self, filetype, orders, attrs=None, factory=None, service=None, set_error=None):
        super(BaseProcess, self)._init_state(filetype, orders, attrs=attrs, factory=factory, service=service)

        # Tags to custom
        self._tags = hasattr(self, 'mod_tags') and callable(self.mod_tags) and self.mod_tags() or \
            ('FileBody_Record',)

        self.interval = attrs.get('interval')

        # Root `set_error` function
        self._set_error = set_error

    def activate(self):
        """
            Check params before start and activate process
        """
        if not (self.mod_clock is not None and callable(self.mod_clock)):
            return False
        if not (self.mod_activate is not None and callable(self.mod_activate)):
            return False

        # Check alarm clock
        key = self.interval and callable(self.interval) and self.interval() or self.interval
        if not self.mod_clock(self.service_config(key)):
            return False

        # Set a new order filename with the given status
        self._base_filename, self._status, self._encoding = self.mod_activate(self._orders, self._saveback)

        # -----
        # Start
        # -----

        self.on_activate()

        return True

    def deactivate(self):
        # ------
        # Finish
        # ------

        # Check new orders
        self.mod_deactivate(self._files, self._saveback)

        self.on_deactivate()

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
                _logger   -- Func, logger function
                _saveback -- Dict, customr's saveback area
                _connect  -- Func, database operational method
                _filename -- String, a new order filename

            Returns:
                output[node]: bytes.
        """
        encoding = kw.get('encoding') or self._encoding or default_encoding
        option = kw.get('option', 'ignore')

        line = self.decode_input(data, encoding, option=option)
        node = ET.fromstring(line)

        self._logger('--> Record[%s] len:%s' % (n, len(line)))

        line = None
        del line

        # ---------
        # Run merge
        # ---------

        code = self.custom(n, node, **kw)

        # Current output file key
        key = self._saveback.get('key')

        # Switch filename
        self.switch_file(key, inc=True)

        return re.sub(r'<\?xml.*?\?>', '', ET.tostring(node, 'unicode')).encode(encoding), self._files[key]['fo']

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

        is_error = self.code == HANDLER_CODE_ERROR and True or False

        self.on_after(is_error=is_error)
