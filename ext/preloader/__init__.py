# -*- coding: cp1251 -*-

# ---------- #
#   loader   #
# ---------- #

from ..defaults import *

from . import otkrytie

"""
    ������ (��������) �������� ������:
"""

# ----------------------------------------------- #
#   FileType : FileStatus From-To-Error : Attrs   #
# ----------------------------------------------- #

scenario = [
    # -------------
    # ���� ��������
    # -------------
    """
    (0, 'Otkrytie_v1', 
        [], 
        {
            'incoming' : otkrytie.incoming,
            'custom'   : otkrytie.custom,
            'outgoing' : otkrytie.outgoing,
        },
    ),
    """
]
