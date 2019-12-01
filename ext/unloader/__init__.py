# -*- coding: cp1251 -*-

# ------------ #
#   unloader   #
# ------------ #

from app.types.actions import *
from app.types.datatypes import *
from app.types.statuses import *

from ..defaults import *

from . import postbank

"""
    Методы (атрибуты) базового класса:
"""

# ------------------------------------------- #
#   FileType : Status From-To-Error : Attrs   #
# ------------------------------------------- #

scenario = [
    # ----------
    # ПОЧТА БАНК
    # ----------
    (0, 'PostBank_v1',
        [STATUS_REPORT_GEN_STARTED, STATUS_ON_READY_ACT_GEN,], # STATUS_REPORT_GEN_FINISHED
        {
            'custom'   : postbank.sort_report, 
            'tags'     : postbank.tags, 
            'output'   : postbank.csv, 
            'mode'     : 'ab', 
            'EOL'      : crlf,

            'keep_history' : 1,
        },
    ),
    (0, 'PostBank_ID',
        [STATUS_REPORT_GEN_STARTED, STATUS_ON_READY_ACT_GEN,], # STATUS_REPORT_GEN_FINISHED
        {
            'custom'   : postbank.sort_report, 
            'tags'     : postbank.tags, 
            'output'   : postbank.csv, 
            'mode'     : 'ab', 
            'EOL'      : crlf,

            'keep_history' : 1,
        },
    ),
    (0, 'PostBank_IDM',
        [STATUS_REPORT_GEN_STARTED, STATUS_ON_READY_ACT_GEN,], # STATUS_REPORT_GEN_FINISHED
        {
            'custom'   : postbank.sort_report, 
            'tags'     : postbank.tags, 
            'output'   : postbank.csv, 
            'mode'     : 'ab', 
            'EOL'      : crlf,

            'keep_history' : 1,
        },
    ),
    (0, 'PostBank_X5',
        [STATUS_REPORT_GEN_STARTED, STATUS_ON_READY_ACT_GEN,], # STATUS_REPORT_GEN_FINISHED
        {
            'custom'   : postbank.sort_report, 
            'tags'     : postbank.tags, 
            'output'   : postbank.csv, 
            'mode'     : 'ab', 
            'EOL'      : crlf,

            'keep_history' : 1,
        },
    ),
    # ------------
    # Обслуживание
    # ------------
    """
    (0, 'PostBank_v1',
        [STATUS_FINISHED, 0,],
        {
            'custom'   : postbank.sort_report, 
            'tags'     : postbank.tags, 
            'output'   : postbank.csv, 
            'mode'     : 'ab', 
            'EOL'      : crlf,
            'change_status' : 0,
        },
    ),
    (0, 'PostBank_v1',
        [199, STATUS_FINISHED,],
        {
            'custom'   : postbank.sort_report, 
            'tags'     : postbank.tags, 
            'output'   : postbank.csv, 
            'mode'     : 'ab', 
            'EOL'      : crlf,
        },
    ),
    (0, 'PostBank_v1',
        [198, 0,],
        {
            'activate' : postbank.check_access, 
            'forced'   : 286920,
            'change_status' : 0,
        },
    ),
    """
]
