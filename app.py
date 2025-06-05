import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Google Sheet URL
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1f-sfZ1uoSlQQ0jBuiIQNuRdz7fjYo1BNZEOTQS_FS50/edit?gid=0").sheet1

# SPOC database (generated from provided details)
spoc_database = {
    "Sanni Vishwakarma": {"password": "spoc_sanni", "store_name": "IPLANET @ JP NAGAR", "city": "Bangalore", "store_state": "Karnataka", "zone": "South"},
    "Gopi": {"password": "spoc_gopi", "store_name": "IPLANET @ KAMANAHALLI", "city": "Bangalore", "store_state": "Karnataka", "zone": "South"},
    "Sachin Rathor": {"password": "spoc_sachin", "store_name": "IPLANET @ VIDYARANYAPURA", "city": "Bangalore", "store_state": "Karnataka", "zone": "South"},
    "Manjunath": {"password": "spoc_manjunath", "store_name": "IPLANET @ JAYANAGAR", "city": "Bangalore", "store_state": "Karnataka", "zone": "South"},
    "Eshwar": {"password": "spoc_eshwar", "store_name": "IPLANET @ FORUM FALCON CITY", "city": "Bangalore", "store_state": "Karnataka", "zone": "South"},
    "Prashanth E": {"password": "spoc_prashanth", "store_name": "IPLANET @ FORUM SHANTINIKETAN MALL", "city": "Bangalore", "store_state": "Karnataka", "zone": "South"},
    "Sai Kumar": {"password": "spoc_sai", "store_name": "IPLANET @ INDIRANAGAR", "city": "Bangalore", "store_state": "Karnataka", "zone": "South"},
    "Phillip Raj": {"password": "spoc_phillip", "store_name": "IPLANET @ YELAHANKA NEW TOWN", "city": "Bangalore", "store_state": "Karnataka", "zone": "South"},
    "Abhishek BS": {"password": "spoc_abhishek", "store_name": "IPLANET @ ROYAL MINAKSHI MALL", "city": "Bangalore", "store_state": "Karnataka", "zone": "South"},
    "Chetana": {"password": "spoc_chetana", "store_name": "IPLANET @ NEW BEL ROAD", "city": "Bangalore", "store_state": "Karnataka", "zone": "South"},
    "Nandisha K": {"password": "spoc_nandisha", "store_name": "IPLANET @ HENNUR ROAD", "city": "Bangalore", "store_state": "Karnataka", "zone": "South"},
    "Bharath S": {"password": "spoc_bharath", "store_name": "IPLANET @ BANASHANKARI", "city": "Bangalore", "store_state": "Karnataka", "zone": "South"},
    "Anbhu S": {"password": "spoc_anbhu", "store_name": "IPLANET @ V R MALL", "city": "Bangalore", "store_state": "Karnataka", "zone": "South"},
    "Mahesh Kumar": {"password": "spoc_mahesh", "store_name": "IPLANET @ OMR", "city": "Thoraipakkam", "store_state": "Tamil Nadu", "zone": "South"},
    "Alir Khan": {"password": "spoc_alir", "store_name": "IPLANET @ TAMBARAM", "city": "Chennai", "store_state": "Tamil Nadu", "zone": "South"},
    "Chandra Mouleeswaran": {"password": "spoc_chandra", "store_name": "IPLANET @ PONDY BAZAAR", "city": "Chennai", "store_state": "Tamil Nadu", "zone": "South"},
    "Issac": {"password": "spoc_issac", "store_name": "IPLANET @ VALSARVAKKAM", "city": "Chennai", "store_state": "Tamil Nadu", "zone": "South"},
    "V Dinesh": {"password": "spoc_dinesh", "store_name": "IPLANET @ AVADI", "city": "Chennai", "store_state": "Tamil Nadu", "zone": "South"},
    "Karuppusami": {"password": "spoc_karuppusami", "store_name": "IPLANET @ MUGAPPAIR", "city": "Chennai", "store_state": "Tamil Nadu", "zone": "South"},
    "Mohd Fazil": {"password": "spoc_fazil", "store_name": "IPLANET @ VYTHILLA", "city": "Kochi", "store_state": "Kerela", "zone": "South"},
    "Motilal": {"password": "spoc_motilal", "store_name": "IPLANET @ PROZONE MALL", "city": "Coimbatore", "store_state": "Tamil Nadu", "zone": "South"},
    "R Rahul": {"password": "spoc_rahul", "store_name": "IPLANET @ 100 FEET ROAD", "city": "Gandhipuram", "store_state": "Tamil Nadu", "zone": "South"},
    "Bharat KP": {"password": "spoc_bharat", "store_name": "IPLANET @ TRICHY ROAD", "city": "Coimbatore", "store_state": "Tamil Nadu", "zone": "South"},
    "Farhaan Khan": {"password": "spoc_farhaan", "store_name": "IPLANET @ D.B.ROAD (RS Puram)", "city": "Coimbatore", "store_state": "Tamil Nadu", "zone": "South"},
    "Badhrudheen": {"password": "spoc_badhrudheen", "store_name": "IPLANET @ BROOKEFIELDS MALL", "city": "Coimbatore", "store_state": "Tamil Nadu", "zone": "South"},
    "Muthukumar": {"password": "spoc_muthukumar", "store_name": "IPLANET @ PALANI ROAD", "city": "Dindugal", "store_state": "Tamil Nadu", "zone": "South"},
    "Vishnu V": {"password": "spoc_vishnu", "store_name": "IPLANET @ KOTTAYAM", "city": "Kottayam", "store_state": "Kerela", "zone": "South"},
    "Muralu R": {"password": "spoc_muralu", "store_name": "IPLANET @ ANNA NAGAR", "city": "Madurai", "store_state": "Tamil Nadu", "zone": "South"},
    "Sirajudeen A": {"password": "spoc_sirajudeen", "store_name": "IPLANET @ BYE PASS ROAD", "city": "Madurai", "store_state": "Tamil Nadu", "zone": "South"},
    "Selvakumar": {"password": "spoc_selvakumar", "store_name": "IPLANET @ NORTH VELI STREET", "city": "Madurai", "store_state": "Tamil Nadu", "zone": "South"},
    "Senthil Athiban": {"password": "spoc_senthil", "store_name": "IPLANET @ KP ROAD", "city": "Nagercoil", "store_state": "Tamil Nadu", "zone": "South"},
    "Sudarsan S": {"password": "spoc_sudarsan", "store_name": "IPLANET @ KAJAS ROAD", "city": "Palakkad", "store_state": "Kerela", "zone": "South"},
    "Aravind G": {"password": "spoc_aravind", "store_name": "IPLANET @ PROVEDENCE MALL", "city": "Puducherry", "store_state": "Puducherry", "zone": "South"},
    "Krishnabharathi": {"password": "spoc_krishnabharathi", "store_name": "IPLANET @ SALEM", "city": "Salem", "store_state": "Tamil Nadu", "zone": "South"},
    "Manikandan": {"password": "spoc_manikandan", "store_name": "IPLANET @ PALAYAMKOTTAI ROAD", "city": "Tirunelveli", "store_state": "Tamil Nadu", "zone": "South"},
    "Prakadeeswaran": {"password": "spoc_prakadeeswaran", "store_name": "IPLANET @ AVINASHI ROAD", "city": "Tiruppur", "store_state": "Tamil Nadu", "zone": "South"},
    "Tamil Selvan": {"password": "spoc_tamil", "store_name": "IPLANET @ TANJORE ROAD", "city": "Trichy", "store_state": "Tamil Nadu", "zone": "South"},
    "Sundaramoorthy": {"password": "spoc_sundaramoorthy", "store_name": "IPLANET @ SASTRI ROAD", "city": "Tiruchirappali", "store_state": "Tamil Nadu", "zone": "South"},
    "Abhijeet B": {"password": "spoc_abhijeet", "store_name": "IPLANET @ MALL OF TRAVANCORE", "city": "Thiruvananthapuram", "store_state": "Kerela", "zone": "South"},
    "Rahul Raju": {"password": "spoc_rahulraju", "store_name": "IPLANET @ TRIVANDRUM", "city": "Thiruvananthapuram", "store_state": "Kerela", "zone": "South"},
    "V Raghul": {"password": "spoc_raghul", "store_name": "IPLANET @ VELLORE", "city": "Vellore", "store_state": "Tamil Nadu", "zone": "South"},
    "Jafer Ali": {"password": "spoc_jafer", "store_name": "IPLANET @ INORBIT MALL VAS1", "city": "Vashi", "store_state": "Maharashtra", "zone": "West"},
    "Sagar": {"password": "spoc_sagar", "store_name": "IPLANET @ KEMPS CORNER KEM1", "city": "Kemps", "store_state": "Maharashtra", "zone": "West"},
    "Javed": {"password": "spoc_javed", "store_name": "IPLANET @ VIVIANA VVT1", "city": "Thane", "store_state": "Maharashtra", "zone": "West"},
    "Pritesh": {"password": "spoc_pritesh", "store_name": "IPLANET @ THE WALK WAK1", "city": "Thane", "store_state": "Maharashtra", "zone": "West"},
    "Rohidas": {"password": "spoc_rohidas", "store_name": "IPLANET @ NEUS SEAWOODS MALL SWD1", "city": "Navi Mumbai", "store_state": "Maharashtra", "zone": "West"},
    "Uttam": {"password": "spoc_uttam", "store_name": "IPLANET @ R-CITY MALL, LBS RD RCT1", "city": "Ghatkopar", "store_state": "Maharashtra", "zone": "West"},
    "Amit": {"password": "spoc_amit", "store_name": "IPLANET @ POWAI POW1", "city": "Powai", "store_state": "Maharashtra", "zone": "West"},
    "Amar": {"password": "spoc_amar", "store_name": "IPLANET @ ORION MALL PAN1", "city": "Panvel", "store_state": "Maharashtra", "zone": "West"},
    "Praful": {"password": "spoc_praful", "store_name": "IPLANET @ LINKING ROAD LNK1", "city": "Khar", "store_state": "Maharashtra", "zone": "West"},
    "Shriram": {"password": "spoc_shriram", "store_name": "IPLANET @ RUNWAL GREENS MULUND MUL1", "city": "Mulung", "store_state": "Maharashtra", "zone": "West"}
}

