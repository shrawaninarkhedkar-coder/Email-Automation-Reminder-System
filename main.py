"""
Email Automation & Reminder System - Main CLI Entry Point
Author: Student / Automation Engineer
GitHub Portfolio Project
"""

import argparse
import sys
from pathlib import Path

from src.config import Config, logger
from src.data_loader import DataLoader
from src.scheduler import ReminderScheduler
from src.tracker import DeliveryTracker


def print_banner():
    banner = """
======================================================================
     EMAIL AUTOMATION & SCHEDULED REMINDER WORKFLOW SYSTEM
      Safe Simulation | SMTP Engine | CSV Reporting & Audit
======================================================================
"""
    print(banner)


def show_contacts():
    loader = DataLoader()
    contacts = loader.load_contacts()
    print(f"\n--- Contacts Database ({len(contacts)} records) ---")
    print(f"{'ID':<6} | {'Name':<18} | {'Email':<28} | {'Department':<15} | {'Valid'}")
    print("-" * 80)
    for cid, c in contacts.items():
        v = "Yes" if c["is_valid_email"] else "NO (Invalid)"
        print(f"{cid:<6} | {c['name'][:18]:<18} | {c['email'][:28]:<28} | {c['department'][:15]:<15} | {v}")
    print("-" * 80 + "\n")


def show_reminders():
    loader = DataLoader()
    reminders = loader.load_reminders()
    print(f"\n--- Scheduled Reminders ({len(reminders)} records) ---")
    print(f"{'ID':<6} | {'Contact':<8} | {'Type':<12} | {'Due Date':<12} | {'Time':<6} | {'Title'}")
    print("-" * 80)
    for r in reminders:
        print(f"{r['reminder_id']:<6} | {r['contact_id']:<8} | {r['reminder_type']:<12} | {r['due_date']:<12} | {r['due_time']:<6} | {r['title']}")
    print("-" * 80 + "\n")


def main():
    print_banner()

    parser = argparse.ArgumentParser(
        description="Email Automation & Reminder System - Industrial Python Workflow"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=None,
        help="Run in virtual simulation mode (No real emails sent, previews saved to outputs/)",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Run in LIVE SMTP mode (Sends real emails using credentials in .env)",
    )
    parser.add_argument(
        "--send-all",
        action="store_true",
        help="Force process all reminders immediately (ignores future due dates for instant testing)",
    )
    parser.add_argument(
        "--loop",
        action="store_true",
        help="Run continuous scheduler daemon loop polling every N seconds",
    )
    parser.add_argument(
        "--list-contacts",
        action="store_true",
        help="Display all contacts loaded from CSV",
    )
    parser.add_argument(
        "--list-reminders",
        action="store_true",
        help="Display all reminders loaded from CSV",
    )

    args = parser.parse_args()

    # Determine execution mode
    if args.live:
        dry_run = False
        print("[MODE] LIVE SMTP Transmission Mode Active")
        if not Config.SENDER_PASSWORD:
            logger.warning("No SENDER_PASSWORD detected in .env! Emails may fail if authentication is required.")
    elif args.dry_run is not None:
        dry_run = args.dry_run
    else:
        # Default from Config (Defaults to True for student safety)
        dry_run = Config.DRY_RUN

    if dry_run:
        print("[MODE] VIRTUAL SIMULATION (Dry Run) Active - Safe for student testing & GitHub proof of work.")

    if args.list_contacts:
        show_contacts()
        return

    if args.list_reminders:
        show_reminders()
        return

    scheduler = ReminderScheduler(dry_run=dry_run)

    if args.loop:
        scheduler.run_continuous_loop()
    else:
        # Default behavior: run batch
        # If --send-all specified, process all reminders
        force_all = args.send_all
        if not force_all:
            print("[INFO] Evaluating due reminders. (Use --send-all to force process all sample reminders).")
        scheduler.run_batch(force_all=force_all)


if __name__ == "__main__":
    main()
