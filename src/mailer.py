"""
SMTP Email Dispatcher with Safe Virtual Simulation (Dry-Run Mode).
Handles real SMTP (Gmail, Outlook, Mailtrap) and offline testing simulations.
"""

import smtplib
import time
import uuid
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from typing import Dict, Any, Optional

from src.config import Config, logger, SIMULATED_DIR


class Mailer:
    """Handles email formatting and transmission via SMTP or safe virtual simulation."""

    def __init__(self, dry_run: Optional[bool] = None):
        self.dry_run = Config.DRY_RUN if dry_run is None else dry_run

    def send_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        content: str,
        content_type: str = "html",
        reminder_id: str = "R000"
    ) -> Dict[str, Any]:
        """
        Sends an email or safely simulates sending if dry_run is True.
        
        Returns:
            dict containing:
                - success (bool)
                - status ("Sent", "Simulated", or "Failed")
                - message_id (str)
                - error (str or None)
                - timestamp (str)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message_id = f"MSG-{uuid.uuid4().hex[:10].upper()}"

        # 1. Validation check
        if not to_email or "@" not in to_email:
            err = f"Invalid recipient email address: '{to_email}'"
            logger.error(f"[{reminder_id}] Dispatch rejected: {err}")
            return {
                "success": False,
                "status": "Failed",
                "message_id": message_id,
                "error": err,
                "timestamp": timestamp,
            }

        # 2. Build MIME Email Message
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = f"{Config.SENDER_NAME} <{Config.SENDER_EMAIL}>"
        msg["To"] = f"{to_name} <{to_email}>"
        msg["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
        msg["Message-ID"] = f"<{message_id}@{Config.SMTP_SERVER}>"

        if content_type == "html":
            # Set plain text fallback first, then HTML alternative
            msg.set_content("Please enable HTML email view to see this notification.")
            msg.add_alternative(content, subtype="html")
        else:
            msg.set_content(content)

        # 3. Virtual Simulation (Dry Run Mode)
        if self.dry_run:
            time.sleep(0.1)  # Simulate brief network turnaround
            logger.info(
                f"[SIMULATION] [ID: {reminder_id}] To: {to_email} | Subject: '{subject}' -> SUCCESS (Dry Run)"
            )

            # Save the rendered HTML/content for student verification
            safe_filename = f"{reminder_id}_{to_email.replace('@', '_at_')}.html"
            preview_file = SIMULATED_DIR / safe_filename
            try:
                with open(preview_file, "w", encoding="utf-8") as pf:
                    pf.write(content)
            except Exception as e:
                logger.warning(f"Could not write simulation preview file: {e}")

            return {
                "success": True,
                "status": "Simulated",
                "message_id": message_id,
                "error": None,
                "timestamp": timestamp,
                "preview_path": str(preview_file),
            }

        # 4. Real SMTP Transmission Mode
        try:
            logger.info(f"[LIVE SMTP] Connecting to {Config.SMTP_SERVER}:{Config.SMTP_PORT}...")

            if Config.SMTP_PORT == 465:
                # SSL Connection
                with smtplib.SMTP_SSL(Config.SMTP_SERVER, Config.SMTP_PORT, timeout=15) as server:
                    if Config.SENDER_PASSWORD:
                        server.login(Config.SENDER_EMAIL, Config.SENDER_PASSWORD)
                    server.send_message(msg)
            else:
                # TLS Connection (Standard port 587)
                with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT, timeout=15) as server:
                    if Config.USE_TLS:
                        server.starttls()
                    if Config.SENDER_PASSWORD:
                        server.login(Config.SENDER_EMAIL, Config.SENDER_PASSWORD)
                    server.send_message(msg)

            logger.info(f"[LIVE SMTP] [ID: {reminder_id}] Successfully dispatched to {to_email}")
            return {
                "success": True,
                "status": "Sent",
                "message_id": message_id,
                "error": None,
                "timestamp": timestamp,
            }

        except smtplib.SMTPAuthenticationError as e:
            err = f"SMTP Authentication failed. Verify App Password. Details: {e.smtp_error.decode() if hasattr(e, 'smtp_error') else e}"
            logger.error(f"[{reminder_id}] {err}")
            return {"success": False, "status": "Failed", "message_id": message_id, "error": err, "timestamp": timestamp}
        except smtplib.SMTPConnectError as e:
            err = f"Could not connect to SMTP server: {e}"
            logger.error(f"[{reminder_id}] {err}")
            return {"success": False, "status": "Failed", "message_id": message_id, "error": err, "timestamp": timestamp}
        except Exception as e:
            err = f"Unexpected transmission error: {str(e)}"
            logger.error(f"[{reminder_id}] {err}", exc_info=True)
            return {"success": False, "status": "Failed", "message_id": message_id, "error": err, "timestamp": timestamp}
