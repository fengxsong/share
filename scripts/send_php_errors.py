#!/usr/bin/env python
# -*- coding:utf-8 -*-
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText

from email.utils import COMMASPACE, formatdate
from email import encoders
import os


def send_mail(server, fro, to, subject, text, files=[]):
    assert type(server) == dict
    assert type(to) == list
    assert type(files) == list

    msg = MIMEMultipart()
    msg['From'] = fro
    msg['Subject'] = subject
    msg['to'] = COMMASPACE.join(to)
    msg['Date'] = formatdate(localtime=True)
    msg.attach(MIMEText(text))

    for f in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(f, "rb").read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
        msg.attach(part)

    import smtplib

    try:
        sm = smtplib.SMTP(server['name'], server['port'])
        sm.ehlo()
        if server['isTls']:
            sm.starttls()
            sm.ehlo()
        sm.login(server['user'], server['password'])
        sm.sendmail(fro, to, msg.as_string())
        sm.close()
    except Exception as e:
        print e


def test():
    cmd = "grep error /usr/local/php/var/log/php_errors.log > /tmp/php_grep_errors.log"
    os.system(cmd)
    with open("/tmp/php_grep_errors.log") as f:
        if len(f.readlines()) != 0:
            import arrow

            server = {'name': 'smtp.qiye.163.com',
                      'user': 'fengxsong@example.com',
                      'password': 'hey_there!!',
                      'port': 25,
                      'isTls': False}
            fro = server['user']
            to = ['someoneelse@example.com']
            subject = 'PHP_errors log at %s' % os.environ['HOSTNAME']
            text = 'PHP_errors util %s\n' % arrow.now().format()
            files = ['/usr/local/php/var/log/php_errors.log', '/tmp/php_grep_errors.log']
            send_mail(server, fro, to, subject, text, files=files)
        else:
            pass
    os.system("echo > /usr/local/php/var/log/php_errors.log")


if __name__ == '__main__':
    test()
