
import os, smtplib
from email.mime.text import MIMEText

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USER)

def send_reset_email(email_to: str, reset_link: str):
    if not SMTP_USER or not SMTP_PASS:
        print("[email_service] SMTP_USER/SMTP_PASS não configurados; simulando envio. Link:", reset_link)
        return
    msg = MIMEText(f'''
    <p>Recebemos um pedido para redefinir sua senha no EmoSync.</p>
    <p>Clique no link abaixo para criar uma nova senha (válido por 30 minutos):</p>
    <p><a href="{reset_link}">{reset_link}</a></p>
    <p>Se você não solicitou, ignore este e-mail.</p>
    ''', 'html')
    msg['Subject'] = "Redefinição de senha - EmoSync"
    msg['From'] = EMAIL_FROM
    msg['To'] = email_to

    if SMTP_PORT == 465:
        server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
    else:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()

    server.login(SMTP_USER, SMTP_PASS)
    server.send_message(msg)
    server.quit()
