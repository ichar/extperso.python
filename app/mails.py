﻿# -*- coding: utf-8 -*-

"""
mails.py
========

This module provides an easy way to send email with docx-attachment.
"""

__all__ = ['SendMail', 'send_materials_order', 'send_test', 'send_simple_mail', 'send_mail_with_attachment']

import io
import sys
import smtplib

from email import encoders
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.header import Header

try:
    from config import (
        IsDebug, IsPrintExceptions, print_exception, print_to, cr,
        default_unicode, default_encoding, default_print_encoding
    )
except:
    IsDebug = 1
    IsPrintExceptions = 0
    print_exception = None
    print_to = None
    cr = '\n'

    default_unicode = 'utf-8'
    default_encoding = 'cp1251'
    default_print_encoding = 'cp866'

DEAULT_MAILROBOT = 'mailrobot@rosan.ru'

try:
    from config import smtphosts, email_address_list
except:
    smtphost1 = {
        'host'      : '172.19.13.5', 
        'port'      : 25,
        'connect'   : None,
        'tls'       : 0,
        'method'    : 1,
        'from'      : 'mailrobot@rosan.ru',
        'debug'     : 0,
    }

    smtphost2 = {
        'host'      : 'smtp-mail.outlook.com', 
        'port'      : 587,
        'connect'   : {'login' : "support@expresscard.ru", 'password' : "Rof86788"},
        'tls'       : 1,
        'method'    : 2,
        'from'      : 'support@expresscard.ru',
        'debug'     : 0,
    }

    smtphosts = (smtphost1, smtphost2)

    email_address_list = {
        'mailrobot' : DEAULT_MAILROBOT
    }

smtphost = None

## ============================== ##


def to_ascii(s):
    return s and s.encode('ascii', 'ignore').decode('ascii') or ''


class SendMail(object):
    """
        SMTP Mail Sender.

        MIME types for attachments:
            octet-stream 
            application/msword
            application/vnd.ms-excel 
            application/pdf 
            application/vnd.ms-powerpoint 
            image/png
    """

    def __init__(self, subject, **kw):
        self._canal = kw.get('canal')

        self._set_smtp()

        self._subject = subject
        self._from = kw.get('addr_from') or email_address_list['mailrobot']
        self._to = to_ascii(kw.get('addr_to'))
        self._cc = to_ascii(kw.get('addr_cc'))

        self._msg = None

    def _set_smtp(self):
        global smtphost

        self._canal = self._canal is not None and self._canal + 1 or 0
        if self._canal > len(smtphosts) - 1:
            smtphost = None
            return

        smtphost = smtphosts[self._canal]
        email_address_list['mailrobot'] = smtphost.get('from') or DEAULT_MAILROBOT

        if IsDebug and callable(print_to):
            print_to(None, 'smtphost:%s, port:%s\n' % (smtphost['host'], smtphost['port']))

    @property
    def canal(self):
        return self._canal

    def create_message(self, html):
        msg = MIMEMultipart()
        msg['Subject'] = self._subject
        msg['From'] = self._from
        msg['To'] = self._to
        
        if self._cc:
            msg['CC'] = self._cc

        if html:
            msg.attach(MIMEText(html, 'html'))

        self._msg = msg

    def attach_docx(self, document, filename):
        if not self._msg:
            return

        if isinstance(document, bytes):
            fp = io.BytesIO(document)
        else:
            fp = io.BytesIO()
            document.save(fp)

        ctype = 'application/msword'
        
        maintype, subtype = ctype.split('/', 1)
        base = MIMEBase(maintype, subtype)
        fp.seek(0)
        base.set_payload(fp.read())
        encoders.encode_base64(base)

        header = Header('%s.doc' % filename, charset=default_unicode)
        base.add_header('Content-Disposition', 'attachment', filename='%s' % header.encode())

        self._msg.attach(base)

        fp.close()

    attach_doc = attach_docx

    def attach_xlsx(self, document, filename):
        if not self._msg:
            return

        if isinstance(document, bytes):
            fp = io.BytesIO(document)
        else:
            fp = io.BytesIO()
            document.save(fp)

        ctype = 'application/vnd.ms-excel'
        
        maintype, subtype = ctype.split('/', 1)
        base = MIMEBase(maintype, subtype)
        fp.seek(0)
        base.set_payload(fp.read())
        encoders.encode_base64(base)

        header = Header('%s.xls' % filename, charset=default_unicode)
        base.add_header('Content-Disposition', 'attachment', filename='%s' % header.encode())
        
        self._msg.attach(base)

        fp.close()

    attach_xls = attach_xlsx

    def attach_zip(self, source, filename):
        if not self._msg:
            return

        ctype = 'application/zip'
        
        maintype, subtype = ctype.split('/', 1)
        base = MIMEBase(maintype, subtype)
        with open('%s/%s' % (source, filename), 'rb') as fp:
            base.set_payload(fp.read())
        encoders.encode_base64(base)

        header = Header(filename, charset=default_unicode)
        base.add_header('Content-Disposition', 'attachment', filename='%s' % header.encode())

        self._msg.attach(base)

        fp.close()

    def attach_csv(self, source, filename):
        if not self._msg:
            return

        ctype = 'application/octet-stream'
        
        maintype, subtype = ctype.split('/', 1)
        base = MIMEBase(maintype, subtype)
        with open('%s/%s' % (source, filename), 'rb') as fp:
            base.set_payload(fp.read())
        encoders.encode_base64(base)

        header = Header(filename, charset=default_unicode)
        base.add_header('Content-Disposition', 'attachment', filename='%s' % header.encode())

        self._msg.attach(base)

        fp.close()

    def attach_any(self, source, filename):
        if not self._msg:
            return

        with open(source, 'rb') as fi:
            part = MIMEApplication(fi.read(), Name=basename(filename))

        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(filename)
        self._msg.attach(part)

        fp.close()

    def send(self, with_raise=None):
        code = 0

        while not code and smtphost is not None and smtphost.get('host'):
            smtp = None

            try:
                smtp = smtplib.SMTP(smtphost['host'], smtphost['port'])
                if smtphost.get('tls'):
                    smtp.ehlo()
                    smtp.starttls()
                if smtphost.get('connect'):
                    smtp.ehlo()
                    smtp.login(smtphost['connect']['login'], smtphost['connect']['password'])

                if smtphost.get('debug'):
                    smtp.set_debuglevel(True)

                if 'method' not in smtphost or smtphost['method'] == 1:
                    smtp.send_message(self._msg)
                else:
                    smtp.sendmail(self._from, self._to, self._msg.as_string())

                code = 1

            except:
                if IsPrintExceptions and callable(print_exception):
                    print_exception()
                if with_raise:
                    raise
                self._set_smtp()
                continue

            finally:
                if smtp is not None:
                    smtp.quit()

        return code


