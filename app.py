import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- DB SETUP ---
conn = sqlite3.connect("recruitment.db", check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS recruitment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT,
    date_opened TEXT,
    date_closed TEXT,
    candidates_interviewed INTEGER,
    hired_candidate TEXT
)
''')
conn.commit()

# --- FUNCTIONS ---
def add_data(role, date_opened, date_closed, candidates, hired):
    c.execute('''
    INSERT INTO recruitment 
    (role, date_opened, date_closed, candidates_interviewed, hired_candidate)
    VALUES (?, ?, ?, ?, ?)
    ''', (role, date_opened, date_closed, candidates, hired))
    conn.commit()

def view_data():
    c.execute("SELECT * FROM recruitment")
    return c.fetchall()

def calculate_time_to_hire(opened, closed):
    d1 = datetime.strptime(opened, "%Y-%m-%d")
    d2 = datetime.strptime(closed, "%Y-%m-%d")
    return (d2 - d1).days

# --- UI ---
st.title("📌 Recruitment Tracker")

menu = ["Add Record", "View Records"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Add Record":
    st.subheader("Add Recruitment Record")

    role = st.text_input("Role")
    date_opened = st.date_input("Date Opened")
    date_closed = st.date_input("Date Closed")
    candidates = st.number_input("Candidates Interviewed", min_value=0)
    hired = st.text_input("Hired Candidate")

    if st.button("Save"):
        add_data(
            role,
            str(date_opened),
            str(date_closed),
            int(candidates),
            hired
        )
        st.success("Record saved!")

elif choice == "View Records":
    st.subheader("All Recruitment Records")

    data = view_data()

    if data:
        df = pd.DataFrame(data, columns=[
            "ID", "Role", "Date Opened", "Date Closed",
            "Candidates", "Hired Candidate"
        ])

        # KPI Calculation
        df["Time to Hire (days)"] = df.apply(
            lambda row: calculate_time_to_hire(
                row["Date Opened"], row["Date Closed"]
            ), axis=1
        )

        df["KPI Status"] = df["Time to Hire (days)"].apply(
            lambda x: "✅ On Target" if x <= 30 else "❌ Delayed"
        )

        st.dataframe(df)

        avg_time = df["Time to Hire (days)"].mean()
        st.metric("Average Time to Hire", f"{avg_time:.1f} days")

    else:
        st.info("No records yet.")
