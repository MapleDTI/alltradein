import streamlit as st
import pandas as pd
import datetime
from io import BytesIO

# -----------------------------
# User Credentials and Access Rights
# -----------------------------
users = {
    "sandesh": {"name": "Sandesh Kadam", "password": "pass123", "access": ["normal_tradein"]},
    "kavish": {"name": "Kavish Shah", "password": "pass123", "access": ["normal_tradein"]},
    "vishwa": {"name": "Vishwa Sanghavi", "password": "pass123", "access": ["normal_tradein"]},
    "karan": {"name": "Karan Podaval", "password": "pass123", "access": ["easy_ozy"]},
    "callcenter": {"name": "Call Center User", "password": "pass123", "access": ["call_center"]},
    "admin": {"name": "Admin", "password": "admin", "access": ["all"]},
}

# -----------------------------
# Login Function
# -----------------------------
def login():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("User ID")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username in users and users[username]["password"] == password:
            st.session_state.user = username
            st.session_state.logged_in = True
        else:
            st.sidebar.error("Invalid credentials")

# -----------------------------
# Data Entry UI
# -----------------------------
def normal_tradein_ui():
    st.subheader("Normal Trade-In")
    date = st.date_input("Date", datetime.date.today())
    platform = st.selectbox("Platform", ["South", "West"])
    cashify = st.number_input("Cashify", min_value=0)
    servify = st.number_input("Servify", min_value=0)
    return {
        "DATE": date,
        "PLATFORM": platform,
        "NT_CASHIFY": cashify,
        "NT_SERVIFY": servify
    }

def easy_ozy_ui():
    st.subheader("Easy Ozy")
    eup_cashify = st.number_input("EUP Trading - Cashify", min_value=0)
    eup_servify = st.number_input("EUP Trading - Servify", min_value=0)
    eup_acp_combo = st.number_input("EUP ACP Combo", min_value=0)
    eup_app_combo = st.number_input("EUP APP Combo", min_value=0)
    eup_standalone = st.number_input("EUP Standalone/Exchange", min_value=0)
    return {
        "EUP_CASHIFY": eup_cashify,
        "EUP_SERVIFY": eup_servify,
        "EUP_ACP_COMBO": eup_acp_combo,
        "EUP_APP_COMBO": eup_app_combo,
        "EUP_STANDALONE": eup_standalone
    }

def call_center_ui():
    st.subheader("Call Center")
    platform = st.selectbox("Platform", ["South", "West"], key="cc_platform")
    dials = st.number_input("Dials", min_value=0)
    connects = st.number_input("Connects", min_value=0)
    prospects = st.number_input("Prospects", min_value=0)
    leads = st.number_input("Leads", min_value=0)
    sales = st.number_input("Sales", min_value=0)
    return {
        "CC_PLATFORM": platform,
        "DIALS": dials,
        "CONNECTS": connects,
        "PROSPECTS": prospects,
        "LEADS": leads,
        "SALES": sales
    }

# -----------------------------
# Main App
# -----------------------------
st.set_page_config(page_title="Master Data Entry Dashboard", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

if not st.session_state.logged_in:
    login()
else:
    st.sidebar.success(f"Logged in as: {users[st.session_state.user]['name']}")
    access = users[st.session_state.user]['access']
    entry = {}

    if "normal_tradein" in access or "all" in access:
        entry.update(normal_tradein_ui())

    if "easy_ozy" in access or "all" in access:
        entry.update(easy_ozy_ui())

    if "call_center" in access or "all" in access:
        entry.update(call_center_ui())

    # Placeholder for future Logistics entry and display area
    # entry.update(logistics_ui())

    # Save and download section
    if st.button("Save Entry"):
        df = pd.DataFrame([entry])
        if "data" in st.session_state:
            st.session_state.data = pd.concat([st.session_state.data, df], ignore_index=True)
        else:
            st.session_state.data = df
        st.success("Entry Saved!")

    if "data" in st.session_state:
        st.subheader("Collected Entries")
        st.dataframe(st.session_state.data)

        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            st.session_state.data.to_excel(writer, index=False, sheet_name="Data")
            writer.close()
        st.download_button("Download Excel", data=output.getvalue(), file_name="master_data.xlsx", mime="application/vnd.ms-excel")
