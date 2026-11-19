"""
Configuration module for Email Automation & Reminder System.
Handles environment variables, paths, and application logging.
"""

import os
import sys
import logging
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = BASE_DIR / "templates"
LOGS_DIR = BASE_DIR / "logs"
OUTPUTS_DIR = BASE_DIR / "outputs"
SIMULATED_DIR = OUTPUTS_DIR / "simulated_emails"

# Ensure runtime directories exist
LOGS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
SIMULATED_DIR.mkdir(parents=True, exist_ok=True)


def load_env_file(env_path: Path):
    """
    Lightweight fallback parser for .env files if python-dotenv is not installed.
    """
    if not env_path.exists():
        return
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
    except ImportError:
        # Standard library fallback parser
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'").strip('"')
                if k not in os.environ:
                    os.environ[k] = v


# Load .env file
load_env_file(BASE_DIR / ".env")


class Config:
    """Application Configuration Holder"""

    # Dry run switch: Default to True for student safety!
    DRY_RUN: bool = os.getenv("DRY_RUN", "True").lower() in ("true", "1", "yes", "y")

    # SMTP Configuration
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    USE_TLS: bool = os.getenv("USE_TLS", "True").lower() in ("true", "1", "yes", "y")

    # Sender Credentials
    SENDER_NAME: str = os.getenv("SENDER_NAME", "Operations Automation Bot")
    SENDER_EMAIL: str = os.getenv("SENDER_EMAIL", "simulation-noreply@enterprise.local")
    SENDER_PASSWORD: str = os.getenv("SENDER_PASSWORD", "")

    # Scheduler Settings
    CHECK_INTERVAL_SECONDS: int = int(os.getenv("CHECK_INTERVAL_SECONDS", "30"))

    # File & Directory Paths
    BASE_DIR = BASE_DIR
    DATA_DIR = DATA_DIR
    TEMPLATES_DIR = TEMPLATES_DIR
    LOGS_DIR = LOGS_DIR
    OUTPUTS_DIR = OUTPUTS_DIR
    SIMULATED_DIR = SIMULATED_DIR
    CONTACTS_FILE = DATA_DIR / "contacts.csv"
    REMINDERS_FILE = DATA_DIR / "reminders.csv"
    LOG_FILE = LOGS_DIR / "email_automation.log"
    REPORT_FILE = OUTPUTS_DIR / "delivery_report_sample.csv"


def setup_logger(name: str = "EmailAutomation") -> logging.Logger:
    """Configures multi-handler logger (Terminal + File)"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # File handler
        file_handler = logging.FileHandler(Config.LOG_FILE, encoding="utf-8")
        file_format = logging.Formatter(
            "%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

        # Console handler with clear formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_format = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S",
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)

    return logger


logger = setup_logger()
