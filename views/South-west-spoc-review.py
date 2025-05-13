import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

st.title("Maple Digital Technology International - Trade-In Dashboard for SPOC review")

# File Upload
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.session_state['data'] = df
        st.success("File uploaded successfully!")
    except Exception as e:
        st.error(f"Error reading file: {e}")

if 'data' in st.session_state:
    df = st.session_state['data'].copy()

    # Convert Date and Extract Components
    df['Created Date'] = pd.to_datetime(df['Created Date'], errors='coerce')
    df['Month'] = df['Created Date'].dt.month_name()
    df['Year'] = df['Created Date'].dt.year

    # Filters
    st.sidebar.header("🔍 Filter Data")
    selected_year = st.sidebar.selectbox("Select Year", sorted(df['Year'].dropna().unique()), index=0)
    filtered_df = df[df['Year'] == selected_year]
    
    selected_month = st.sidebar.selectbox("Select Month", ["All"] + sorted(filtered_df['Month'].dropna().unique()), index=0)
    if selected_month != "All":
        filtered_df = filtered_df[filtered_df['Month'] == selected_month]

    # KPI Section
    st.subheader("📊 Key Performance Indicators (KPIs)")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Years in Data", len(df['Year'].unique()))
    
    with col2:
        maple_bid_total = filtered_df['Maple Device Value'].count()
        st.metric("Count of Maple Bid till 9th May,2025", f"{maple_bid_total:,.2f}")
    
    with col3:
        cashify_bid_total = filtered_df['Cashify Bid'].count()
        st.metric("Count of Cashify Bid till 9th May,2025", f"{cashify_bid_total:,.2f}")
    
    # Store Performance Improvement
    st.subheader("(1) Store Performance Improvement")
    
    selected_region = st.selectbox("Select Region for Store Performance", df['State Region'].dropna().unique())
    state_options = df[df['State Region'] == selected_region]['Store State'].dropna().unique()
    selected_state = st.selectbox("Select State", state_options)
    
    spoc_options = df[(df['State Region'] == selected_region) & (df['Store State'] == selected_state)]['Spoc Name'].dropna().unique()
    selected_spoc = st.selectbox("Select SPOC", spoc_options)
    
    spoc_filtered_df = df[(df['State Region'] == selected_region) &
                           (df['Store State'] == selected_state) &
                           (df['Spoc Name'] == selected_spoc)]
    
    # SPOC Store Performance Bar Chart
    spoc_filtered_df['YearMonth'] = spoc_filtered_df['Created Date'].dt.to_period('M').astype(str)
    spoc_store_performance = spoc_filtered_df.groupby(['YearMonth', 'Store Name']).size().reset_index(name='Trade-In Count')
    fig_spoc_performance = px.bar(spoc_store_performance, x='YearMonth', y='Trade-In Count', color='Store Name', 
                                  title=f"Store Performance for {selected_spoc}")
    st.plotly_chart(fig_spoc_performance)
    
    # Trade-In Analysis by Region, Store, and SPOC
    st.subheader("(2) Trade-In Analysis by Region, State, Store, and SPOC")
    selected_region = st.selectbox("Select Region", filtered_df['State Region'].dropna().unique())
    region_filtered_df = filtered_df[filtered_df['State Region'] == selected_region]
    selected_state = st.selectbox("Selecte State", filtered_df['Store State'].dropna().unique())
    state_filtered_df = filtered_df[filtered_df['Store State'] == selected_state]
    selected_store = st.selectbox("Select Store", region_filtered_df['Store Name'].dropna().unique())
    store_filtered_df = region_filtered_df[region_filtered_df['Store Name'] == selected_store]
    selected_spoc = st.selectbox("Select SPOC", store_filtered_df['Spoc Name'].dropna().unique())
    spoc_filtered_df = store_filtered_df[store_filtered_df['Spoc Name'] == selected_spoc]
    st.write(f"Total Trade-Ins for {selected_spoc}: {spoc_filtered_df.shape[0]}")
    
    # Price Comparison
    st.subheader("(3) Price Range Comparison")
    filtered_df['Price Difference'] = filtered_df['Maple Bid'] - filtered_df['Cashify Bid']
    fig_price_comparison = px.bar(filtered_df, x='New Product Name', y='Price Difference', title="Price Difference between Maple and Cashify Bids")
    st.plotly_chart(fig_price_comparison)
    
    # Difference Analysis
    st.subheader("(4) Difference Analysis")
    filtered_df = filtered_df[filtered_df['Cashify Bid with coupon'] > 0]
    filtered_df['% Difference'] = ((filtered_df['Price Difference'] / filtered_df['Cashify Bid with coupon']) * 100).round(2)
    fig_difference = px.histogram(filtered_df, x='% Difference', title="% Difference Analysis (Maple vs Cashify)")
    st.plotly_chart(fig_difference)
    
    # Year and Month Wise Growth
    st.subheader("(5) Year and Month Wise Growth")
    year_month_growth = filtered_df.groupby(['Year', 'Month', 'State Region']).size().reset_index(name='Trade-In Count')
    year_month_growth['Year-Month'] = year_month_growth['Year'].astype(str) + " " + year_month_growth['Month']
    fig_growth = px.bar(year_month_growth, x='Year-Month', y='Trade-In Count', color='State Region', title="Year and Month Wise Growth")
    st.plotly_chart(fig_growth)
    
    # Downloadable Report
    st.subheader("(6) Downloadable Report - Top & Bottom 10 Stores")
    top_10 = filtered_df.groupby(['Store State', 'Store Name', 'Spoc Name']).size().reset_index(name='Trade-In Count').nlargest(10, 'Trade-In Count')
    bottom_10 = filtered_df.groupby(['Store State', 'Store Name', 'Spoc Name']).size().reset_index(name='Trade-In Count').nsmallest(10, 'Trade-In Count')
    
    def download_excel(df, filename="filtered_data.xlsx"):
        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        st.download_button("Download Excel", data=buffer, file_name=filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    st.write("### Top 10 Performing Stores")
    st.dataframe(top_10)
    download_excel(top_10, "top_10_stores.xlsx")
    
    st.write("### Bottom 10 Performing Stores")
    st.dataframe(bottom_10)
    download_excel(bottom_10, "bottom_10_stores.xlsx")
