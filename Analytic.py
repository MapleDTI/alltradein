import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import uuid
import io

# Set page config
st.set_page_config(page_title="Maple vs Cashify Analytics", layout="wide")

# Initialize session state for data and authentication
if 'maple_data' not in st.session_state:
    st.session_state.maple_data = None
if 'cashify_data' not in st.session_state:
    st.session_state.cashify_data = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None

# User credentials
users = {
    "mahesh_shetty": {"password": "Maple2025!", "name": "Mahesh Shetty"},
    "sandesh_kadam": {"password": "TradeIn@2025", "name": "Sandesh Kadam"},
    "vishwa_sanghavi": {"password": "Analytics#2025", "name": "Vishwa Sanghavi"},
    "kavish_shah": {"password": "Cashify2025$", "name": "Kavish Shah"}
}

# Backend SPOC Targets for May 2025
spoc_targets = {
    "Senthil Athiban": 28, "Motilal": 30, "R Rahul": 28, "V Dinesh": 27, "Rahul Raju": 28,
    "Mahesh Kumar": 30, "Nandish": 28, "Vishnu": 25, "Issac": 30, "Mudasir": 25,
    "Selva kumar": 28, "Muthukumar": 27, "V.RAGHUL": 27, "Mohd Riyas": 28, "Gopi J": 34,
    "Anbhu S": 28, "Philip Raj": 28, "Bala Murugan": 29, "Vacant": 27, "Manikandan": 31,
    "Tamil Selvan": 28, "Alir Khan": 37, "Resigned(Vacant)": 30, "Suntareshwar": 30,
    "Aravind G": 37, "Sudarsan S": 33, "Sachin Rathor": 34, "MOHAMMED FAZIL": 34,
    "Prakadeeswaran": 37, "Abhijit B": 33, "Krishnabharathi": 43, "Sanni Vishwakarma": 40,
    "Sirajudeen A": 41, "Karuppusami": 42, "Bharat KP": 43, "Mohd Waseem": 44,
    "Murali R": 45, "Prashanth E": 54, "Bharath S": 63, "Abhishek B S": 68,
    "Farhaan Khan": 73, "Badhrudheen": 76, "Eshwar": 87, "Chandra Mouleeswaran": 80,
    "Sundaramoorthy": 73, "Sai Kumar": 108, "Manjunath": 101, "Javed Shaikh": 160,
    "Amit Desai": 110, "Rohidas": 160, "Praful": 175, "Uttam Singh": 125,
    "Pritesh Vele": 125, "Ramsagar": 63, "Amar": 70, "Jafer Shaikh": 120, "Shriram": 55,
    "Rohan": 60
}

# Backend SPOC Weekoffs (converted to specific dates in May 2025)
weekoff_days = {
    "Senthil Athiban": "Thursday", "Motilal": "Thursday", "R Rahul": "Tuesday",
    "V Dinesh": "Wednesday", "Rahul Raju": "Tuesday", "Mahesh Kumar": "Tuesday",
    "Nandish": "Tuesday", "Vishnu": "Tuesday", "Issac": "Tuesday", "Mudasir": "Tuesday",
    "Selva kumar": "Monday", "Muthukumar": "Wednesday", "V.RAGHUL": "Thursday",
    "Mohd Riyas": "Monday", "Gopi J": "Monday", "Anbhu S": "Thursday",
    "Philip Raj": "Thursday", "Bala Murugan": "Wednesday", "Vacant": "Vacant",
    "Manikandan": "Monday", "Tamil Selvan": "Monday", "Alir Khan": "Wednesday",
    "Resigned(Vacant)": "Vacant", "Suntareshwar": "Vacant", "Aravind G": "Tuesday",
    "Sudarsan S": "Monday", "Sachin Rathor": "Wednesday", "MOHAMMED FAZIL": "Thursday",
    "Prakadeeswaran": "Thursday", "Abhijit B": "Wednesday", "Krishnabharathi": "Wednesday",
    "Sanni Vishwakarma": "Wednesday", "Sirajudeen A": "Monday", "Karuppusami": "Thursday",
    "Bharat KP": "Monday", "Mohd Waseem": "Tuesday", "Murali R": "Wednesday",
    "Prashanth E": "Thursday", "Bharath S": "Thursday", "Abhishek B S": "Tuesday",
    "Farhaan Khan": "Wednesday", "Badhrudheen": "Tuesday", "Eshwar": "Wednesday",
    "Chandra Mouleeswaran": "Monday", "Sundaramoorthy": "Tuesday", "Sai Kumar": "Tuesday",
    "Manjunath": "Wednesday"
}

