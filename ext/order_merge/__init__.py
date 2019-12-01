# -*- coding: cp1251 -*-

# --------------- #
#   order.check   #
# --------------- #

from app.types.actions import *
from app.types.statuses import *

from ..defaults import *

from . import postbank

"""
    Методы (атрибуты) базового класса:
"""

# ----------------------------------------------- #
#   FileType : FileStatus From-To-Error : Attrs   #
# ----------------------------------------------- #

scenario = [
    # ----------
    # ПОЧТА БАНК
    # ----------
    (0, 'PostBank_v1',  
        [STATUS_ON_ORDER_WAIT, STATUS_ON_ARCHIVE_DONE, STATUS_ON_ERROR],
        {
            'clock'      : postbank.clock,
            'activate'   : postbank.activate,
            'deactivate' : postbank.deactivate,
            'custom'     : postbank.custom,
            'filename'   : postbank.make_filename,
            'interval'   : postbank.interval,
        },
    ),
    (0, 'PostBank_X5',  
        [STATUS_ON_ORDER_WAIT, STATUS_ON_ARCHIVE_DONE, STATUS_ON_ERROR],
        {
            'clock'      : postbank.clock,
            'activate'   : postbank.activate,
            'deactivate' : postbank.deactivate,
            'custom'     : postbank.custom,
            'filename'   : postbank.make_filename,
            'interval'   : postbank.interval,
        },
    ),
]
