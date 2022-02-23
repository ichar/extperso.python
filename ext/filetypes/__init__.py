# -*- coding: cp1251 -*-

# ------------- #
#   filetypes   #
# ------------- #

from .postbank import *

# ------------------------- #

registered_order_filetypes = {
    # ---------
    # ПОЧТАБАНК
    # ---------
    'PostBank_v1'  : FILETYPE_POSTBANK_V1,
    'PostBank_ID'  : FILETYPE_POSTBANK_ID,
    'PostBank_IDM' : FILETYPE_POSTBANK_IDM,
    'PostBank_X5'  : FILETYPE_POSTBANK_X5,
    'PostBank_CL'  : FILETYPE_POSTBANK_CYBERLAB,
    'PostBank_Ref' : FILETYPE_POSTBANK_REFERENCE,
    'PostBank_Lty' : FILETYPE_POSTBANK_LOYALTY,
}
