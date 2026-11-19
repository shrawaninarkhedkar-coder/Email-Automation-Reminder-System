# 📧 Email Automation & Reminder System

> An enterprise-grade, modular Python automation engine designed to schedule, personalize, and dispatch automated notification emails (one-off or recurring), validate contact lists, prevent credential leaks, and generate auditable delivery reports.

[![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-brightgreen.svg)]()
[![Proof of Work](https://img.shields.io/badge/Proof%20of%20Work-Student%20Portfolio-orange.svg)]()

---

## 📌 1. Project Overview

The **Email Automation & Reminder System** automates the repetitive communication workflows common to Operations, Human Resources, Sales, Educational Academies, and Finance teams.

It reads contact details and scheduled reminders from structured data files (CSV), maps dynamic variables into responsive HTML/text email templates, validates email integrity, schedules dispatches based on target timestamps, and sends emails over secure SMTP (or via safe offline virtual simulation). Every send attempt is recorded into audit logs and an exportable CSV delivery report.

---

## ❗ 2. Problem Statement & Industry Relevance

### The Problem
Organizations lose hundreds of hours annually on repetitive manual tasks:
- HR manually following up on document verification and onboarding steps.
- Sales teams forgetting to send follow-up emails after product demos.
- Operations sending calendar reminders for team meetings and webinar dates.
- Accounts teams manually copying invoices to chase overdue payments.

Manual email sending is prone to:
- **Human Error**: Misspelled names, broken links, missed attachments.
- **Missed Deadlines**: Notifications sent too late or forgotten entirely.
- **Lack of Auditability**: No central log to prove whether an email was dispatched.

### The Solution
This automated Python system solves these bottlenecks with zero license fees:
1. **Automated Personalization**: Auto-injects recipient names, meeting links, due amounts, and deadlines.
2. **Scheduled Dispatch Engine**: Triggers notifications exactly when due.
3. **Safe Virtual Simulation**: Enables students and QA engineers to test end-to-end workflows without sending live emails or risking account bans.
4. **Audit Trail & CSV Reporting**: Generates a timestamped delivery log for every processed reminder.

---

## ⚡ 3. Key Features

- **Decoupled Architecture**: Modular design separating Data Ingestion, Template Rendering, SMTP Dispatch, Scheduling, and Audit Tracking.
- **Virtual Simulation Mode (Dry-Run)**: Test the entire pipeline offline; rendered HTML emails are saved directly to `outputs/simulated_emails/` for inspection.
- **RFC-Compliant Email Validation**: Flags invalid email syntax before attempting network calls.
- **Fault-Tolerant Templating**: Custom placeholder substitution that will not crash on missing variables.
- **Multi-Template Support**: Comes pre-configured with Meeting, Payment, Webinar, and Task reminder templates.
- **Live SMTP Transmission**: Built-in support for Gmail App Passwords, Outlook, and Mailtrap with TLS/SSL encryption.
- **Interactive Monitoring Dashboard**: Built-in optional Streamlit UI for visual inspection of contacts, reminders, live template previews, and one-click batch triggers.
- **Comprehensive Logging**: Dual-output logging to both console and `logs/email_automation.log`.

---

## 🛠️ 4. Tech Stack

| Domain | Technology / Library | Description |
| :--- | :--- | :--- |
| **Language** | Python 3.9+ | Core programming language |
| **Data Handling** | `csv`, `pandas` | Structured ingestion of contacts and reminders |
| **Email Protocol** | `smtplib`, `email.message` | TLS/SSL socket connections & MIME message assembly |
| **Scheduling** | `datetime`, `time`, `schedule` | Time comparisons and automated polling loops |
| **Security** | `python-dotenv`, `.gitignore` | Environment variable protection against credential leaks |
| **Logging** | Python `logging` | Formatted multi-handler logging (terminal + file) |
| **Dashboard** | `streamlit` *(optional)* | Interactive web dashboard for operations monitoring |

---

## 📂 5. Folder Structure

```
Email-Automation-Reminder-System/
├── data/
│   ├── contacts.csv                 # Recipient database (names, emails, roles, depts)
│   └── reminders.csv                # Reminders queue (dates, times, links, amounts)
├── templates/
│   ├── meeting_reminder.html        # Responsive HTML template for calendar syncs
│   ├── payment_reminder.html        # Invoice and payment due reminder
│   ├── webinar_reminder.html        # Live event access and speaker invitation
│   └── task_reminder.txt            # Plain-text operational task reminder
├── src/
│   ├── __init__.py                  # Package initializer
│   ├── config.py                    # Environment variable parser, paths, and logger setup
│   ├── data_loader.py               # CSV parsing, email regex validation, and table joins
│   ├── template_engine.py           # Placeholder replacement and subject extraction
│   ├── mailer.py                    # SMTP dispatch engine & safe dry-run simulator
│   ├── scheduler.py                 # Time comparison & batch/daemon execution loop
│   ├── tracker.py                   # Delivery report CSV writer & summary metrics
│   └── dashboard.py                 # Optional Streamlit visual UI
├── outputs/
│   ├── delivery_report_sample.csv   # Generated CSV delivery report
│   └── simulated_emails/            # Rendered HTML email previews from dry-runs
├── logs/
│   └── email_automation.log         # Persistent timestamped audit trail
├── docs/
│   ├── architecture.md              # Detailed architecture diagram and data flows
│   └── interview_qa.md              # 10 interview questions with model answers
├── .env.example                     # Environment template (safe to commit)
├── .gitignore                       # Protects .env, logs, and venvs from Git commits
├── requirements.txt                 # Project dependencies
├── main.py                          # Primary CLI executable
└── test_simulation.py               # Automated verification and proof-of-work test suite
```

---

## 🚀 6. Installation & Setup

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/Email-Automation-Reminder-System.git
cd Email-Automation-Reminder-System
```

### Step 2: Create a Virtual Environment
**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```
*(Note: Core CLI features run using pure Python standard library out of the box!)*

---

## 🔐 7. Environment Configuration

1. Copy the sample environment file:
   ```bash
   cp .env.example .env
   ```
   *(On Windows Command Prompt: `copy .env.example .env`)*

2. Open `.env` in any text editor:
   ```ini
   # Set to True for safe offline testing (No real emails sent)
   DRY_RUN=True

   # SMTP Configuration
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   USE_TLS=True

   # Sender Information
   SENDER_NAME=Operations Team
   SENDER_EMAIL=your_email@gmail.com
   SENDER_PASSWORD=your_16_digit_app_password
   ```

> [!WARNING]
> **Never commit your `.env` file to GitHub!** Verify that `.env` is listed in your `.gitignore` file before running `git add`.

---

## 💻 8. How to Run the Project

### Mode A: Run Safe Virtual Simulation (Recommended for Students)
Executes all reminders in offline simulation mode, validates templates, writes HTML previews, and logs delivery:
```bash
python main.py --dry-run --send-all
```

### Mode B: Inspect Contacts & Reminders Database
```bash
python main.py --list-contacts
python main.py --list-reminders
```

### Mode C: Run Continuous Background Scheduler Loop
Checks every 30 seconds for reminders due at the current time:
```bash
python main.py --loop
```

### Mode D: Send Live Emails via SMTP
*(Requires valid credentials in `.env`)*
```bash
python main.py --live --send-all
```

### Mode E: Run Automated Verification Suite (Proof of Work)
Runs unit validations and outputs sample reports:
```bash
python test_simulation.py
```

### Mode F: Launch Interactive Web Dashboard (Optional)
```bash
streamlit run src/dashboard.py
```

---

## 📊 9. Sample Execution Output

```text
======================================================================
     EMAIL AUTOMATION & SCHEDULED REMINDER WORKFLOW SYSTEM
      Safe Simulation | SMTP Engine | CSV Reporting & Audit
======================================================================

[MODE] VIRTUAL SIMULATION (Dry Run) Active - Safe for student testing & GitHub proof of work.
22:06:00 [INFO] Loaded 7 contacts from contacts.csv
22:06:00 [INFO] Loaded 7 reminders from reminders.csv
22:06:00 [INFO] Starting batch evaluation of 7 reminder tasks...
22:06:00 [INFO] [SIMULATION] [ID: R101] To: aarav.sharma@example.com | Subject: 'Meeting Reminder: Quarterly Sprint Planning' -> SUCCESS (Dry Run)
22:06:01 [INFO] [SIMULATION] [ID: R102] To: priya.patel@example.com | Subject: 'Reminder: Submit Monthly Payroll Audit' -> SUCCESS (Dry Run)
22:06:01 [INFO] [SIMULATION] [ID: R103] To: rohan.verma@example.com | Subject: 'Payment Due Notice: Pending Software License Invoice' -> SUCCESS (Dry Run)
22:06:01 [INFO] [SIMULATION] [ID: R104] To: ananya.iyer@example.com | Subject: 'Exclusive Webinar Access: Modern Python Automation Masterclass' -> SUCCESS (Dry Run)
22:06:01 [INFO] [SIMULATION] [ID: R105] To: vikram.malhotra@example.com | Subject: 'Meeting Reminder: Enterprise Client Follow-up Call' -> SUCCESS (Dry Run)
22:06:01 [INFO] [SIMULATION] [ID: R106] To: neha.gupta@example.com | Subject: 'Reminder: Update Q4 Marketing KPIs' -> SUCCESS (Dry Run)
22:06:01 [ERROR] [R107] Dispatch rejected: Invalid recipient email address: 'invalid-email-format'

=================================================================
          EMAIL DISPATCH & REMINDER EXECUTION SUMMARY          
=================================================================
 Mode               : SIMULATION (DRY-RUN)
 Total Evaluated    : 7
 Succeeded/Simulated: 6
 Failed / Rejected  : 1
 Success Rate       : 85.71%
 Report Saved To    : delivery_report_sample.csv
-----------------------------------------------------------------
ID     | Recipient          | Status     | Error / Note
-----------------------------------------------------------------
R101   | Aarav Sharma       | Simulated  | OK
R102   | Priya Patel        | Simulated  | OK
R103   | Rohan Verma        | Simulated  | OK
R104   | Ananya Iyer        | Simulated  | OK
R105   | Vikram Malhotra    | Simulated  | OK
R106   | Neha Gupta         | Simulated  | OK
R107   | Invalid User       | Failed     | Invalid recipient email f...
=================================================================
```

---

## 📈 10. Generated Delivery Report Sample (`outputs/delivery_report_sample.csv`)

| reminder_id | recipient_name | recipient_email | department | reminder_title | status | error_reason | timestamp |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **R101** | Aarav Sharma | aarav.sharma@example.com | Engineering | Quarterly Sprint Planning | Simulated | None | 2026-11-18 22:06:00 |
| **R102** | Priya Patel | priya.patel@example.com | Human Resources | Submit Monthly Payroll Audit | Simulated | None | 2026-11-18 22:06:01 |
| **R103** | Rohan Verma | rohan.verma@example.com | Finance | Pending Software License Invoice | Simulated | None | 2026-11-18 22:06:01 |
| **R107** | Invalid User | invalid-email-format | Engineering | Intern Onboarding Sync | Failed | Invalid recipient email format | 2026-11-18 22:06:01 |

---

## 🎓 11. Learning Outcomes

By completing and presenting this project, you demonstrate competence in:
1. **Modular Python Architecture**: Clean separation of concerns with isolated modules and configuration classes.
2. **Protocol Engineering (SMTP/MIME)**: Establishing encrypted TLS/SSL sessions, structuring multipart MIME bodies, and formatting RFC headers.
3. **Data Pipelines**: Parsing, validating, and cross-joining disparate CSV files.
4. **Resilience & Error Handling**: Pre-flight regex validation and graceful exception recovery.
5. **Security Best Practices**: Decoupling secrets via `.env`, creating `.env.example`, and using `.gitignore`.
6. **Observability**: Building dual-output logging engines and exportable audit reports.

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
