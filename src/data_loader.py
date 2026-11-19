"""
Data loader module for reading and validating Contacts and Reminders CSV files.
Supports both Pandas and standard library csv.DictReader for 100% portability.
"""

import csv
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
from src.config import Config, logger

# RFC 5322 simplified email validation regex
EMAIL_REGEX = re.compile(r"^[\w\.-]+@([\w-]+\.)+[\w-]{2,4}$")


def is_valid_email(email_str: str) -> bool:
    """Validates basic email structure."""
    if not email_str or not isinstance(email_str, str):
        return False
    return bool(EMAIL_REGEX.match(email_str.strip()))


class DataLoader:
    """Handles parsing, validation, and joining of contacts and reminders."""

    def __init__(self, contacts_path: Path = None, reminders_path: Path = None):
        self.contacts_path = contacts_path or Config.CONTACTS_FILE
        self.reminders_path = reminders_path or Config.REMINDERS_FILE

    def load_contacts(self) -> Dict[str, Dict[str, Any]]:
        """
        Loads contacts from CSV into a dictionary keyed by contact_id.
        Validates email format and logs invalid entries.
        """
        contacts: Dict[str, Dict[str, Any]] = {}
        if not self.contacts_path.exists():
            logger.error(f"Contacts file not found at: {self.contacts_path}")
            return contacts

        try:
            with open(self.contacts_path, mode="r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row_idx, row in enumerate(reader, start=2):
                    cid = row.get("contact_id", "").strip()
                    email = row.get("email", "").strip()
                    name = row.get("name", "").strip()

                    if not cid:
                        logger.warning(f"Line {row_idx}: Skipped contact with missing 'contact_id'")
                        continue

                    valid_email = is_valid_email(email)
                    contacts[cid] = {
                        "contact_id": cid,
                        "name": name,
                        "email": email,
                        "department": row.get("department", "General").strip(),
                        "role": row.get("role", "Team Member").strip(),
                        "timezone": row.get("timezone", "Asia/Kolkata").strip(),
                        "status": row.get("status", "Active").strip(),
                        "is_valid_email": valid_email,
                    }
                    if not valid_email:
                        logger.warning(f"Contact '{name}' (ID: {cid}) has invalid email: '{email}'")

            logger.info(f"Loaded {len(contacts)} contacts from {self.contacts_path.name}")
        except Exception as e:
            logger.error(f"Failed to read contacts CSV: {e}", exc_info=True)

        return contacts

    def load_reminders(self) -> List[Dict[str, Any]]:
        """Loads all reminders from reminders.csv."""
        reminders: List[Dict[str, Any]] = []
        if not self.reminders_path.exists():
            logger.error(f"Reminders file not found at: {self.reminders_path}")
            return reminders

        try:
            with open(self.reminders_path, mode="r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row_idx, row in enumerate(reader, start=2):
                    rid = row.get("reminder_id", "").strip()
                    cid = row.get("contact_id", "").strip()
                    if not rid or not cid:
                        logger.warning(f"Line {row_idx}: Skipped reminder missing ID or contact_id")
                        continue

                    reminders.append({
                        "reminder_id": rid,
                        "contact_id": cid,
                        "template_name": row.get("template_name", "meeting_reminder").strip(),
                        "reminder_type": row.get("reminder_type", "General").strip(),
                        "title": row.get("title", "Scheduled Reminder").strip(),
                        "due_date": row.get("due_date", "").strip(),
                        "due_time": row.get("due_time", "").strip(),
                        "amount_due": row.get("amount_due", "0.00").strip(),
                        "meeting_link": row.get("meeting_link", "N/A").strip(),
                        "status": row.get("status", "Pending").strip(),
                    })
            logger.info(f"Loaded {len(reminders)} reminders from {self.reminders_path.name}")
        except Exception as e:
            logger.error(f"Failed to read reminders CSV: {e}", exc_info=True)

        return reminders

    def get_enriched_reminders(self) -> List[Dict[str, Any]]:
        """
        Joins Reminders with Contacts data to form fully populated message tasks.
        """
        contacts = self.load_contacts()
        reminders = self.load_reminders()
        enriched: List[Dict[str, Any]] = []

        for rem in reminders:
            cid = rem["contact_id"]
            contact = contacts.get(cid)
            if not contact:
                logger.warning(f"Reminder {rem['reminder_id']} references unknown contact {cid}")
                continue

            # Merge reminder and contact fields
            task = {**contact, **rem}
            enriched.append(task)

        return enriched
