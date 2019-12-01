# -*- coding: utf-8 -*-

##  ==================
##  DataType Constants
##  ==================

DATA_TYPE_ABSTRACT = None

##  =====================================
##  Customer Incoming FileOrder DataTypes
##  =====================================

DATA_TYPE_TAG    = 'TAG'
DATA_TYPE_FIELD  = 'FIELD'
DATA_TYPE_BIN    = 'BIN'

##  ========================
##  Customer Field DataTypes
##  ========================

DATA_TYPE_EMPTY     = 0x00
DATA_TYPE_TEXT      = 0x01
DATA_TYPE_TEXT_N    = 0x02
DATA_TYPE_TEXT_NS   = 0x03
DATA_TYPE_TEXT_AN   = 0x04
DATA_TYPE_TEXT_AS   = 0x05
DATA_TYPE_TEXT_ANS  = 0x06
DATA_TYPE_INT       = 0x07
DATA_TYPE_INTEGER   = 0x08
DATA_TYPE_NUMBER    = 0x09
DATA_TYPE_FLOAT     = 0x0A
DATA_TYPE_DATETIME  = 0x0B
DATA_TYPE_TEXT_A    = 0x0C
DATA_TYPE_TEXT_ANC  = 0x0D

DATA_TYPE_VALID_TEXT = (DATA_TYPE_TEXT, DATA_TYPE_TEXT_N, DATA_TYPE_TEXT_NS, DATA_TYPE_TEXT_AN, DATA_TYPE_TEXT_AS, DATA_TYPE_TEXT_ANS, DATA_TYPE_TEXT_A, DATA_TYPE_TEXT_ANC,)

##  ======================
##  Public Perso DataTypes
##  ======================

DATA_PERSO_TYPE_DEFAULT      = r'.*'
DATA_PERSO_TYPE_PAN16        = r'\d{16}'
DATA_PERSO_TYPE_PAN19        = r'\d{19}'
DATA_PERSO_TYPE_PANWIDE16    = r'\d{4}\s\d{4}\s\d{4}\s\d{4}'
DATA_PERSO_TYPE_PANWIDE19    = r'\d{4}\s\d{4}\s\d{4}\s\d{4}\s\d{3}'
DATA_PERSO_TYPE_EXPDATE      = r'\d{2}\d{2}'
DATA_PERSO_TYPE_EXPIREDATE   = r'\d{2}\/\d{2}'
DATA_PERSO_TYPE_DATE_MMYY    = r'\d{2}\/\d{2}'
DATA_PERSO_TYPE_BIN          = r'\d{6}'
DATA_PERSO_TYPE_POSTINDEX    = r'\d{6}'
# 'ЁЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮQWERTYUIOPASDFGHJKLZXCVBNM 1234567890/.,&-'+''''
DATA_PERSO_TYPE_EMBOSSNAME   = r'[\d\w\s\/\.\,\&\-\']+'

crlf = '\r\n'
cr = '\n'
