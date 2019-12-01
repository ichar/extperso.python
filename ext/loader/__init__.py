# -*- coding: cp1251 -*-

# ---------- #
#   loader   #
# ---------- #

from app.types.statuses import *

from ..defaults import *

from . import otkrytie
from . import postbank

"""
    Методы (атрибуты) базового класса:
"""

# ----------------------------------------------- #
#   FileType : FileStatus From-To-Error : Attrs   #
# ----------------------------------------------- #

scenario = [
    # -------------
    # БАНК ОТКРЫТИЕ
    # -------------
    #(0, 'Otkrytie_v1', 
    #    [STATUS_EMPTY, STATUS_CREATED, STATUS_REJECTED_INVALID], 
    #    {
    #        'incoming'  : otkrytie.incoming,
    #        'validator' : otkrytie.validator,
    #    },
    #),
    # ----------
    # ПОЧТА БАНК
    # ----------
    (0, 'PostBank_Lty', 
        [STATUS_ON_INCOMING],
        {
            'reference' : postbank.loyalty, 
            'custom'    : postbank.loyalty_custom, 
            'outgoing'  : postbank.loyalty_outgoing, 
        },
    ),
    (0, 'PostBank_Ref', 
        [STATUS_ON_INCOMING],
        {
            'reference' : postbank.reference, 
            'custom'    : postbank.reference_custom, 
            'validator' : postbank.validator,
            'outgoing'  : postbank.reference_outgoing, 
        },
    ),
    (0, 'PostBank_v1', 
        [STATUS_EMPTY, STATUS_CREATED, STATUS_REJECTED_INVALID], 
        {
            'incoming'  : postbank.incoming,
            'validator' : postbank.validator,
            'outgoing'  : postbank.outgoing,
        },
    ),
    (0, 'PostBank_ID', 
        [STATUS_EMPTY, STATUS_CREATED, STATUS_REJECTED_INVALID], 
        {
            'incoming'  : postbank.incoming_individual_design,
            'validator' : postbank.validator,
            'outgoing'  : postbank.outgoing,
        },
    ),
    (0, 'PostBank_IDM', 
        [STATUS_EMPTY, STATUS_CREATED, STATUS_REJECTED_INVALID], 
        {
            'incoming'  : postbank.incoming_nspk_individual_design,
            'validator' : postbank.validator,
            'outgoing'  : postbank.outgoing,
        },
    ),
    (0, 'PostBank_X5', 
        [STATUS_EMPTY, STATUS_CREATED, STATUS_REJECTED_INVALID], 
        {
            'incoming'  : postbank.incoming_X5,
            'validator' : postbank.validator,
            'outgoing'  : postbank.outgoing,
        },
    ),
]
