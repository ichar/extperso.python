
from datetime import datetime
import asyncore
from smtpd import SMTPServer

smtphost = {'host':'localhost', 'port':25}
email_address_list = {'mailrobot' : 'mailrobot@rosan.ru',}


class EmlServer(SMTPServer):
    no = 0
    def process_message(self, peer, mailfrom, rcpttos, data):
        filename = 'E:/mail/%s-%d.eml' % (datetime.now().strftime('%Y%m%d%H%M%S'),
                self.no)
        f = open(filename, 'w')
        f.write(data)
        f.close
        print('%s saved.' % filename)
        self.no += 1

        super().process_message(peer, mailfrom, rcpttos, data)


def run():
    foo = EmlServer(('127.0.0.1', 1025), None)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    run()

"""
# Proxy smtp to a starttls server with authentication, from a local
# connection.

from inbox import Inbox
from smtplib import SMTP

inbox = Inbox()

SMTP_HOST = 'localhost.mail'
SMTP_USERNAME = 'username'
SMTP_PASSWORD = 'password'

@inbox.collate
def handle(to, sender, body, **kw):
    # Forward a message via an authenticated SMTP connection with
    # starttls.
    conn = SMTP(SMTP_HOST, 25, 'localhost')

    #print('to:', to)
    #print('sender:', sender)
    #print('body:', str(body))
    #print(kw)

    conn.starttls()
    conn.ehlo_or_helo_if_needed()
    #conn.login(SMTP_USERNAME, SMTP_PASSWORD)
    conn.sendmail(sender, to, body)
    conn.quit()

inbox.serve(address='127.0.0.1', port=1025) # 192.168.0.53
"""
"""
import smtpd
import asyncore

class CustomSMTPServer(smtpd.SMTPServer):
    
    def process_message(self, peer, mailfrom, rcpttos, data):
        print('Receiving message from:', peer)
        print('Message addressed from:', mailfrom)
        print('Message addressed to  :', rcpttos)
        print('Message length        :', len(data))
        
        super().process_message(peer, mailfrom, rcpttos, data)

server = CustomSMTPServer(('127.0.0.1', 1025), None)

asyncore.loop()
"""