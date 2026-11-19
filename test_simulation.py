"""
End-to-End Simulation Test Script
Runs automated verification of the Email Automation & Reminder System.
Generates sample delivery logs and CSV reports for GitHub proof of work.
"""

import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from src.config import Config, logger, SIMULATED_DIR
from src.data_loader import DataLoader
from src.template_engine import TemplateEngine
from src.scheduler import ReminderScheduler


def run_test():
    print("=================================================================")
    print("    RUNNING AUTOMATED SIMULATION & VERIFICATION TEST SUITE       ")
    print("=================================================================")

    # Step 1: Validate Data Loader
    loader = DataLoader()
    contacts = loader.load_contacts()
    reminders = loader.load_reminders()
    assert len(contacts) > 0, "Contacts should not be empty"
    assert len(reminders) > 0, "Reminders should not be empty"
    print(f"[TEST 1 PASS] Loaded {len(contacts)} contacts and {len(reminders)} reminders.")

    # Step 2: Validate Email Validation Logic
    invalid_contacts = [c for c in contacts.values() if not c["is_valid_email"]]
    assert len(invalid_contacts) >= 1, "Expected at least 1 deliberately invalid contact for error testing"
    print(f"[TEST 2 PASS] Email validation detected invalid contact: {invalid_contacts[0]['name']}")

    # Step 3: Validate Template Engine
    engine = TemplateEngine()
    subject, content, ctype = engine.render("meeting_reminder", {
        "name": "Test Engineer",
        "title": "Automated Unit Test Verification",
        "due_date": "2026-11-20",
        "due_time": "15:00",
        "timezone": "UTC",
        "department": "Engineering",
        "meeting_link": "https://example.com/test-room",
    })
    assert "Test Engineer" in content, "Rendered content should contain recipient name"
    assert "Automated Unit Test Verification" in content, "Rendered content should contain title"
    print(f"[TEST 3 PASS] Template engine rendered HTML email with subject: '{subject}'")

    # Step 4: Run Full Virtual Simulation Batch
    scheduler = ReminderScheduler(dry_run=True)
    tracker = scheduler.run_batch(force_all=True)
    metrics = tracker.get_summary_metrics()

    assert metrics["total_processed"] > 0, "Should have processed reminders"
    assert metrics["successful"] > 0, "Should have simulated successful sends"
    assert metrics["failed"] >= 1, "Should have recorded deliberate failure for invalid email"
    print(f"[TEST 4 PASS] Scheduler batch completed with {metrics['success_rate_pct']}% success rate.")

    # Step 5: Check output files
    assert Config.REPORT_FILE.exists(), "Delivery report CSV must exist"
    assert Config.LOG_FILE.exists(), "Log file must exist"
    sim_previews = list(SIMULATED_DIR.glob("*.html"))
    assert len(sim_previews) > 0, "Simulated email HTML files should be generated in outputs/simulated_emails/"
    print(f"[TEST 5 PASS] Generated delivery report CSV, logs, and {len(sim_previews)} HTML previews.")

    print("\nALL VERIFICATION TESTS COMPLETED SUCCESSFULLY!")
    print(f"Log location: {Config.LOG_FILE}")
    print(f"Report location: {Config.REPORT_FILE}")
    print("=================================================================\n")


if __name__ == "__main__":
    run_test()
