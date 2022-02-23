# -*- coding: cp1251 -*-

# ---------------- #
#   order.report   #
# ---------------- #

from app.types.actions import *
from app.types.datatypes import *
from app.types.statuses import *

from ..defaults import *

from . import postbank

"""
    ������ (��������) �������� ������:
"""

# -------------------------------------- #
#   ��������� ���������� ��������������  #
# -------------------------------------- #

command_scenario = {
    'postbank' : 
        {
            'custom'   : postbank.post_report, 
            'outgoing' : postbank.outgoing,
            'tags'     : postbank.tags, 
        },
}

# ------------------------------------------- #
#   FileType : Status From-To-Error : Attrs   #
# ------------------------------------------- #

scenario = [
    # ----------
    # ����� ����
    # ----------
    (1, 'PostBank_v1',
        [STATUS_CARD_ENCASH_FINISHED, STATUS_REPORT_GEN_STARTED,],
        {
            'activate' : postbank.activate,
            'custom'   : postbank.delivery_report, 
            'outgoing' : postbank.send_mail,
            'tags'     : postbank.tags, 

            'keep_history' : 1,
        },
    ),
    (1, 'PostBank_v1',
        [STATUS_READY, STATUS_FINISHED,],
        {
            'custom'   : postbank.post_report, 
            'outgoing' : postbank.outgoing,
            'tags'     : postbank.tags, 
        },
    ),
    # --------------------------------
    # ����� ���� �������������� ������
    # --------------------------------
    (1, 'PostBank_ID',
        [STATUS_CARD_ENCASH_FINISHED, STATUS_REPORT_GEN_STARTED,],
        {
            'activate' : postbank.activate,
            'custom'   : postbank.delivery_report, 
            'outgoing' : postbank.send_mail,
            'tags'     : postbank.tags, 

            'keep_history' : 1,
        },
    ),
    (1, 'PostBank_ID',
        [STATUS_READY, STATUS_FINISHED,],
        {
            'custom'   : postbank.post_report, 
            'outgoing' : postbank.outgoing,
            'tags'     : postbank.tags, 
        },
    ),
    # ------------------------------------
    # ����� ���� �������������� ������ ���
    # ------------------------------------
    (1, 'PostBank_IDM',
        [STATUS_CARD_ENCASH_FINISHED, STATUS_REPORT_GEN_STARTED,],
        {
            'activate' : postbank.activate,
            'custom'   : postbank.delivery_report, 
            'outgoing' : postbank.send_mail,
            'tags'     : postbank.tags, 

            'keep_history' : 1,
        },
    ),
    (1, 'PostBank_IDM',
        [STATUS_READY, STATUS_FINISHED,],
        {
            'custom'   : postbank.post_report, 
            'outgoing' : postbank.outgoing,
            'tags'     : postbank.tags, 
        },
    ),
    # --------------------
    # ����� ���� ���������
    # --------------------
    (1, 'PostBank_X5',
        [STATUS_CARD_ENCASH_FINISHED, STATUS_REPORT_GEN_STARTED,],
        {
            'activate' : postbank.activate,
            'custom'   : postbank.delivery_report, 
            'outgoing' : postbank.send_mail,
            'tags'     : postbank.tags, 

            'keep_history' : 1,
        },
    ),
    (1, 'PostBank_X5',
        [STATUS_READY, STATUS_FINISHED,],
        {
            'custom'   : postbank.post_report, 
            'outgoing' : postbank.outgoing,
            'tags'     : postbank.tags, 
        },
    ),
    # -------------------
    # ����� ���� ��������
    # -------------------
    (1, 'PostBank_CL',
        [STATUS_CARD_ENCASH_FINISHED, STATUS_REPORT_GEN_STARTED,],
        {
            'activate' : postbank.activate,
            'custom'   : postbank.delivery_report, 
            'outgoing' : postbank.send_mail,
            'tags'     : postbank.tags, 

            'keep_history' : 1,
        },
    ),
    (1, 'PostBank_CL',
        [STATUS_READY, STATUS_FINISHED,],
        {
            'custom'   : postbank.post_report, 
            'outgoing' : postbank.outgoing,
            'tags'     : postbank.tags, 
        },
    ),
    # ------------
    # ������������
    # ------------
    """
    (1, 'PostBank_v1',
        [STATUS_FINISHED, 0,],
        {
            'custom'   : postbank.delivery_report, 
            'outgoing' : postbank.send_mail,
            'tags'     : postbank.tags, 

            'change_status' : 0,

            'forced'   : 286425,
        },
    ),
    (1, 'PostBank_v1',
        [198, 0,],
        {
            'custom'   : postbank.post_report, 
            'outgoing' : postbank.outgoing,
            'tags'     : postbank.tags, 

            'change_status' : 0,

            'forced'   : 295707,
        },
    ),
    #
    # ������������� ������� ���� ����� ����������
    #
    (1, 'PostBank_ID',
        [STATUS_CARD_ENCASH_FINISHED, STATUS_FINISHED,],
        {
            'custom'   : None, 
        },
    ),
    """
]
