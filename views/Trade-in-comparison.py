import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from datetime import datetime
import base64
from fpdf import FPDF

# Set page config
st.set_page_config(page_title="Trade-in Analysis", layout="wide")

st.title("📊 Trade-in Price Analysis Dashboard")

# File Uploader
uploaded_file = st.file_uploader("Upload Trade-in Excel File", type=["xlsx", "xls"])

# Helper: Convert DataFrame to Excel
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Report')
    return output.getvalue()

# Helper: Convert DataFrame to PDF
def to_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=8)
    col_width = pdf.w / 5
    row_height = 6

    for i, row in df.iterrows():
        for item in row[:5]:  # Limit columns to fit on PDF
            pdf.cell(col_width, row_height, txt=str(item), border=1)
        pdf.ln(row_height)

    return pdf.output(dest='S').encode('latin1')

# Main logic
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Standardizing column names (strip spaces)
    df.columns = df.columns.str.strip()

    st.subheader("📁 Raw Data Preview")
    st.dataframe(df.head(50), use_container_width=True)

    # MODEL-WISE PRICE ANALYSIS
    st.subheader("📈 Model-wise Price Analysis of Lost Devices")
    lost_devices_df = df[df['Partner Name'].str.lower().str.contains("cashify", na=False)]
    model_loss = lost_devices_df.groupby('Old Device Name')['Total Device Value Paid'].sum().reset_index()
    fig1 = px.bar(model_loss, x='Old Device Name', y='Total Device Value Paid', title="Lost Device Value by Model")
    st.plotly_chart(fig1, use_container_width=True)

    # TRADE-IN COMPARISON
    st.subheader("🔍 Trade-in Price Comparison on SPOC Working Days")
    spoc_days_df = df[df['Spoc Name'].notna()]
    price_comparison = spoc_days_df.groupby(['Old Device Name', 'Store Name']).agg({
        'Total Device Value Paid': 'mean',
        'Partner Contribution': 'sum'
    }).reset_index()
    st.dataframe(price_comparison, use_container_width=True)

    # STORE SUPPORT ISSUES
    st.subheader("⚠️ Store Support Issues Reported by SPOCs")
    issues_df = df[df['Order Status'].str.lower().str.contains('fail|issue|not', na=False)]
    st.dataframe(issues_df[['Store Name', 'Spoc Name', 'Order Status', 'Old Device Name']], use_container_width=True)

    # CONSOLIDATED ANALYSIS REPORT
    st.subheader("🗃️ Consolidated Trade-in Analysis Report")
    month_comparison = df.groupby(['Month', 'Old Device Name'])['Total Device Value Paid'].sum().reset_index()
    fig2 = px.line(month_comparison, x='Month', y='Total Device Value Paid', color='Old Device Name', title="Month-wise Trade-in Value")
    st.plotly_chart(fig2, use_container_width=True)

    # STORE-WISE LOSS REPORT
    st.subheader("🏪 Store-wise Model Loss to Cashify (Higher Maple Price)")
    # Simulate Maple price > Cashify condition (adjust if you have Maple price data)
    loss_conditions = lost_devices_df[lost_devices_df['Partner Contribution'] > 0]
    store_loss = loss_conditions.groupby('Store Name')['Partner Contribution'].sum().reset_index()
    st.dataframe(store_loss, use_container_width=True)

    # Download Buttons
    st.subheader("⬇️ Download Reports")
    excel_data = to_excel(price_comparison)
    st.download_button("Download Excel Report", data=excel_data, file_name="trade_in_analysis.xlsx")

    pdf_data = to_pdf(price_comparison)
    st.download_button("Download PDF Report", data=pdf_data, file_name="trade_in_analysis.pdf")

    # Reminder to escalate
    st.info("📧 Escalate issues with higher Maple prices but no support to Sandesh Kadam & Sandeep Selvamani.")
