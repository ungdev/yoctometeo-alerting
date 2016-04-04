import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_mail(config, addressee, subject, body):
    msg = MIMEMultipart()
    msg['From'] = config["from-address"]
    msg['To'] = addressee
    msg['Subject'] = subject
    msg.attach(MIMEText(body))
    mailserver = smtplib.SMTP(host=config["host"], port=config["port"])
    mailserver.ehlo()
    if config["tls"] == 'true':
        mailserver.starttls()
    mailserver.ehlo()
    mailserver.login(config["username"], config["password"])
    mailserver.sendmail(config["from-address"], addressee, msg.as_string())
    mailserver.quit()