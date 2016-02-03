import smtplib
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart


def send_mail(to, sub, content, from_email, mail_pass, filelist=[]):
    mail_postfix, mail_user = from_email.split('@')
    mail_host = "smtp.%s" % mail_postfix

    me = mail_user + "<" + from_email + ">"

    msg = MIMEMultipart('related')
    msg['Subject'] = sub.encode('gbk')
    msg['Form'] = me
    msg['To'] = to
    msgAlternative = MIMEMultipart('alternative')
    msg.attach(msgAlternative)

    msgText = MIMEText(content, 'html', 'gbk')
    msgAlternative.attach(msgText)

    if filelist:
        for f in filelist:
            att = MIMEText(open(f, 'rb').read(), 'base64', 'gb2312')
            att["Content-Type"] = 'application/octet-stream'
            att["Content-Disposition"] = 'attachment;filename=%s' % f
            msgAlternative.attach(att)

    message = msg.as_string()

    try:
        s = smtplib.SMTP()
        try:
            s.connect(mail_host)
        except Exception, e:
            print str(e)
        s.starttls()
        s.login(mail_user, mail_pass)
        s.sendmail(me, to, message)
        s.close()
        return True
    except Exception, e:
        print str(e)
        return False
