# -*- coding: cp1251 -*-

__all__ = ['custom']

from ..xmllib import *

# ------------------------- #

def custom(n, node, logger, saveback, **kw):
    if node.tag != 'FileBody_Record':
        return

    arep_record = ET.SubElement(node, 'AREP_Record')

    record = FMT_XmlTag(arep_record, 'Record')
    FMT_XmlTag(record, 'CLIENTID', getTag(node, 'CLIENTID'))
    FMT_XmlTag(record, 'DocumentNumber', getTag(node, 'DocumentNumber'))
    FMT_XmlTag(record, 'Client', getTag(node, 'CardholderName'))
    FMT_XmlTag(record, 'Address', getTag(node, 'FactAddress'))

    logger('--> Generate Node: %s' % arep_record.tag, force=True)

# ------------------------- #