# Convert weekoff days to specific dates in May 2025
may_2025_weekoffs = {
    "Monday": [date(2025, 5, 5), date(2025, 5, 12), date(2025, 5, 19), date(2025, 5, 26)],
    "Tuesday": [date(2025, 5, 6), date(2025, 5, 13), date(2025, 5, 20), date(2025, 5, 27)],
    "Wednesday": [date(2025, 5, 7), date(2025, 5, 14), date(2025, 5, 21), date(2025, 5, 28)],
    "Thursday": [date(2025, 5, 1), date(2025, 5, 8), date(2025, 5, 15), date(2025, 5, 22), date(2025, 5, 29)],
    "Vacant": []
}
spoc_weekoffs = {spoc: may_2025_weekoffs.get(day, []) for spoc, day in weekoff_days.items()}

# Required columns for validation
MAPLE_REQUIRED_COLUMNS = ['Created Date', 'Month', 'Year', 'Store Name', 'Spoc Name', 'State Region', 'Store State', 'Maple Bid', 'Old IMEI No']
CASHIFY_REQUIRED_COLUMNS = ['Order Date', 'Month', 'Year', 'Store Name', 'Spoc Name', 'Store State', 'Initial Device Amount', 'Old Device IMEI']

# Function to validate DataFrame columns
def validate_columns(df, required_columns, df_name):
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"Missing columns in {df_name} data: {', '.join(missing_columns)}")
        return False
    return True

# Function to standardize month format
def standardize_month(df, month_col='Month'):
    month_mapping = {
        1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
        7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December",
        "jan": "January", "feb": "February", "mar": "March", "apr": "April", "may": "May", "jun": "June",
        "jul": "July", "aug": "August", "sep": "September", "oct": "October", "nov": "November", "dec": "December"
    }
    def parse_month(x):
        if pd.isna(x):
            return x
        x_str = str(x).strip().lower()
        # Try converting to int if it's a number
        try:
            month_num = int(float(x_str))
            return month_mapping.get(month_num, x_str.title())
        except (ValueError, TypeError):
            # If not a number, look for month name or abbreviation
            return month_mapping.get(x_str, x_str.title())
    
    df[month_col] = df[month_col].apply(parse_month)
    return df

# Function to standardize state names
def standardize_states(df, state_col='Store State'):
    df[state_col] = df[state_col].apply(lambda x: str(x).title() if pd.notna(x) else x)
    return df

# Function to process date filters
def filter_by_date(df, year, month, day=None, is_maple=True):
    date_column = 'Created Date' if is_maple else 'Order Date'
    if date_column not in df.columns:
        st.error(f"Column '{date_column}' not found in {'Maple' if is_maple else 'Cashify'} data.")
        return pd.DataFrame()
    try:
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce', dayfirst=True)
        df = df[df['Year'] == year]
        if month and month != "All":
            df = df[df['Month'] == month]
        if day and day != "All":
            df = df[df[date_column].dt.day == day]
        return df
    except Exception as e:
        st.error(f"Error processing dates in {'Maple' if is_maple else 'Cashify'} data: {str(e)}")
        return pd.DataFrame()

# Function to calculate market share
def calculate_market_share(maple_count, cashify_count):
    total = maple_count + cashify_count
    return (maple_count / total * 100) if total > 0 else 0

# Login function
def login():
    st.sidebar.header("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login"):
        if username in users and users[username]["password"] == password:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.sidebar.success(f"Welcome, {users[username]['name']}!")
        else:
            st.sidebar.error("Invalid username or password")

# Logout function
def logout():
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.sidebar.success("Logged out successfully")

# Main app
if not st.session_state.authenticated:
    login()
