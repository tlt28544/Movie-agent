import os
import smtplib
from email.mime.text import MIMEText

from src.constants import SMTP_HOST, SMTP_PORT


def send_email(subject: str, html_body: str, to_email: str) -> None:
    smtp_user = os.getenv("SMTP_USER", "").strip()
    smtp_password = os.getenv("SMTP_APP_PASSWORD", "").strip()
    from_email = os.getenv("FROM_EMAIL", smtp_user).strip()

    if not smtp_user or not smtp_password:
        raise ValueError("SMTP_USER or SMTP_APP_PASSWORD is missing")

    msg = MIMEText(html_body, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30) as server:
        server.login(smtp_user, smtp_password)
        server.sendmail(from_email, [to_email], msg.as_string())
