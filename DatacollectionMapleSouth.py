import streamlit as st #type:ignore
import pandas as pd #type:ignore
from datetime import date, datetime
from io import BytesIO

st.set_page_config(page_title="Trade-in Data Collection", layout="wide")

# Login credentials
users = {
    "Sandeep Selvamni": "SS@123"
}

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:  
    st.title("🔐 Login Panel")
    username = st.text_input("User ID")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid credentials")
    st.stop()

# Load store data from Excel
@st.cache_data
def load_store_data():
    return pd.read_excel("Spoc Data File.xlsx")  # Make sure this file is available in the same folder

store_df = load_store_data()
store_names = store_df["Store Name "].tolist()

if 'data' not in st.session_state:
    st.session_state.data = []

st.title("📊 Trade-in Performance Data Entry")

st.markdown("### 🗓️ Select Date")
date_input = st.date_input("Date", value=date.today())

st.markdown("### 🏬 Store Details")
col1, col2, col3, col4 = st.columns(4)
with col1:
    region = "South"
    st.text_input("Region", region, disabled=True)
with col2:
    store_selected = st.selectbox("Store Name ", store_names)
    selected_row = store_df[store_df["Store Name "] == store_selected].iloc[0]
with col3:
    spoc_name = st.text_input("Spoc Name", value=selected_row["Spoc Name "], disabled=True)
with col4:
    tradein_target = st.number_input("Trade-in Target for April Month ", value=int(selected_row["Trade-in Target for the Month "]), disabled=True)

col5, col6 = st.columns(2)
with col5:
    location = st.text_input("Location", value=selected_row["Location"], disabled=True)
with col6:
    weekly_off = st.text_input("Weekly Off", value=selected_row["Weekly Off "], disabled=True)

st.markdown("### 📋 Trade-in Performance Details")
total_maple_mserv = st.number_input("Maple & Mserv TOTAL (Daily Entry)", min_value=0, step=1)
tradein_lost_cashify = st.number_input("Trade-in Lost with Cashify (Daily Entry)", min_value=0, step=1)

# Store trade-in entry data daily per SPOC
data_row = {
    "Date": date_input,
    "User": st.session_state.username,
    "Region": region,
    "Location": location,
    "Store Name": store_selected,
    "Weekly Off": weekly_off,
    "Spoc Name": spoc_name,
    "Trade-in Target April Month": int(selected_row["Trade-in Target for the Month "]),
    "Maple & Mserv TOTAL": total_maple_mserv,
    "Trade-in Lost with Cashify": tradein_lost_cashify,
}

if st.button("Add Entry"):
    st.session_state.data.append(data_row)
    st.success("Entry added successfully!")

# Recalculate KPIs
if st.session_state.data:
    df = pd.DataFrame(st.session_state.data)

    df_filtered = df[df["Spoc Name"] == spoc_name]
    total_mtd_maple = df_filtered["Maple & Mserv TOTAL"].sum()
    total_lost_cashify = df_filtered["Trade-in Lost with Cashify"].sum()
    tradein_target = int(selected_row["Trade-in Target for the Month "])

    mtd_achieved = (total_mtd_maple / tradein_target * 100) if tradein_target > 0 else 0
    market_share = (total_mtd_maple / (total_mtd_maple + total_lost_cashify) * 100) if (total_mtd_maple + total_lost_cashify) > 0 else 0

    st.metric("📊 Maple MTD Achieved %", f"{mtd_achieved:.2f}%")
    st.metric("📈 Market Share %", f"{market_share:.2f}%")

st.markdown("### 👥 Spoc & Buy-Back Remarks (For Lost Trade-ins Only)")
col7, col8 = st.columns(2)
with col7:
    spoc_remarks = st.text_area("Spoc Remarks")
    buyback_spoc = st.text_input("Buy-Back Team Spoc")
    device_type = st.text_input("Device Type (Lost to Cashify)")
    model_variant = st.text_input("Model & Variant (Lost to Cashify)")
    deal_lost_location = st.text_input("Location of SPOC When Deal Lost")
with col8:
    buyback_remark = st.text_area("Buy-Back Team Spoc Remark")
    device_condition = st.selectbox("Devices Condition", ["New", "Good", "Average", "Poor", "Dead"])
    cashify_available = st.selectbox("Cashify Available Spoc (YES/NO)", ["YES", "NO"])
    device_dead = st.selectbox("If Devices is dead YES/NO", ["YES", "NO"])
    cashify_price = st.number_input("Cashify Price (Lost Only)", min_value=0.0, step=0.1)
    maple_given_price = st.number_input("Maple Given Price (Lost Only)", min_value=0.0, step=0.1)

if st.button("Add Lost Trade-in Remarks"):
    remark_row = {
        "Date": date_input,
        "Store Name": store_selected,
        "Spoc Name": spoc_name,
        "Device Type": device_type,
        "Model & Variant": model_variant,
        "SPOC Deal Lost Location": deal_lost_location,
        "Cashify Price": cashify_price,
        "Maple Given Price": maple_given_price,
        "Spoc Remarks": spoc_remarks,
        "Buy-Back Team Spoc": buyback_spoc,
        "Buy-Back Team Spoc Remark": buyback_remark,
        "Devices Condition": device_condition,
        "Cashify Available Spoc (YES/NO)": cashify_available,
        "If Devices is dead YES/NO": device_dead
    }
    if 'remarks' not in st.session_state:
        st.session_state.remarks = []
    st.session_state.remarks.append(remark_row)
    st.success("Lost trade-in remark added!")

# Display data and download option
if st.session_state.data:
    st.markdown("### 📄 Collected Daily Trade-in Data")
    df = pd.DataFrame(st.session_state.data)
    st.dataframe(df)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Daily Trade-in')
        if 'remarks' in st.session_state:
            pd.DataFrame(st.session_state.remarks).to_excel(writer, index=False, sheet_name='Lost Trade-ins')
        writer.close()
    excel_data = output.getvalue()

    st.download_button(
        label="📥 Download Excel File",
        data=excel_data,
        file_name="trade_in_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
