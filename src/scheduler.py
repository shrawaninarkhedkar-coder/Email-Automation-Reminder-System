"""
Scheduler module for time-based reminder triggers and automated dispatch loops.
Supports both one-off batch runs and continuous recurring checks.
"""

import time
from datetime import datetime
from typing import List, Dict, Any, Optional

from src.config import Config, logger
from src.data_loader import DataLoader
from src.template_engine import TemplateEngine
from src.mailer import Mailer
from src.tracker import DeliveryTracker


class ReminderScheduler:
    """Coordinates reminder evaluation, template rendering, dispatch, and tracking."""

    def __init__(self, dry_run: Optional[bool] = None):
        self.dry_run = Config.DRY_RUN if dry_run is None else dry_run
        self.loader = DataLoader()
        self.engine = TemplateEngine()
        self.mailer = Mailer(dry_run=self.dry_run)
        self.tracker = DeliveryTracker()

    def is_reminder_due(self, task: Dict[str, Any], reference_dt: Optional[datetime] = None) -> bool:
        """
        Determines if a reminder is due to be sent.
        If due_date is empty, it treats it as an immediate one-off reminder.
        """
        if task.get("status", "").lower() in ("completed", "sent"):
            return False

        due_date_str = task.get("due_date", "").strip()
        due_time_str = task.get("due_time", "").strip()

        if not due_date_str:
            return True  # Immediate dispatch

        ref = reference_dt or datetime.now()
        today_str = ref.strftime("%Y-%m-%d")

        # Compare dates
        if due_date_str < today_str:
            return True  # Past due, trigger now
        elif due_date_str == today_str:
            if not due_time_str:
                return True
            curr_time_str = ref.strftime("%H:%M")
            return curr_time_str >= due_time_str

        return False  # Future date

    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Renders template, dispatches email, and records to delivery tracker."""
        reminder_id = task.get("reminder_id", "R000")
        recipient_name = task.get("name", "Valued Recipient")
        recipient_email = task.get("email", "")
        template_name = task.get("template_name", "meeting_reminder")

        # Check for invalid email upfront
        if not task.get("is_valid_email", True) or not recipient_email:
            result = {
                "success": False,
                "status": "Failed",
                "message_id": "N/A",
                "error": f"Invalid recipient email format: '{recipient_email}'",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            self.tracker.record_result(task, result)
            return result

        try:
            subject, content, content_type = self.engine.render(template_name, task)
        except Exception as e:
            logger.error(f"[{reminder_id}] Template render error: {e}")
            result = {
                "success": False,
                "status": "Failed",
                "message_id": "N/A",
                "error": f"Template rendering failed: {str(e)}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            self.tracker.record_result(task, result)
            return result

        # Dispatch via mailer
        send_result = self.mailer.send_email(
            to_email=recipient_email,
            to_name=recipient_name,
            subject=subject,
            content=content,
            content_type=content_type,
            reminder_id=reminder_id,
        )

        self.tracker.record_result(task, send_result)
        return send_result

    def run_batch(self, force_all: bool = False) -> DeliveryTracker:
        """
        Executes a single cycle over all reminders.
        Args:
            force_all: If True, executes all reminders regardless of due time (e.g. for testing/demo).
        """
        tasks = self.loader.get_enriched_reminders()
        logger.info(f"Starting batch evaluation of {len(tasks)} reminder tasks...")

        due_count = 0
        for task in tasks:
            if force_all or self.is_reminder_due(task):
                due_count += 1
                self.process_task(task)
            else:
                logger.info(
                    f"[SKIPPED] [{task['reminder_id']}] '{task['title']}' not due yet (Due: {task['due_date']} {task['due_time']})"
                )

        logger.info(f"Batch completed. Dispatched {due_count} of {len(tasks)} reminders.")
        self.tracker.save_csv_report()
        self.tracker.print_terminal_summary()
        return self.tracker

    def run_continuous_loop(self, interval_seconds: Optional[int] = None):
        """Runs continuous polling loop checking for due reminders."""
        interval = interval_seconds or Config.CHECK_INTERVAL_SECONDS
        logger.info(f"Starting Reminder Daemon Loop (Polling interval: {interval}s). Press Ctrl+C to stop.")

        try:
            while True:
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logger.info(f"[CYCLE HEARTBEAT {now_str}] Checking for due reminders...")
                self.run_batch(force_all=False)
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Continuous scheduler loop stopped by user.")
