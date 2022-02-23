# -*- coding: utf-8 -*-

__all__ = ['BasePreloader']

import re

from . import (
    IsDebug, IsDeepDebug, IsTrace, IsDisableOutput, IsPrintExceptions,
    default_print_encoding, default_unicode, default_encoding, default_iso, cr,
    LOCAL_EASY_DATESTAMP, UTC_FULL_TIMESTAMP, DATE_STAMP,
    print_to, print_exception
    )

from app.core import ET, ProcessException, AbstractPreloaderClass
from app.types import *

## =============================
## CORE: OPENWAY PRELOADER CLASS
## =============================

class BaseOpenwayPreloaderClass(AbstractPreloaderClass):

    _mod_name = 'preloader'

    def _init_state(self, attrs=None, service=None, set_error=None):
        if IsDeepDebug:
            print('BaseOpenwayPreloaderClass initstate')

        super(BaseOpenwayPreloaderClass, self)._init_state(attrs=attrs, service=service)

        self._format = FILE_FORMAT_PM_PRS

        # Root `set_error` function
        self._set_error = set_error

    def custom(self, filename):
        """
            Run custom
        """
        tree = ET.parse(filename)
        root = tree.getroot()
        
        code = None
        if self.mod_custom is not None and callable(self.mod_custom):
            code = self.mod_custom(root, self._logger, self._saveback, 
                actions=self.actions,
                filename=filename,
                service=self.service,
                tmp=self.tmp_folder,
            )

            self.code = HANDLER_CODE_SUCCESS

        return code

    def run(self):
        self.on_before()

        is_error = False

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

        if not is_error:
            is_error = (self.code == HANDLER_CODE_ERROR or self._total == 0) and True or False

        self.on_after(is_error=is_error)