# Streamlit app
st.title("SPOC Order Management System")

# Session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.spoc = None

# Login page
if not st.session_state.logged_in:
    st.subheader("SPOC Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in spoc_database and spoc_database[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.spoc = username
            st.success("Logged in successfully!")
        else:
            st.error("Invalid username or password")
else:
    # Form for logged-in SPOC
    st.subheader(f"Welcome, {st.session_state.spoc}")
    with st.form("order_form"):
        # Form fields
        order_date = st.date_input("Order Date")
        nature_of_business = st.selectbox("Nature of Business", ["Trade-in", "EUP"])
        order_status = "Cancelled"  # Default value
        company = st.selectbox("Company", ["Maple", "EasyOzy"])
        old_device_imei = st.text_input("Old Device IMEI")
        old_device_name = st.text_input("Old Device Name")
        new_device_name = st.text_input("New Device Name")
        initial_old_device_amount = st.number_input("Initial Old Device Amount", min_value=0.0, step=0.01)
        cashify_price = st.number_input("Cashify Price", min_value=0.0, step=0.01)
        maple_given_price = st.number_input("Maple Given Price", min_value=0.0, step=0.01)
        spoc_reason = st.selectbox("Spoc Reason", [
            "Spoc Was on week-off",
            "Spoc was occupied with other customer",
            "Cashify pricing were higher",
            "Device was dead",
            "Customer had cashify reference"
        ])
        device_condition = st.selectbox("Device Condition", ["Best", "Good", "Average", "Poor", "Dead"])
        cashify_spoc = st.selectbox("Cashify Spoc", ["Yes", "No"])
        buy_back_team = st.selectbox("Buy-Back Team Personnel", ["Sanjith", "Sudheer", "Ravi"])

        # Submit button
        submitted = st.form_submit_button("Submit")

        if submitted:
            # Get SPOC details from database
            spoc_details = spoc_database[st.session_state.spoc]
            store_name = spoc_details["store_name"]
            city = spoc_details["city"]
            store_state = spoc_details["store_state"]
            zone = spoc_details["zone"]

            # Prepare data for Google Sheets
            data = {
                "Order Date": str(order_date),
                "Nature of Business": nature_of_business,
                "Order Status": order_status,
                "Company": company,
                "Store Name": store_name,
                "Spocs": st.session_state.spoc,
                "City": city,
                "Store State": store_state,
                "Zone": zone,
                "Old Device IMEI": old_device_imei,
                "Old Device Name": old_device_name,
                "New Device Name": new_device_name,
                "Initial Old Device Amount": initial_old_device_amount,
                "Cashify Price": cashify_price,
                "Maple Given Price": maple_given_price,
                "Spoc Reason": spoc_reason,
                "Device Condition": device_condition,
                "Cashify Spoc": cashify_spoc,
                "Buy-Back Team Personnel": buy_back_team
            }

            # Append data to Google Sheet
            try:
                sheet.append_row(list(data.values()))
                st.success("Data saved successfully to Google Sheets!")
            except Exception as e:
                st.error(f"Error saving data: {str(e)}")

    # Logout button
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.spoc = None
        st.success("Logged out successfully!")