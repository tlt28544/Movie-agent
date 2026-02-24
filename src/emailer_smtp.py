import os
import smtplib
from email.utils import getaddresses
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.constants import SMTP_HOST, SMTP_PORT


def parse_recipients(to_email: str) -> list[str]:
    """Parse a recipient string into an SMTP-safe recipient list."""
    raw = (to_email or "").strip()
    if not raw:
        return []

    normalized = raw.replace(";", ",")
    recipients = [address for _, address in getaddresses([normalized]) if address]
    return [address.strip() for address in recipients if address.strip()]


def send_email(subject: str, html_body: str, to_email: str, attachments: list[str] | None = None) -> None:
    smtp_user = os.getenv("SMTP_USER", "").strip()
    smtp_password = os.getenv("SMTP_APP_PASSWORD", "").strip()
    from_email = os.getenv("FROM_EMAIL", smtp_user).strip()

    if not smtp_user or not smtp_password:
        raise ValueError("SMTP_USER or SMTP_APP_PASSWORD is missing")

    recipients = parse_recipients(to_email)
    if not recipients:
        raise ValueError("TO_EMAIL is missing or invalid")

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    for file_path in attachments or []:
        with open(file_path, "rb") as f:
            part = MIMEApplication(
                f.read(),
                _subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            part.add_header(
                "Content-Disposition",
                "attachment",
                filename=os.path.basename(file_path),
            )
            msg.attach(part)

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30) as server:
        server.login(smtp_user, smtp_password)
        server.sendmail(from_email, recipients, msg.as_string())
