import streamlit as st
import pandas as pd
import plotly.express as px
import io
from fpdf import FPDF
from datetime import datetime
import tempfile
import plotly.io as pio


# --- 🔐 LOGIN ENFORCEMENT ---
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("🔒 You must be logged in to view this page.")
    st.stop()

# --- Load Data ---
df = pd.read_excel("/Users/maple/Desktop/Transfer/Final Dashboard for the trade-in/views/March Summary of Trade-in (1).xlsx")
df.columns = df.columns.str.strip()

exclude_spocs = ["No-spoc", "Joining on 14th April, 2025", "Joining on 24th April,2025", "Joined on 9th April,2025"]
df = df[~df["Spoc Name"].isin(exclude_spocs)]

st.title("📊 Trade-in Performance Dashboard - March 2025")

# Required column check
required_columns = [
    "Trade-in Lost with Cashify March 2025", "Maple & Mserv TOTAL", "Maple MTD Achieved %",
    "Market Share %", "Trade-in Target March Month", "Spoc Name", "Store Name",
    "State", "Weekly Off", "Location"
]
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
    st.stop()

# === KPI SECTION ===
st.header("Key Performance Indicators")

kpi1 = df["Trade-in Lost with Cashify March 2025"].sum()
kpi2 = df["Maple & Mserv TOTAL"].sum()
kpi3 = round(df["Maple MTD Achieved %"].mean())
kpi4 = round(df["Market Share %"].mean())

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Trade-in Lost (Cashify)", f"{kpi1}")
col2.metric("Total Maple & Mserv", f"{kpi2}")
col3.metric("Avg Maple MTD Achieved %", f"{kpi3}%")
col4.metric("Avg Market Share %", f"{kpi4}%")

# === SPOC Target Achievement Section ===
st.header("SPOC Target Achievements")
achieved_df = df[df["Maple & Mserv TOTAL"] >= df["Trade-in Target March Month"]]
st.subheader(f"✅ Total SPOCs Achieved Target: {achieved_df.shape[0]}")

fig_ach = px.bar(
    achieved_df,
    x="Spoc Name",
    y="Maple & Mserv TOTAL",
    color="State",
    text="Maple & Mserv TOTAL",
    labels={"Maple & Mserv TOTAL": "Total Maple & Mserv"},
    title="SPOCs Achieved Trade-in Targets",
)
fig_ach.update_traces(textposition="outside")
fig_ach.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_ach, use_container_width=True)

# === Top 10 Performers Section ===
st.header("Top 10 Performers by Store")
top10 = df.sort_values("Maple & Mserv TOTAL", ascending=False).head(10)
top_state = top10["State"].value_counts().idxmax()

selected_State = st.selectbox("🌟 Select a Top Performing State", df["State"].unique(), index=list(df["State"].unique()).index(top_state))

State_df = df[df["State"] == selected_State].sort_values("Maple & Mserv TOTAL", ascending=False)
fig_top10 = px.bar(
    State_df,
    x="Store Name",
    y="Maple & Mserv TOTAL",
    color="Store Name",
    text="Maple & Mserv TOTAL",
    title=f"Top Stores in {selected_State} State",
)
fig_top10.update_traces(textposition="outside")
fig_top10.update_layout(xaxis_tickangle=-45, showlegend=False)
st.plotly_chart(fig_top10, use_container_width=True)

# === Weekly Off Analysis Section ===
st.header("Weekly Off Trade-in Comparison")
weekly_off_options = sorted(df["Weekly Off"].dropna().astype(str).unique())
selected_off_day = st.selectbox("📅 Select Weekly Off Day", weekly_off_options)

weekly_df = df[df["Weekly Off"] == selected_off_day]
weekly_df_filtered = weekly_df[["Store Name", "Spoc Name", "Maple & Mserv TOTAL", "Trade-in Lost with Cashify March 2025"]]

melted_weekly = weekly_df_filtered.melt(
    id_vars=["Store Name", "Spoc Name"],
    value_vars=["Maple & Mserv TOTAL", "Trade-in Lost with Cashify March 2025"],
    var_name="Source",
    value_name="Trade-in Count"
)

fig_weekly = px.bar(
    melted_weekly,
    x="Store Name",
    y="Trade-in Count",
    color="Source",
    barmode="group",
    text="Trade-in Count",
    title=f"📍 Trade-in Comparison on Weekly Off - {selected_off_day}",
    hover_data=["Spoc Name"]
)
fig_weekly.update_traces(textposition="outside")
fig_weekly.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_weekly, use_container_width=True)

# === SPOCs under 50% Achievement ===
st.header("SPOCs Below 50% Achievement")
df["% Achieved"] = df.apply(
    lambda row: round((row["Maple & Mserv TOTAL"] / row["Trade-in Target March Month"]) * 100, 2)
    if row["Trade-in Target March Month"] > 0 else 0, axis=1
)
under_50 = df[df["% Achieved"] < 50]

fig_under = px.bar(
    under_50,
    x="Spoc Name",
    y="% Achieved",
    color="State",
    text="% Achieved",
    title="SPOCs with < 50% Target Achievement",
)
fig_under.update_traces(textposition="outside")
fig_under.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_under, use_container_width=True)

# === Export Section ===
st.header("📥 Export Options")

excel_buffer = io.BytesIO()
df.to_excel(excel_buffer, index=False, engine='xlsxwriter')
st.download_button(
    label="Download Excel",
    data=excel_buffer,
    file_name="March_Trade-in_Report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# === PDF Export ===
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Trade-in KPI Summary - March 2025", ln=True, align="C")
        self.ln(5)

    def section_title(self, title):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, ln=True)
        self.ln(2)

    def section_body(self, text):
        self.set_font("Arial", "", 11)
        self.multi_cell(0, 8, text)
        self.ln(3)

    def insert_chart(self, image_path):
        self.image(image_path, w=180)
        self.ln(5)

pdf = PDF()
pdf.add_page()
pdf.section_title("Key Performance Indicators")
pdf.section_body(
    f"""- Total Trade-in Lost (Cashify): {kpi1}
- Total Maple & Mserv: {kpi2}
- Avg Maple MTD Achieved %: {kpi3}%
- Avg Market Share %: {kpi4}%"""
)

pdf.add_page()
pdf.section_title("SPOCs Achieved Targets")
with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
    pio.write_image(fig_ach, tmpfile.name, width=900, height=600)
    pdf.insert_chart(tmpfile.name)

pdf.add_page()
pdf.section_title(f"Top Performing Stores in {selected_State}")
with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
    pio.write_image(fig_top10, tmpfile.name, width=900, height=600)
    pdf.insert_chart(tmpfile.name)

pdf.add_page()
pdf.section_title(f"Weekly Off Analysis - {selected_off_day}")
with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
    pio.write_image(fig_weekly, tmpfile.name, width=900, height=600)
    pdf.insert_chart(tmpfile.name)

pdf.add_page()
pdf.section_title("SPOCs with < 50% Target Achievement")
with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
    pio.write_image(fig_under, tmpfile.name, width=900, height=600)
    pdf.insert_chart(tmpfile.name)

pdf_output = io.BytesIO()
pdf_bytes = pdf.output(dest='S').encode('latin1')
pdf_output.write(pdf_bytes)
pdf_output.seek(0)

st.download_button(
    label="Download Full PDF Summary with Visuals",
    data=pdf_output,
    file_name="March_Trade-in_Visual_Summary.pdf",
    mime="application/pdf"
)
