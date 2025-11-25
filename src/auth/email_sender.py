
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
FRONTEND_RESET_URL = os.getenv("FRONTEND_RESET_URL") or "http://localhost"

def send_recovery_email(to_email: str, token: str):
    reset_link = f"{FRONTEND_RESET_URL}?token={token}"

    subject = "Recuperación de contraseña - FinTrack"
    body = f"""
    <h2>Recuperación de contraseña</h2>
    <p>Haz clic en este enlace para restablecer tu contraseña:</p>
    <a href="{reset_link}">{reset_link}</a>
    """

    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
        print(f"Correo enviado a {to_email}")
    except Exception as e:
        print("Error enviando correo:", e)
        raise
