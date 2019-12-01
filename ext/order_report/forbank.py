# -*- coding: cp1251 -*-

__all__ = ['custom']

from ..xmllib import *

# ------------------------- #

def custom(n, node, logger, saveback, **kw):
    if node.tag == 'FileBody_Record':
        return

# ------------------------- #
