"""Real email sending via SMTP with Gmail-compatible settings."""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings, get_logger

logger = get_logger(__name__)


def send_email(to_email: str, subject: str, body: str) -> bool:
    """Sends a plain-text email. Returns True on success, False on failure.

    Tries SMTP_SSL (port 465) first, then falls back to STARTTLS (port 587)
    since some cloud providers block one or the other.
    """
    recipient = (to_email or "").strip()
    if not recipient:
        logger.error("No recipient email provided")
        return False

    username = (settings.EMAIL_USER or os.getenv("SMTP_USERNAME", "") or os.getenv("EMAIL_HOST_USER", "")).strip()
    password = (settings.EMAIL_PASSWORD or os.getenv("SMTP_PASSWORD", "") or os.getenv("EMAIL_HOST_PASSWORD", "")).strip()
    if not username or not password:
        logger.error("SMTP credentials not configured (EMAIL_USER or EMAIL_PASSWORD missing)")
        return False

    smtp_server = (os.getenv("SMTP_SERVER") or settings.SMTP_SERVER or "smtp.gmail.com").strip()
    smtp_port = int(os.getenv("SMTP_PORT", settings.SMTP_PORT or 465))
    from_email = (os.getenv("EMAIL_FROM") or username).strip()

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = recipient
    msg["Subject"] = subject or "FoodBridge India Donation Notification"
    msg.attach(MIMEText(body or "", "plain"))

    # Attempt 1: SMTP_SSL (port 465)
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=15) as server:
            server.login(username, password)
            server.sendmail(from_email, recipient, msg.as_string())
        logger.info(f"Email sent successfully to {recipient} via SMTP_SSL (port {smtp_port})")
        return True
    except Exception as e:
        logger.warning(f"SMTP_SSL (port {smtp_port}) failed for {recipient}: {e}")

    # Attempt 2: STARTTLS (port 587) — fallback for cloud providers that block 465
    try:
        with smtplib.SMTP(smtp_server, 587, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(username, password)
            server.sendmail(from_email, recipient, msg.as_string())
        logger.info(f"Email sent successfully to {recipient} via STARTTLS (port 587)")
        return True
    except Exception as e:
        logger.error(f"STARTTLS (port 587) also failed for {recipient}: {e}")

    return False
