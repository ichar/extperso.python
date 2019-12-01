# -*- coding: utf-8 -*-

import re
from datetime import datetime

product_version = '1.31 (Windows Service), 2019-11-15 with cp1251 (Python3)'

#########################################################################################

#   -------------
#   Default types
#   -------------

DEFAULT_LANGUAGE = 'ru'
DEFAULT_LOG_MODE = 1
DEFAULT_PER_PAGE = 10
DEFAULT_ADMIN_PER_PAGE = 20
DEFAULT_PAGE = 1
DEFAULT_UNDEFINED = '---'
DEFAULT_DATE_FORMAT = ('%d/%m/%Y', '%Y-%m-%d',)
DEFAULT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_DATETIME_INLINE_FORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_DATETIME_PERSOLOG_FORMAT = ('%Y%m%d', '%Y-%m-%d %H:%M:%S',)
DEFAULT_DATETIME_SDCLOG_FORMAT = ('%d.%m.%Y', '%d.%m.%Y %H:%M:%S,%f',)
DEFAULT_DATETIME_EXCHANGELOG_FORMAT = ('%d.%m.%Y', '%d.%m.%Y %H:%M:%S,%f',)
DEFAULT_HTML_SPLITTER = ':'

USE_FULL_MENU = True

MAX_TITLE_WORD_LEN = 50
MAX_XML_BODY_LEN = 1024*100
MAX_XML_TREE_NODES = 100
MAX_LOGS_LEN = 999
MAX_UNRESOLVED_LINES = (10, 99, 9)
MAX_CARDHOLDER_ITEMS = 9999
EMPTY_VALUE = '...'

COMPLETE_STATUSES = (62, 64, 98, 197, 198, 201, 202, 203, 255,)