else:
    st.sidebar.write(f"Logged in as: {users[st.session_state.username]['name']}")
    logout()

    # Sidebar for file upload only
    st.sidebar.header("Data Upload")
    maple_file = st.sidebar.file_uploader("Upload Maple Data (Excel)", type=["xlsx"])
    cashify_file = st.sidebar.file_uploader("Upload Cashify Data (Excel)", type=["xlsx"])

    # Load data if uploaded
    if maple_file:
        st.session_state.maple_data = pd.read_excel(maple_file)
    if cashify_file:
        st.session_state.cashify_data = pd.read_excel(cashify_file)

    # Main content
    st.title("Maple vs Cashify Analytics Dashboard")

    # Validate and process data
    if st.session_state.maple_data is not None and st.session_state.cashify_data is not None:
        if not (validate_columns(st.session_state.maple_data, MAPLE_REQUIRED_COLUMNS, "Maple") and
                validate_columns(st.session_state.cashify_data, CASHIFY_REQUIRED_COLUMNS, "Cashify")):
            st.stop()

        # Standardize month and state formats in both datasets
        maple_df = standardize_month(st.session_state.maple_data.copy())
        maple_df = standardize_states(maple_df)
        cashify_df = standardize_month(st.session_state.cashify_data.copy())
        cashify_df = standardize_states(cashify_df)

        # Validate and convert Year column to numeric
        for df, name in [(maple_df, "Maple"), (cashify_df, "Cashify")]:
            try:
                df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
                if df['Year'].isna().any():
                    st.warning(f"Some entries in the 'Year' column of {name} data could not be converted to numbers and will be ignored.")
            except Exception as e:
                st.error(f"Error converting 'Year' column in {name} data to numeric: {str(e)}")
                st.stop()

        # Filters at the top of the dashboard
        st.header("Filters")
        col1, col2, col3 = st.columns(3)

        with col1:
            years = sorted(set(maple_df['Year'].dropna()) & set(cashify_df['Year'].dropna()))
            years = [int(year) for year in years]  # Ensure years are integers
            selected_year = st.selectbox("Select Year", years if years else [2025], key="year_filter")

        with col2:
            # Get common months between Maple and Cashify, ensuring no duplicates
            maple_months = set(maple_df['Month'].dropna())
            cashify_months = set(cashify_df['Month'].dropna())
            common_months = sorted(maple_months & cashify_months)
            selected_month = st.selectbox("Select Month", ["All"] + common_months, key="month_filter")

        with col3:
            if selected_month != "All":
                days = []
                if not maple_df.empty:
                    days.extend(maple_df[maple_df['Month'] == selected_month]['Created Date'].dt.day.dropna())
                if not cashify_df.empty:
                    days.extend(cashify_df[cashify_df['Month'] == selected_month]['Order Date'].dt.day.dropna())
                days = sorted(set(days))
                selected_day = st.selectbox("Select Day", ["All"] + list(map(int, days)), key="day_filter")
            else:
                selected_day = "All"

        # Apply date filters to both datasets
        maple_filtered = filter_by_date(maple_df, selected_year, selected_month, selected_day, is_maple=True)
        cashify_filtered = filter_by_date(cashify_df, selected_year, selected_month, selected_day, is_maple=False)

        if maple_filtered.empty or cashify_filtered.empty:
            st.warning("No data available after applying filters. Please check your data or adjust the filters.")
            st.stop()

        # Standardize Store Name and Spoc Name to avoid mismatches
        for df in [maple_filtered, cashify_filtered]:
            df['Store Name'] = df['Store Name'].str.strip().str.title()
            df['Spoc Name'] = df['Spoc Name'].str.strip().str.title()

        # 1. Daily, Weekly, Monthly Average Devices Acquired
        st.header("1. Average Devices Acquired")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Maple")
            maple_daily = maple_filtered.groupby(maple_filtered['Created Date'].dt.date).size().mean() if not maple_filtered.empty else 0
            maple_weekly = maple_filtered.groupby(maple_filtered['Created Date'].dt.isocalendar().week).size().mean() if not maple_filtered.empty else 0
            maple_monthly = maple_filtered.groupby('Month').size().mean() if not maple_filtered.empty else 0
            st.write(f"Daily Avg: {maple_daily:.2f}")
            st.write(f"Weekly Avg: {maple_weekly:.2f}")
            st.write(f"Monthly Avg: {maple_monthly:.2f}")
        
        with col2:
            st.subheader("Cashify")
            cashify_daily = cashify_filtered.groupby(cashify_filtered['Order Date'].dt.date).size().mean() if not cashify_filtered.empty else 0
            cashify_weekly = cashify_filtered.groupby(cashify_filtered['Order Date'].dt.isocalendar().week).size().mean() if not cashify_filtered.empty else 0
            cashify_monthly = cashify_filtered.groupby('Month').size().mean() if not cashify_filtered.empty else 0
            st.write(f"Daily Avg: {cashify_daily:.2f}")
            st.write(f"Weekly Avg: {cashify_weekly:.2f}")
            st.write(f"Monthly Avg: {cashify_monthly:.2f}")

        # 2. Market Share Analysis
        st.header("2. Market Share Analysis")
        regions = sorted(set(maple_filtered['State Region'].dropna()))
        if not regions:
            st.warning("No regions available in the filtered data.")
            st.stop()
        region = st.selectbox("Select Region", regions)
        store_states = sorted(set(maple_filtered[maple_filtered['State Region'] == region]['Store State'].dropna()))
        if not store_states:
            st.warning("No store states available for the selected region.")
            st.stop()
        store_state = st.selectbox("Select Store State", store_states)
        store_names = sorted(set(maple_filtered[maple_filtered['Store State'] == store_state]['Store Name'].dropna()))
        if not store_names:
            st.warning("No store names available for the selected store state.")
            st.stop()
        store_name = st.selectbox("Select Store Name", store_names)
        spocs = sorted(set(maple_filtered[maple_filtered['Store Name'] == store_name]['Spoc Name'].dropna()))
        if not spocs:
            st.warning("No SPOCs available for the selected store.")
            st.stop()
        spoc = st.selectbox("Select SPOC", spocs)

        maple_spoc_count = len(maple_filtered[(maple_filtered['Store Name'] == store_name) & (maple_filtered['Spoc Name'] == spoc)])
        cashify_spoc_count = len(cashify_filtered[(cashify_filtered['Store Name'] == store_name) & (cashify_filtered['Spoc Name'] == spoc)])
        market_share = calculate_market_share(maple_spoc_count, cashify_spoc_count)
        
        target = spoc_targets.get(spoc, 0)
        achievement = maple_spoc_count
        shortfall = target - achievement
        devices_lost = cashify_spoc_count
        maple_avg_bid = maple_filtered[(maple_filtered['Store Name'] == store_name) & (maple_filtered['Spoc Name'] == spoc)]['Maple Bid'].mean()
        cashify_avg_bid = cashify_filtered[(cashify_filtered['Store Name'] == store_name) & (cashify_filtered['Spoc Name'] == spoc)]['Initial Device Amount'].mean()
        price_diff = maple_avg_bid - cashify_avg_bid if pd.notna(maple_avg_bid) and pd.notna(cashify_avg_bid) else 0
        
        st.write(f"Market Share: {market_share:.2f}%")
        st.write(f"SPOC Target: {target}")
        st.write(f"SPOC Achievement: {achievement}")
        st.write(f"SPOC Shortfall: {shortfall}")
        st.write(f"Devices Lost to Cashify: {devices_lost}")
        st.write(f"Average Price Difference (Maple - Cashify): {price_diff:.2f}")
        if price_diff > 0:
            st.warning("Maple offered higher prices but still lost devices.")

        # 2.1 Stores with Market Share Below 50% in the Selected State
        st.subheader("Stores with Market Share Below 50% in Selected State")
        stores_in_state = maple_filtered[maple_filtered['Store State'] == store_state]['Store Name'].unique()
        low_market_share_data = []
        
        for store in stores_in_state:
            store_spocs = maple_filtered[maple_filtered['Store Name'] == store]['Spoc Name'].unique()
            for store_spoc in store_spocs:
                maple_count = len(maple_filtered[(maple_filtered['Store Name'] == store) & (maple_filtered['Spoc Name'] == store_spoc)])
                cashify_count = len(cashify_filtered[(cashify_filtered['Store Name'] == store) & (cashify_filtered['Spoc Name'] == store_spoc)])
                ms = calculate_market_share(maple_count, cashify_count)
                if ms < 50:
                    low_market_share_data.append({
                        'Store Name': store,
                        'Spoc Name': store_spoc,
                        'Maple Devices': maple_count,
                        'Market Share (%)': ms
                    })
        
        if low_market_share_data:
            low_ms_df = pd.DataFrame(low_market_share_data)
            st.write("**Stores with Market Share Below 50%:**")
            st.dataframe(low_ms_df)

            # Bar chart visualization
            fig = px.bar(
                low_ms_df,
                x='Market Share (%)',
                y='Store Name',
                color='Spoc Name',
                text='Maple Devices',
                title=f"Stores in {store_state} with Market Share Below 50%",
                orientation='h'
            )
            fig.update_traces(textposition='inside')
            st.plotly_chart(fig)

            # Excel download
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                low_ms_df.to_excel(writer, index=False, sheet_name='Low Market Share Stores')
            st.download_button(
                label="Download Low Market Share Stores as Excel",
                data=buffer.getvalue(),
                file_name="low_market_share_stores.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.write(f"No stores in {store_state} have a market share below 50%.")

        # 3. SPOC Performance for Selected Month
        st.header("3. SPOC Performance in Selected Month")
        if selected_month != "All":
            spoc_devices = len(maple_filtered[maple_filtered['Spoc Name'] == spoc])
            st.write(f"**{spoc}'s Performance in {selected_month} {selected_year}**")
            st.write(f"Devices Acquired: {spoc_devices}")
        else:
            st.write("Please select a specific month to view SPOC performance.")

        # 4. Category-wise Contribution
        st.header("4. Category-wise Contribution")
        maple_cat = maple_filtered[maple_filtered['Spoc Name'] == spoc].groupby('Product Category').size()
        cashify_cat = cashify_filtered[cashify_filtered['Spoc Name'] == spoc].groupby('Product Category').size()
        total = maple_cat.sum() + cashify_cat.sum()
        if total > 0:
            maple_cat = (maple_cat / total * 100).reset_index(name='Maple %')
            cashify_cat = (cashify_cat / total * 100).reset_index(name='Cashify %')
            cat_df = pd.merge(maple_cat, cashify_cat, on='Product Category', how='outer').fillna(0)
            fig = go.Figure(data=[
                go.Bar(name='Maple', x=cat_df['Product Category'], y=cat_df['Maple %']),
                go.Bar(name='Cashify', x=cat_df['Product Category'], y=cat_df['Cashify %'])
            ])
            fig.update_layout(barmode='group', title="Category-wise Contribution")
            st.plotly_chart(fig)
        else:
            st.write("No category data available for this SPOC.")

        # 5. Devices Lost on SPOC Weekoff Days at the SPOC's Store
        st.header("5. Devices Lost on SPOC Weekoff Days at Their Store")
        weekoff_dates = spoc_weekoffs.get(spoc, [])
        # Get the store(s) where the SPOC works
        spoc_stores = maple_filtered[maple_filtered['Spoc Name'] == spoc]['Store Name'].unique()
        if len(spoc_stores) == 0:
            st.write(f"No stores found for {spoc} in the filtered data.")
        else:
            store = spoc_stores[0]  # Assuming SPOC is tied to one store in the filtered data
            weekoff_losses = cashify_filtered[
                (cashify_filtered['Store Name'] == store) &
                (cashify_filtered['Order Date'].dt.date.isin(weekoff_dates))
            ]
            weekoff_count = len(weekoff_losses)
            st.write(f"Devices Traded in Cashify at {store} on {spoc}'s Weekoff Days: {weekoff_count}")
            if weekoff_count > 0:
                weekoff_by_cat = weekoff_losses.groupby('Product Category').size().reset_index(name='Count')
                fig = px.pie(weekoff_by_cat, names='Product Category', values='Count', title="Weekoff Day Losses by Category")
                st.plotly_chart(fig)

        # 6. Working Day Losses
        st.header("6. Working Day Losses")
        working_losses = cashify_filtered[(cashify_filtered['Spoc Name'] == spoc) & 
                                         (~cashify_filtered['Order Date'].dt.date.isin(weekoff_dates))]
        total_working = len(maple_filtered[maple_filtered['Spoc Name'] == spoc]) + len(working_losses)
        loss_percent = (len(working_losses) / total_working * 100) if total_working > 0 else 0
        st.write(f"Total Devices Lost: {len(working_losses)} ({loss_percent:.2f}%)")
        
        loss_by_state = working_losses.groupby('Store State').size().reset_index(name='Count')
        if not loss_by_state.empty:
            fig = px.bar(loss_by_state, x='Store State', y='Count', title="Working Day Losses by State")
            st.plotly_chart(fig)
        else:
            st.write("No working day losses to display.")

    else:
        st.warning("Please upload both Maple and Cashify Excel files to proceed.")
