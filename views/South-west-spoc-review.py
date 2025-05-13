import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import plotly.graph_objects as go

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
    if 'Created Date' in df.columns:
        df['Created Date'] = pd.to_datetime(df['Created Date'], errors='coerce')
        df['Month'] = df['Created Date'].dt.month_name()
        df['Year'] = df['Created Date'].dt.year
    else:
        st.error("'Created Date' column not found in uploaded file.")
        st.stop()

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
        if 'Maple Bid' in filtered_df.columns:
            maple_bid_total = filtered_df['Maple Bid'].count()
            st.metric("Count of Maple Bid till 9th May,2025", f"{maple_bid_total:,.2f}")
        else:
            st.warning("'Maple Bid' column is missing.")

    with col3:
        if 'Cashify Bid' in filtered_df.columns:
            cashify_bid_total = filtered_df['Cashify Bid'].count()
            st.metric("Count of Cashify Bid till 9th May,2025", f"{cashify_bid_total:,.2f}")
        else:
            st.warning("'Cashify Bid' column is missing.")

    required_columns = ['State Region', 'Store State', 'Spoc Name', 'Store Name']
    if not all(col in df.columns for col in required_columns):
        st.error("Essential columns for analysis are missing. Required: " + ", ".join(required_columns))
        st.stop()

    st.subheader("(1) Store Performance Improvement")
    selected_region = st.selectbox("Select Region for Store Performance", df['State Region'].dropna().unique())
    state_options = df[df['State Region'] == selected_region]['Store State'].dropna().unique()
    selected_state = st.selectbox("Select State", state_options)

    spoc_options = df[(df['State Region'] == selected_region) & (df['Store State'] == selected_state)]['Spoc Name'].dropna().unique()
    selected_spoc = st.selectbox("Select SPOC", spoc_options)

    spoc_filtered_df = df[(df['State Region'] == selected_region) &
                          (df['Store State'] == selected_state) &
                          (df['Spoc Name'] == selected_spoc)]

    spoc_filtered_df['YearMonth'] = spoc_filtered_df['Created Date'].dt.to_period('M').astype(str)
    spoc_store_performance = spoc_filtered_df.groupby(['YearMonth', 'Store Name']).size().reset_index(name='Trade-In Count')
    fig_spoc_performance = px.bar(spoc_store_performance, x='YearMonth', y='Trade-In Count', color='Store Name',
                                  title=f"Store Performance for {selected_spoc}")
    # Add text annotations for trade-in count on top of bars
    for i, row in spoc_store_performance.iterrows():
        fig_spoc_performance.add_annotation(
            x=row['YearMonth'],
            y=row['Trade-In Count'],
            text=str(row['Trade-In Count']),
            showarrow=False,
            yshift=10,
            font=dict(size=10)
        )
    st.plotly_chart(fig_spoc_performance)

    st.subheader("(2) Trade-In Analysis by Region, State, Store, and SPOC")
    selected_region = st.selectbox("Select Region", filtered_df['State Region'].dropna().unique())
    region_filtered_df = filtered_df[filtered_df['State Region'] == selected_region]
    selected_state = st.selectbox("Select State", filtered_df['Store State'].dropna().unique())
    state_filtered_df = filtered_df[filtered_df['Store State'] == selected_state]
    selected_store = st.selectbox("Select Store", region_filtered_df['Store Name'].dropna().unique())
    store_filtered_df = region_filtered_df[region_filtered_df['Store Name'] == selected_store]
    selected_spoc = st.selectbox("Select SPOC", store_filtered_df['Spoc Name'].dropna().unique())
    spoc_filtered_df = store_filtered_df[store_filtered_df['Spoc Name'] == selected_spoc]
    st.write(f"Total Trade-Ins for {selected_spoc}: {spoc_filtered_df.shape[0]}")

    st.subheader("(3) Price Range Comparison")
    required_bid_columns = ['Maple Bid', 'Cashify Bid', 'Product Category', 'Product Type Old', 'New Product Name']
    missing_columns = [col for col in required_bid_columns if col not in filtered_df.columns]
    
    if missing_columns:
        st.error(f"Missing the following required columns for bid comparison: {', '.join(missing_columns)}")
        st.warning("Please check the uploaded Excel file and ensure the column names match exactly: " + ", ".join(required_bid_columns))
        st.write("Available columns in your file: " + ", ".join(filtered_df.columns))
    else:
        filtered_df['Price Difference'] = filtered_df['Maple Bid'] - filtered_df['Cashify Bid']

        # Dropdowns for filtering
        selected_category = st.selectbox("Select Product Category", filtered_df['Product Category'].dropna().unique())
        filtered_df = filtered_df[filtered_df['Product Category'] == selected_category]

        selected_type = st.selectbox("Select Product Type Old", filtered_df['Product Type'].dropna().unique())
        filtered_df = filtered_df[filtered_df['Product Type Old'] == selected_type]

        selected_product = st.selectbox("Select Product Name", filtered_df['New Product Name'].dropna().unique())
        filtered_df = filtered_df[filtered_df['New Product Name'] == selected_product]

        # Prepare YearMonth
        filtered_df['YearMonth'] = filtered_df['Created Date'].dt.to_period('M').astype(str)

        # Aggregated Bids by Month
        monthly_bids = filtered_df.groupby('YearMonth').agg({
            'Maple Bid': ['mean', 'count'],
            'Cashify Bid': ['mean', 'count'],
            'Price Difference': ['mean', 'count']
        }).reset_index()
        monthly_bids.columns = ['YearMonth', 'Maple Bid Mean', 'Maple Bid Count', 'Cashify Bid Mean', 'Cashify Bid Count', 'Price Difference Mean', 'Price Difference Count']

        # Melt for multi-bar plotting
        plot_df = monthly_bids.melt(id_vars='YearMonth', 
                                    value_vars=['Maple Bid Mean', 'Cashify Bid Mean', 'Price Difference Mean'],
                                    var_name='Bid Type', value_name='Amount')

        # Map Bid Type for legend
        plot_df['Bid Type'] = plot_df['Bid Type'].replace({
            'Maple Bid Mean': 'Maple Bid',
            'Cashify Bid Mean': 'Cashify Bid',
            'Price Difference Mean': 'Price Difference'
        })

        color_map = {
            'Maple Bid': '#4C9AFF',  # Sea Blue
            'Cashify Bid': '#003F88',  # Navy Blue
            'Price Difference': '#00A86B'  # Jade Blue
        }

        fig = px.bar(plot_df, x='YearMonth', y='Amount', color='Bid Type',
                     title=f"Monthly Bid Comparison for {selected_product}: Maple vs Cashify",
                     color_discrete_map=color_map, barmode='group')

        # Add annotations for count and average bid
        for _, row in monthly_bids.iterrows():
            year_month = row['YearMonth']
            for bid_type, color in [('Maple Bid', '#4C9AFF'), ('Cashify Bid', '#003F88'), ('Price Difference', '#00A86B')]:
                bid_key = bid_type.replace(' ', ' ') + ' Mean'
                count_key = bid_type.replace(' ', ' ') + ' Count'
                if bid_key in monthly_bids.columns:
                    amount = row[bid_key]
                    count = row[count_key]
                    if pd.notnull(amount):
                        fig.add_annotation(
                            x=year_month,
                            y=amount,
                            text=f"Count: {int(count)}<br>Avg: {amount:.2f}",
                            showarrow=False,
                            yshift=10,
                            font=dict(size=10, color=color),
                            xanchor='center',
                            align='center'
                        )

        st.plotly_chart(fig)

    st.subheader("(4) Year and Month Wise Growth")
    year_month_growth = filtered_df.groupby(['Year', 'Month', 'State Region']).size().reset_index(name='Trade-In Count')
    year_month_growth['Year-Month'] = year_month_growth['Year'].astype(str) + " " + year_month_growth['Month']
    fig_growth = px.bar(year_month_growth, x='Year-Month', y='Trade-In Count', color='State Region', title="Year and Month Wise Growth")
    st.plotly_chart(fig_growth)

    st.subheader("(5) Downloadable Report - Top & Bottom 10 Stores")
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
