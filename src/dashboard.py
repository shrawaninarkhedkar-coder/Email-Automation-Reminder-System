"""
Interactive Streamlit Dashboard for Email Automation & Reminder System.
Run with: streamlit run src/dashboard.py
"""

import sys
from pathlib import Path

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

try:
    import streamlit as st
    import pandas as pd
except ImportError:
    print("\n[ERROR] Streamlit or Pandas is not installed.")
    print("Please install them to launch the dashboard:")
    print("    pip install streamlit pandas\n")
    sys.exit(1)

from src.config import Config, DATA_DIR, LOGS_DIR, OUTPUTS_DIR, SIMULATED_DIR
from src.data_loader import DataLoader
from src.template_engine import TemplateEngine
from src.scheduler import ReminderScheduler

# Page Configuration
st.set_page_config(
    page_title="Email Automation & Reminder System",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📧 Email Automation & Reminder System")
st.caption("Operations & Workflow Monitoring Dashboard | Proof of Work Portfolio")

# Sidebar Controls
st.sidebar.header("⚙️ Dispatch Settings")
dry_run_toggle = st.sidebar.toggle("Virtual Simulation Mode (Dry Run)", value=Config.DRY_RUN)
st.sidebar.info(
    "💡 **Dry Run Mode**: Safely tests templates, personalizes content, and verifies schedules without sending real emails."
)

loader = DataLoader()
contacts = loader.load_contacts()
reminders = loader.load_reminders()

# Metrics Row
col1, col2, col3, col4 = st.columns(4)

report_file = OUTPUTS_DIR / "delivery_report_sample.csv"
if report_file.exists():
    df_report = pd.read_csv(report_file)
    total_sent = len(df_report[df_report["status"].isin(["Sent", "Simulated"])])
    total_failed = len(df_report[df_report["status"] == "Failed"])
    rate = f"{(total_sent / len(df_report) * 100):.1f}%" if len(df_report) > 0 else "0%"
else:
    df_report = pd.DataFrame()
    total_sent = 0
    total_failed = 0
    rate = "N/A"

col1.metric("Total Contacts", len(contacts))
col2.metric("Scheduled Reminders", len(reminders))
col3.metric("Simulated / Sent", total_sent)
col4.metric("Success Rate", rate)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Delivery Reports & Audit",
    "👥 Contacts Database",
    "⏰ Scheduled Reminders",
    "✉️ Live Template Previewer"
])

with tab1:
    st.subheader("Recent Email Dispatch Log & Audit Trail")
    if not df_report.empty:
        st.dataframe(df_report, use_container_width=True)
        st.download_button(
            "📥 Download Delivery Report (CSV)",
            df_report.to_csv(index=False),
            file_name="email_delivery_report.csv",
            mime="text/csv",
        )
    else:
        st.warning("No delivery report found yet. Click 'Run Batch Dispatch' below to generate.")

    st.divider()
    st.subheader("Trigger Workflow")
    if st.button("🚀 Run Immediate Batch Evaluation"):
        scheduler = ReminderScheduler(dry_run=dry_run_toggle)
        with st.spinner("Processing reminders..."):
            tracker = scheduler.run_batch(force_all=True)
        st.success("Batch run completed! Refresh to view updated audit metrics.")

with tab2:
    st.subheader("Configured Contact List")
    if Config.CONTACTS_FILE.exists():
        df_contacts = pd.read_csv(Config.CONTACTS_FILE)
        st.dataframe(df_contacts, use_container_width=True)
    else:
        st.error("contacts.csv not found!")

with tab3:
    st.subheader("Scheduled Reminder Queue")
    if Config.REMINDERS_FILE.exists():
        df_reminders = pd.read_csv(Config.REMINDERS_FILE)
        st.dataframe(df_reminders, use_container_width=True)
    else:
        st.error("reminders.csv not found!")

with tab4:
    st.subheader("Email Template Personalization Preview")
    selected_template = st.selectbox(
        "Select Email Template",
        ["meeting_reminder", "payment_reminder", "webinar_reminder", "task_reminder"]
    )
    
    # Sample preview context
    sample_context = {
        "name": "Alex Mercer",
        "title": "Quarterly Operations Review",
        "due_date": "2026-11-25",
        "due_time": "14:00",
        "timezone": "Asia/Kolkata",
        "department": "Operations",
        "amount_due": "18,500.00",
        "role": "Operations Manager",
        "meeting_link": "https://meet.google.com/sample-room",
    }

    engine = TemplateEngine()
    try:
        subj, html_content, ctype = engine.render(selected_template, sample_context)
        st.markdown(f"**Subject:** `{subj}`")
        if ctype == "html":
            st.components.v1.html(html_content, height=450, scrolling=True)
        else:
            st.text_area("Plain Text Content", html_content, height=250)
    except Exception as e:
        st.error(f"Error rendering template: {e}")
