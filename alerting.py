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


def send_log_alert(logger, level, msg):
    if level == 'critical':
        logger.critical(msg)
    elif level == 'error':
        logger.error(msg)
    elif level == 'warning':
        logger.warning(msg)
    else:
        logger.info(msg)