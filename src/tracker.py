"""
Delivery Tracker and Report Generator.
Records sent/failed emails to CSV audit reports and calculates delivery metrics.
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from src.config import Config, logger


class DeliveryTracker:
    """Manages dispatch audit trails and generates CSV reports."""

    def __init__(self, report_path: Path = None):
        self.report_path = report_path or Config.REPORT_FILE
        self.records: List[Dict[str, Any]] = []

    def record_result(self, reminder_task: Dict[str, Any], send_result: Dict[str, Any]):
        """Records the outcome of a single email dispatch attempt."""
        entry = {
            "reminder_id": reminder_task.get("reminder_id", "N/A"),
            "recipient_name": reminder_task.get("name", "N/A"),
            "recipient_email": reminder_task.get("email", "N/A"),
            "department": reminder_task.get("department", "N/A"),
            "reminder_title": reminder_task.get("title", "N/A"),
            "status": send_result.get("status", "Unknown"),
            "message_id": send_result.get("message_id", "N/A"),
            "error_reason": send_result.get("error") or "None",
            "timestamp": send_result.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        }
        self.records.append(entry)

    def save_csv_report(self) -> Path:
        """Writes all accumulated records to a CSV report."""
        if not self.records:
            logger.warning("No records to save to delivery report.")
            return self.report_path

        fieldnames = [
            "reminder_id",
            "recipient_name",
            "recipient_email",
            "department",
            "reminder_title",
            "status",
            "message_id",
            "error_reason",
            "timestamp",
        ]

        file_exists = self.report_path.exists()

        try:
            with open(self.report_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for rec in self.records:
                    writer.writerow(rec)

            logger.info(f"Delivery report saved successfully -> {self.report_path}")
        except Exception as e:
            logger.error(f"Failed to write delivery report CSV: {e}", exc_info=True)

        return self.report_path

    def get_summary_metrics(self) -> Dict[str, Any]:
        """Calculates success rates and counts."""
        total = len(self.records)
        sent = sum(1 for r in self.records if r["status"] in ("Sent", "Simulated"))
        failed = sum(1 for r in self.records if r["status"] == "Failed")
        rate = (sent / total * 100) if total > 0 else 0.0

        return {
            "total_processed": total,
            "successful": sent,
            "failed": failed,
            "success_rate_pct": round(rate, 2),
        }

    def print_terminal_summary(self):
        """Prints a professional, clean ASCII summary box to the terminal."""
        metrics = self.get_summary_metrics()
        print("\n" + "=" * 65)
        print("          EMAIL DISPATCH & REMINDER EXECUTION SUMMARY          ")
        print("=" * 65)
        print(f" Mode               : {'SIMULATION (DRY-RUN)' if Config.DRY_RUN else 'LIVE SMTP'}")
        print(f" Total Evaluated    : {metrics['total_processed']}")
        print(f" Succeeded/Simulated: {metrics['successful']}")
        print(f" Failed / Rejected  : {metrics['failed']}")
        print(f" Success Rate       : {metrics['success_rate_pct']}%")
        print(f" Report Saved To    : {self.report_path.name}")
        print("-" * 65)
        print(f"{'ID':<6} | {'Recipient':<18} | {'Status':<10} | {'Error / Note'}")
        print("-" * 65)
        for r in self.records:
            note = r["error_reason"] if r["error_reason"] != "None" else "OK"
            if len(note) > 28:
                note = note[:25] + "..."
            print(f"{r['reminder_id']:<6} | {r['recipient_name'][:18]:<18} | {r['status']:<10} | {note}")
        print("=" * 65 + "\n")