def send_test(subject, document, filename, html, **kw):
    if subject:
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = kw.get('addr_from')
        msg['To'] = kw.get('addr_to')

        if html:
            msg.attach(MIMEText(html, 'html'))
    
        if isinstance(document, bytes):
            fp = io.BytesIO(document)
        else:
            fp = io.BytesIO()
            document.save(fp)

        ctype = kw.get('ctype') or 'application/msword' #octet-stream vnd.ms-excel application/pdf vnd.ms-powerpoint image/png

        maintype, subtype = ctype.split('/', 1)
        base = MIMEBase(maintype, subtype)
        fp.seek(0)
        base.set_payload(fp.read())
        encoders.encode_base64(base)

        header = Header(filename, charset=default_unicode)
        base.add_header('Content-Disposition', 'attachment', filename='%s' % header.encode())

        msg.attach(base)

        smtp = smtplib.SMTP(smtphost['host'], smtphost['port'])
        smtp.send_message(msg)
        smtp.quit()

        fp.close()

    return 1

def send_materials_order(subject, props, document, filename, **kw):
    """
        Materials order mail request.
    """
    html = '''
        <html>
        <head>
          <style type="text/css">
            h1 { font-size:18px; padding:0; margin:0 0 10px 0; }
            td { font-size:16px; font-weight:bold; line-height:24px; padding:0; color:#468; margin-left:0px; }
            div.line { border-top:1px dotted #888; width:100%%; height:1px; margin:10px 0 10px 0; }
            div.line hr { display:none; }
          </style>
        </head>
        <body>
          <h1 class="center">Файл заказа:</h1>
          <table>
          <tr><td class="value">%(ClientName)s</td><tr>
          <tr><td class="value">%(FileName)s</td></tr></table>
          <div class="line"><hr></div>
        </body>
        </html>
    ''' % props

    #return send_test(subject, document, filename, html, **kw)

    mail = SendMail(subject, **kw)

    mail.create_message(html)
    mail.attach_docx(document, filename)
    
    return mail.send()

def send_simple_mail(subject, message, addr_to, addr_cc=None, addr_from=None, with_raise=None, canal=None):
    if not addr_to:
        return 0

    mail = SendMail(subject, addr_to=addr_to, addr_cc=addr_cc, addr_from=addr_from, canal=canal)
    mail.create_message(message)

    return mail.send(with_raise=with_raise)

