import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USERNAME, MAIL_PASSWORD

def enviar_correo(destinatario, asunto, mensaje):
    try:
        msg = MIMEMultipart()
        msg['From'] = MAIL_USERNAME
        msg['To'] = destinatario
        msg['Subject'] = asunto

        msg.attach(MIMEText(mensaje, 'html'))

        servidor = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
        if MAIL_USE_TLS:
            servidor.starttls()

        servidor.login(MAIL_USERNAME, MAIL_PASSWORD)
        servidor.send_message(msg)
        servidor.quit()
        print(f" Correo enviado a {destinatario}")
        return True
    except Exception as e:
        print(f" Error al enviar el correo: {e}")
        return False
