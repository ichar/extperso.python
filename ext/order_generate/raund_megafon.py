# -*- coding: cp1251 -*-

__all__ = ['custom']

from ..xmllib import *

# ------------------------- #

def custom(n, node, logger, saveback, **kw):
    if node.tag != 'FileBody_Record':
        return

    chip_record = ET.SubElement(node, 'CHIP_Record')

    chip_record.text = '%s%s%s%s%s' % ( 
        FMT_PinTag('RECID', getTag(node, 'FileRecNo')),
        FMT_PinTag('MTrack1', getTag(node, 'Track1')),
        FMT_PinTag('MTrack2', getTag(node, 'Track2')),
        FMT_PinTag('CVV2', getTag(node, 'CVV2')),
        getTag(node, 'ParsedDump'),
    )

    logger('--> Generate Node: %s' % chip_record.tag)

# ------------------------- #
