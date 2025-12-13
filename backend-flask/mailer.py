from typing import List, Optional
from flask import current_app
from flask_mail import Message
from extensions import mail


def send_email(subject: str, recipients: List[str], body: str, html: Optional[str] = None) -> bool:
    """Send an email; returns True on success, False otherwise."""
    if not recipients:
        return False
    try:
        msg = Message(
            subject=subject,
            recipients=recipients,
            body=body,
            html=html,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER')
        )
        mail.send(msg)
        return True
    except Exception as exc:  # pragma: no cover - best-effort notification
        current_app.logger.warning(f"Email send failed: {exc}")
        return False

