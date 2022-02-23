# -*- coding: cp1251 -*-

# --------------- #
#   order.check   #
# --------------- #

from app.types.actions import *
from app.types.statuses import *

from ..defaults import *

from . import postbank

"""
    Методы (атрибуты) базового класса.

    Модуль контроля параметров и данных в заказе:
    ---------------------------------------------

        `auto`          --  int, тип контроля:

                            ACTION_ORDER_CHECK_PARAMETERS - параметры
                            ACTION_ORDER_CHECK_DATA - данные

        `custom`        --  func, функция контроля данных

        `outgoing`      --  func, функция генерации файла-квитанции

    Опционально:
    ------------

        `forced`        --  int|str, принудительный вызов модуля для ID файла (FileID)

        `change_status` --  bool, флаг смены статуса файла FileStatus [To|Error]: {1|0}, default: 1
"""

# ----------------------------------------------- #
#   FileType : FileStatus From-To-Error : Attrs   #
# ----------------------------------------------- #

scenario = [
    # ----------
    # ПОЧТА БАНК
    # ----------
    (0, 'PostBank_v1',  
        [STATUS_CREATED, STATUS_PARAMETERS_CHECKED, STATUS_REJECTED_INVALID],
        {
            'auto'     : ACTION_ORDER_CHECK_PARAMETERS, 
            'custom'   : postbank.check_parameters, 
            'outgoing' : postbank.outgoing,
        },
    ),
    (0, 'PostBank_v1',  
        [STATUS_PARAMETERS_CHECKED, STATUS_DATA_CHECKED, STATUS_REJECTED_ERROR],
        {
            'auto'     : ACTION_ORDER_CHECK_DATA,
            'custom'   : postbank.check_data,
            'outgoing' : postbank.outgoing,
        },
    ),
    (0, 'PostBank_ID',  
        [STATUS_CREATED, STATUS_PARAMETERS_CHECKED, STATUS_REJECTED_INVALID],
        {
            'auto'     : ACTION_ORDER_CHECK_PARAMETERS, 
            'custom'   : postbank.check_parameters, 
            'outgoing' : postbank.outgoing,
        },
    ),
    (0, 'PostBank_ID',  
        [STATUS_PARAMETERS_CHECKED, STATUS_DATA_CHECKED, STATUS_REJECTED_ERROR],
        {
            'auto'     : ACTION_ORDER_CHECK_DATA,
            'custom'   : postbank.check_data,
            'outgoing' : postbank.outgoing,
        },
    ),
    (0, 'PostBank_IDM',  
        [STATUS_CREATED, STATUS_PARAMETERS_CHECKED, STATUS_REJECTED_INVALID],
        {
            'auto'     : ACTION_ORDER_CHECK_PARAMETERS, 
            'custom'   : postbank.check_parameters, 
            'outgoing' : postbank.outgoing,
        },
    ),
    (0, 'PostBank_IDM',  
        [STATUS_PARAMETERS_CHECKED, STATUS_DATA_CHECKED, STATUS_REJECTED_ERROR],
        {
            'auto'     : ACTION_ORDER_CHECK_DATA,
            'custom'   : postbank.check_data,
            'outgoing' : postbank.outgoing,
        },
    ),
    (0, 'PostBank_X5',  
        [STATUS_CREATED, STATUS_PARAMETERS_CHECKED, STATUS_REJECTED_INVALID],
        {
            'auto'     : ACTION_ORDER_CHECK_PARAMETERS, 
            'custom'   : postbank.check_parameters, 
            'outgoing' : postbank.outgoing,
        },
    ),
    (0, 'PostBank_X5',  
        [STATUS_PARAMETERS_CHECKED, STATUS_DATA_CHECKED, postbank.status_error_to],
        {
            'auto'     : ACTION_ORDER_CHECK_DATA,
            'custom'   : postbank.check_data,
            'outgoing' : postbank.outgoing,

            'autocommit' : 0,
        },
    ),
    (0, 'PostBank_CL',  
        [STATUS_CREATED, STATUS_PARAMETERS_CHECKED, STATUS_REJECTED_INVALID],
        {
            'auto'     : ACTION_ORDER_CHECK_PARAMETERS, 
            'custom'   : postbank.check_parameters, 
            'outgoing' : postbank.outgoing,
        },
    ),
    (0, 'PostBank_CL',  
        [STATUS_PARAMETERS_CHECKED, STATUS_DATA_CHECKED, postbank.status_error_to],
        {
            'auto'     : ACTION_ORDER_CHECK_DATA,
            'custom'   : postbank.check_data,
            'outgoing' : postbank.outgoing,

            'autocommit' : 0,
        },
    ),
    # ------------
    # Обслуживание
    # ------------
    """
    (0, 'PostBank_v1',
        [199, 0,],
        {
            'auto'     : ACTION_ORDER_CHECK_DATA,
            'custom'   : postbank.dummy,
            'outgoing' : postbank.outgoing,

            'forced'   : 218302,

            'change_status' : 0,
        },
    ),
    """
]
