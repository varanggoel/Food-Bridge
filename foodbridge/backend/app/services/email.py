"""Real email sending via Gmail SMTP (smtplib), SSL on port 465."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings, get_logger

logger = get_logger(__name__)


def send_email(to_email: str, subject: str, body: str) -> bool:
    """Sends a plain-text email. Returns True on success, False on failure."""
    if not settings.EMAIL_USER or not settings.EMAIL_PASSWORD:
        logger.error("EMAIL_USER / EMAIL_PASSWORD not configured")
        return False

    if not to_email:
        logger.error("No recipient email provided")
        return False

    msg = MIMEMultipart()
    msg["From"] = settings.EMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT, timeout=15) as server:
            server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
            server.sendmail(settings.EMAIL_USER, to_email, msg.as_string())
        logger.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False
