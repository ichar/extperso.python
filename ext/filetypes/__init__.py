# -*- coding: cp1251 -*-

# ------------- #
#   filetypes   #
# ------------- #

from .otkrytie import *
from .postbank import *

# ------------------------- #

registered_order_filetypes = {
    # -------------
    # БАНК ОТКРЫТИЕ
    # -------------
    #'Otkrytie_v1' : FILETYPE_OTKRYTIE_V1,
    # ---------
    # ПОЧТАБАНК
    # ---------
    'PostBank_v1'  : FILETYPE_POSTBANK_V1,
    'PostBank_ID'  : FILETYPE_POSTBANK_ID,
    'PostBank_IDM' : FILETYPE_POSTBANK_IDM,
    'PostBank_X5'  : FILETYPE_POSTBANK_X5,
    'PostBank_Ref' : FILETYPE_POSTBANK_REFERENCE,
    'PostBank_Lty' : FILETYPE_POSTBANK_LOYALTY,
}
