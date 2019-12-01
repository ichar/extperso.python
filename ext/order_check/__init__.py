# -*- coding: cp1251 -*-

# --------------- #
#   order.check   #
# --------------- #

from app.types.actions import *
from app.types.statuses import *

from ..defaults import *

from . import otkrytie
from . import postbank

"""
    ������ (��������) �������� ������.

    ������ �������� ���������� � ������ � ������:
    ---------------------------------------------

        `auto`          --  int, ��� ��������:

                            ACTION_ORDER_CHECK_PARAMETERS - ���������
                            ACTION_ORDER_CHECK_DATA - ������

        `custom`        --  func, ������� �������� ������

        `outgoing`      --  func, ������� ��������� �����-���������

    �����������:
    ------------

        `forced`        --  int|str, �������������� ����� ������ ��� ID ����� (FileID)

        `change_status` --  bool, ���� ����� ������� ����� FileStatus [To|Error]: {1|0}, default: 1
"""

# ----------------------------------------------- #
#   FileType : FileStatus From-To-Error : Attrs   #
# ----------------------------------------------- #

scenario = [
    # -------------
    # ���� ��������
    # -------------
    #(0, 'Otkrytie_v1',  
    #    [STATUS_CREATED, STATUS_PARAMETERS_CHECKED, STATUS_REJECTED_INVALID],
    #    {
    #        'auto'     : ACTION_ORDER_CHECK_PARAMETERS, 
    #        'custom'   : otkrytie.check_parameters, 
    #        'outgoing' : otkrytie.outgoing,
    #    },
    #),
    #(0, 'Otkrytie_v1',  
    #    [STATUS_PARAMETERS_CHECKED, STATUS_DATA_CHECKED, STATUS_REJECTED_ERROR],
    #    {
    #        'auto'     : ACTION_ORDER_CHECK_DATA,
    #        'custom'   : otkrytie.check_data,
    #        'outgoing' : otkrytie.outgoing,
    #    },
    #),
    # ----------
    # ����� ����
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
]