def send_mail_with_attachment(subject, message, addr_to, addr_cc=None, attachments=None, with_info=None):
    if not addr_to:
        return 0

    mail = SendMail(subject, addr_to=addr_to, addr_cc=addr_cc)
    mail.create_message(message)
    
    for document, filename, ftype in attachments:
        if not ftype:
            pass
        elif ftype == 'doc':
            mail.attach_doc(document, filename)
        elif ftype == 'xls':
            mail.attach_xls(document, filename)
        elif ftype == 'zip':
            mail.attach_zip(document, filename)
        elif ftype == 'csv':
            mail.attach_csv(document, filename)
        else:
            mail.attach_any(document, filename)

    code = mail.send()

    if with_info:
        return code, mail.canal, \
            mail.canal is not None and smtphosts and mail.canal < len(smtphosts) and smtphosts[mail.canal] or None

    return code


if __name__ == "__main__":
    argv = sys.argv

    #   Arguments in debug mode:
    #       0: script name
    #       1: mode     {0|1|2|3|4}
    #       2: canal    {-1|0}
    #       3: addr_to  {<emails>}

    #from local import setup_console
    #setup_console(default_encoding)

    mode = len(argv) == 1 and 3 or int(argv[1])
    canal = len(argv) < 3 and None or int(argv[2])

    print('argv:%s' % repr(argv))
    
    addr_to, filename = '', ''

    print('mode:%s, canal:%s\n' % (mode, canal))

    if mode == 0:
        subject = 'Тест сообщения'
    elif mode < 3:
        source = r'R:\scripts\perso\tmp\PLP_20180827_1415_C2_001_Post1Class.xls'
        filename = 'VBEX_CRDEMB_20180831_005_40599115_111.TXT'

        subject = 'ПОЧТАБАНК Накладные на отгрузку'
        filename = '%s.xls' % filename.split('.')[0]

        fi = open(source, 'rb')
        document = fi.read()
        fi.close()
    elif mode == 4:
        subject = 'Накладные DHL'
        #addr_to = 'hperso@rosan.ru;otgruzka@rosan.ru;pmmos@rosan.ru;webdev@rosan.ru'
        addr_to = 'webdev@rosan.ru'
        source, filename = 'C:/apps/perso/tmp', 'VBEX_CRDEMB_20191230_005_20200113$DN.csv'
    else:
        subject = 'PostBank F103:354'
        source, filename = 'C:/0/mail', 'F003232005484901100002.zip'

    props = {'ClientName' : 'ПАО "ПОЧТАБАНК"', 'FileName' : filename}

    html = '''
        <html>
        <head>
          <style type="text/css">
            h1 { font-size:18px; padding:0; margin:0 0 10px 0; }
            td { font-size:16px; font-weight:bold; line-height:24px; padding:0; color:#468; margin-left:0px; }
            div.line { border-top:1px dotted #888; width:100%%; height:1px; margin:10px 0 10px 0; }
            div.line hr { display:none; }
          </style>
        </head>
        <body>
          <h1 class="center">Файл заказа:</h1>
          <table>
          <tr><td class="value">%(ClientName)s</td><tr>
          <tr><td class="value">%(FileName)s</td></tr></table>
          <div class="line"><hr></div>
        </body>
        </html>
    ''' % props
    
    addr_from = 'mailrobot@rosan.ru'
    if not addr_to:
        addr_to = len(argv) > 3 and argv[3] or 'webdev@rosan.ru'
    addr_cc = ''

    code = 0

    if mode == 0:
        code = send_simple_mail(subject, html, addr_to, addr_cc=addr_cc, with_raise=True, canal=canal)
    elif mode == 1:
        code = send_test(subject, document, filename, html, 
            addr_from=addr_from,
            addr_to=addr_to,
            ctype='application/vnd.ms-excel',
            )
    elif mode == 2:
        mail = SendMail(subject, addr_from=addr_from, addr_to=addr_to, addr_cc=addr_cc)
        mail.create_message(html)
        mail.attach_xls(document, filename)
        code = mail.send()
    elif mode == 3:
        mail = SendMail(subject, addr_from=addr_from, addr_to=addr_to, addr_cc=addr_cc)
        mail.create_message('See attachment')
        mail.attach_zip(source, filename)
        code = mail.send()
    elif mode == 4:
        """
        mail = SendMail(subject, addr_from=addr_from, addr_to=addr_to)
        mail.create_message('See attachment')
        mail.attach_csv(source, filename)
        code = mail.send()
        """
        message = 'See attachment'
        attachments = [(source, filename, 'csv'),]
        code, canal, smtphost = send_mail_with_attachment(subject, message, addr_to, attachments=attachments, with_info=True)

        print('canal:%s, smtphost:%s' % (canal, smtphost))

    print('Mail sent to: %s, cc: %s, code: %d' % (addr_to, addr_cc, code))
