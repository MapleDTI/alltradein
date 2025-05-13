import streamlit as st
import hashlib
import plotly
import fpdf

# ✅ Set Streamlit page config ONLY ONCE here
st.set_page_config(page_title="Trade-in KPI Dashboard", layout="wide")

# Hashing passwords for basic security (can be expanded with real auth systems)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Users and their (hashed) passwords
users = {
    "Mahesh Shetty": hash_password("mahesh123"),
    "Manil Shetty": hash_password("manil123"),
    "Madhurima Das": hash_password("madhurima123"),
    "Hardik Shah": hash_password("hardik123"),
    "Sandesh Kadam": hash_password("sandesh123"),
    "Vishwa Sanghavi": hash_password("vishwa123"),
    "Kavish Shah": hash_password("kavish123")
}

# Function to verify login
def login(username, password):
    return username in users and users[username] == hash_password(password)

# Streamlit UI for login
def login_panel():
    st.title("🔐 Login Panel")

    with st.form("login_form", clear_on_submit=False):
        username = st.selectbox("Select your username", list(users.keys()))
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if login(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome, {username}!")
                st.rerun()
            else:
                st.error("Invalid username or password.")

# Initialize session state if not already set
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 🚫 Only show pages if user is logged in
if not st.session_state.logged_in:
    login_panel()
else:
    st.success(f"✅ You are logged in as {st.session_state.username}")
    
    # -- Page Setup --
    CRL_Trade_In_Comparison = st.Page(
        page="views/CPLcomparisonboard.py",
        title="CPL Trade-in Comparison",
    )

    South_monthly_tradin_comparison = st.Page(
        page="views/South_comparison.py",
        title="South Region Trade-in comparison",
    )

    Over_all_SPOC_Review = st.Page(
        page="views/South-west-spoc-review.py",
        title="Over all Spoc Review",
    )

    # -- Navigate Setup [Only after login] --
    pg = st.navigation(pages=[
        CRL_Trade_In_Comparison,
        South_monthly_tradin_comparison,
        Over_all_SPOC_Review
    ])

    # -- Run the Navigation --
    pg.run()
