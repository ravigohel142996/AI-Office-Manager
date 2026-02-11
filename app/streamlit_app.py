from __future__ import annotations

import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import train_test_split

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.services.ai_engine import AIEngine
from app.services.database import Lead, SessionLocal, Task, Ticket, User, init_db

st.set_page_config(page_title="AI Office Manager", layout="wide", page_icon="🤖")
init_db()
ai = AIEngine()


def db_session():
    return SessionLocal()


def auth_gate() -> None:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return

    st.title("🔐 AI Office Manager Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        with db_session() as db:
            user = db.query(User).filter(User.username == username, User.password == password).first()
        if user:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials. Default: admin/admin123")
    st.stop()


def kpi_cards() -> None:
    with db_session() as db:
        tasks = db.query(Task).count()
        tickets = db.query(Ticket).count()
        leads = db.query(Lead).count()

    productivity = min(100, 45 + tasks * 3)
    cost_saving = 15000 + (leads * 800)
    tasks_completed = tasks + tickets

    c1, c2, c3 = st.columns(3)
    c1.metric("Productivity", f"{productivity}%", delta="+5%")
    c2.metric("Cost Saving", f"${cost_saving:,.0f}", delta="+$1,200")
    c3.metric("Tasks Completed", tasks_completed, delta="+9")


def dashboard_home() -> None:
    st.title("🏢 AI Office Manager")
    st.caption("Central workforce automation platform for HR, Analytics, Support, Admin, and Sales")
    kpi_cards()

    timeline = pd.DataFrame(
        {
            "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "Automation ROI": [8, 12, 16, 21, 29, 35],
        }
    )
    fig = px.area(timeline, x="Month", y="Automation ROI", title="Automation ROI Trend")
    st.plotly_chart(fig, use_container_width=True)


def hr_module() -> None:
    st.header("👥 HR Bot")
    tabs = st.tabs(["Attendance", "Resume Analyzer", "Leave Requests", "Interview", "Performance"])

    with tabs[0]:
        team = ["Ava", "Ben", "Cara", "Dan", "Eli"]
        attendance = pd.DataFrame(
            {
                "Employee": team,
                "Present Days": np.random.randint(18, 23, size=5),
                "Late Days": np.random.randint(0, 4, size=5),
            }
        )
        st.dataframe(attendance, use_container_width=True)
        st.plotly_chart(px.bar(attendance, x="Employee", y="Present Days", title="Attendance Simulator"), use_container_width=True)

    with tabs[1]:
        resume_text = st.text_area("Paste resume text")
        if st.button("Analyze Resume"):
            if not resume_text.strip():
                st.warning("Please provide resume text")
            else:
                score = min(100, len(resume_text.split()) // 3)
                st.success(f"Resume Score: {score}/100")
                st.info(ai.process("hr", f"Evaluate resume for skills and fit: {resume_text[:180]}"))

    with tabs[2]:
        with st.form("leave_form"):
            employee = st.text_input("Employee Name")
            leave_type = st.selectbox("Leave Type", ["Sick", "Casual", "Annual"])
            days = st.number_input("Days", min_value=1, max_value=30, value=2)
            submitted = st.form_submit_button("Submit Leave Request")
        if submitted:
            st.success(f"Leave request recorded: {employee}, {leave_type}, {days} days")

    with tabs[3]:
        candidate = st.text_input("Candidate Name")
        interviewer = st.text_input("Interviewer")
        interview_date = st.date_input("Interview Date", value=date.today() + timedelta(days=3))
        if st.button("Schedule Interview"):
            st.success(f"Interview scheduled for {candidate} with {interviewer} on {interview_date}")

    with tabs[4]:
        perf = pd.DataFrame(
            {
                "Employee": ["Ava", "Ben", "Cara", "Dan", "Eli"],
                "Performance Score": [88, 79, 93, 74, 85],
                "Goal Completion %": [90, 80, 95, 76, 88],
            }
        )
        st.dataframe(perf, use_container_width=True)
        st.plotly_chart(px.scatter(perf, x="Performance Score", y="Goal Completion %", text="Employee", title="Performance Report"), use_container_width=True)


def analyst_module() -> None:
    st.header("📊 Analyst Bot")
    uploaded = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded is not None:
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_csv("data/sample_sales.csv")

    st.dataframe(df.head(), use_container_width=True)
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

    if len(numeric_cols) >= 2:
        x_col = st.selectbox("X Axis", numeric_cols, index=0)
        y_col = st.selectbox("Y Axis", numeric_cols, index=min(1, len(numeric_cols)-1))
        st.plotly_chart(px.line(df, x=x_col, y=y_col, title="Trend Analysis"), use_container_width=True)

    if len(numeric_cols) >= 2:
        model_df = df[numeric_cols].dropna()
        target = numeric_cols[-1]
        features = model_df[numeric_cols[:-1]]
        y = model_df[target]
        model = LinearRegression().fit(features, y)
        pred = model.predict(features.tail(1))[0]
        st.info(f"Prediction model output for next {target}: {pred:.2f}")

    st.markdown("### Monthly Report")
    st.write(ai.process("analyst", "Generate monthly trend and anomaly report"))


def support_module() -> None:
    st.header("🎧 Support Bot")
    tab1, tab2, tab3, tab4 = st.tabs(["AI Chatbot", "Ticket System", "Auto Reply", "Complaint Classifier"])

    with tab1:
        user_query = st.text_input("Customer question")
        if st.button("Get AI Response"):
            st.write(ai.process("support", user_query))

    with tab2:
        with st.form("ticket_form"):
            customer = st.text_input("Customer")
            issue = st.text_area("Issue")
            category = st.selectbox("Category", ["Billing", "Technical", "Logistics", "General"])
            submitted = st.form_submit_button("Create Ticket")
        if submitted:
            with db_session() as db:
                ticket = Ticket(customer=customer, issue=issue, category=category)
                db.add(ticket)
                db.commit()
            st.success("Ticket created")

        with db_session() as db:
            tickets = db.query(Ticket).order_by(Ticket.created_at.desc()).all()
            ticket_df = pd.DataFrame(
                [
                    {
                        "ID": t.id,
                        "Customer": t.customer,
                        "Issue": t.issue,
                        "Category": t.category,
                        "Status": t.status,
                    }
                    for t in tickets
                ]
            )
        st.dataframe(ticket_df, use_container_width=True)

    with tab3:
        message = st.text_area("Incoming customer message")
        if st.button("Generate Auto Reply"):
            st.write(ai.process("support", f"Draft polite auto-reply for: {message}"))

    with tab4:
        complaint = st.text_area("Complaint text")
        if st.button("Classify Complaint"):
            label = "Technical" if "bug" in complaint.lower() else "General"
            st.success(f"Predicted category: {label}")


def admin_module() -> None:
    st.header("🗂️ Admin Bot")
    tab1, tab2, tab3, tab4 = st.tabs(["Task Manager", "Calendar", "Reminders", "Email Generator"])

    with tab1:
        with st.form("task_form"):
            title = st.text_input("Task Title")
            owner = st.text_input("Owner")
            due_date = st.date_input("Due Date")
            priority = st.selectbox("Priority", ["Low", "Medium", "High"])
            submitted = st.form_submit_button("Add Task")
        if submitted and title and owner:
            with db_session() as db:
                db.add(Task(title=title, owner=owner, due_date=str(due_date), priority=priority))
                db.commit()
            st.success("Task added")

        with db_session() as db:
            tasks = db.query(Task).all()
        st.dataframe(pd.DataFrame([{"Title": t.title, "Owner": t.owner, "Due": t.due_date, "Priority": t.priority, "Status": t.status} for t in tasks]), use_container_width=True)

    with tab2:
        date_selected = st.date_input("Calendar Scheduler", value=date.today())
        st.info(f"Scheduled events for {date_selected}: Team sync at 10:00 AM")

    with tab3:
        reminder = st.text_input("Reminder")
        reminder_time = st.time_input("Time", value=datetime.now().time())
        if st.button("Set Reminder"):
            st.success(f"Reminder set: {reminder} at {reminder_time}")

    with tab4:
        purpose = st.text_input("Email purpose")
        if st.button("Generate Email"):
            st.code(ai.process("admin", f"Generate concise professional email for: {purpose}"))


def sales_module() -> None:
    st.header("💼 Sales Bot")
    tab1, tab2, tab3, tab4 = st.tabs(["Lead Form", "Lead Scoring", "Sales Forecast", "CRM Dashboard"])

    with tab1:
        with st.form("lead_form"):
            name = st.text_input("Lead Name")
            email = st.text_input("Email")
            company = st.text_input("Company")
            source = st.selectbox("Source", ["Website", "Referral", "Email", "LinkedIn"])
            deal_size = st.number_input("Potential Deal Size", min_value=100.0, value=5000.0)
            submitted = st.form_submit_button("Save Lead")
        if submitted:
            score = 40 + (deal_size / 1000) + (10 if source == "Referral" else 0)
            with db_session() as db:
                db.add(Lead(name=name, email=email, company=company, source=source, deal_size=deal_size, score=score))
                db.commit()
            st.success(f"Lead saved with score {score:.1f}")

    with tab2:
        data = pd.read_csv("data/sample_leads.csv")
        X = data[["deal_size", "engagement", "meetings"]]
        y = data["converted"]
        X_train, X_test, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)
        model = LogisticRegression().fit(X_train, y_train)
        prob = model.predict_proba([[10000, 70, 2]])[0][1]
        st.metric("Example Lead Conversion Probability", f"{prob*100:.1f}%")

    with tab3:
        forecast_df = pd.read_csv("data/sample_sales.csv")
        model = LinearRegression().fit(forecast_df[["month_index"]], forecast_df[["revenue"]])
        next_rev = model.predict([[forecast_df["month_index"].max() + 1]])[0][0]
        st.metric("Next Month Forecast", f"${next_rev:,.0f}")
        st.plotly_chart(px.line(forecast_df, x="month", y="revenue", markers=True, title="Sales Forecast Trend"), use_container_width=True)

    with tab4:
        with db_session() as db:
            leads = db.query(Lead).all()
        lead_df = pd.DataFrame([{"Name": l.name, "Company": l.company, "Source": l.source, "Deal Size": l.deal_size, "Score": l.score} for l in leads])
        st.dataframe(lead_df, use_container_width=True)


def main() -> None:
    auth_gate()
    st.sidebar.title("AI Workforce Bots")
    section = st.sidebar.radio(
        "Departments",
        ["Dashboard", "HR Bot", "Analyst Bot", "Support Bot", "Admin Bot", "Sales Bot"],
    )
    st.sidebar.success(f"Logged in as {st.session_state.get('username', 'admin')}")

    if section == "Dashboard":
        dashboard_home()
    elif section == "HR Bot":
        hr_module()
    elif section == "Analyst Bot":
        analyst_module()
    elif section == "Support Bot":
        support_module()
    elif section == "Admin Bot":
        admin_module()
    elif section == "Sales Bot":
        sales_module()


if __name__ == "__main__":
    main()
