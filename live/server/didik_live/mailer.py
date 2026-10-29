"""The few emails the app sends (password reset links), over SMTP with the standard library.

Without SMTP settings (a computer at home or in a classroom), a message is written to the server log
instead, where whoever runs the server can find it.
"""

from __future__ import annotations

import logging
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formatdate, make_msgid, parseaddr

from .config import MailSettings

log = logging.getLogger("didik.mail")


class Mailer:
    def __init__(self, settings: MailSettings | None) -> None:
        self.settings = settings

    @property
    def ready(self) -> bool:
        return self.settings is not None

    def send(self, to: str, subject: str, body: str) -> None:
        """Blocking: call it from a worker thread (FastAPI background tasks run there)."""
        settings = self.settings
        if settings is None:
            log.warning("Tiada SMTP, jadi emel ini tidak dihantar.\nKepada: %s\nPerkara: %s\n\n%s", to, subject, body)
            return

        message = EmailMessage()
        message["From"] = settings.sender
        message["To"] = to
        message["Subject"] = subject
        message["Date"] = formatdate(localtime=True)
        # the sender may carry a name ("DIDIK <no-reply@contoh.my>"); the id takes the bare domain
        message["Message-ID"] = make_msgid(domain=parseaddr(settings.sender)[1].rpartition("@")[2] or None)
        message.set_content(body)

        context = ssl.create_default_context()
        try:
            if settings.security == "ssl":
                with smtplib.SMTP_SSL(settings.host, settings.port, context=context, timeout=20) as smtp:
                    self._deliver(smtp, message)
            else:
                with smtplib.SMTP(settings.host, settings.port, timeout=20) as smtp:
                    if settings.security == "starttls":
                        smtp.starttls(context=context)
                    self._deliver(smtp, message)
        except (OSError, smtplib.SMTPException):
            log.exception("email to %s could not be sent", to)

    def _deliver(self, smtp: smtplib.SMTP, message: EmailMessage) -> None:
        settings = self.settings
        assert settings is not None
        if settings.user:
            smtp.login(settings.user, settings.password)
        smtp.send_message(message)
