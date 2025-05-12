import streamlit as st # type: ignore
import pandas as pd  # type: ignore
import plotly.express as px  # type: ignore
from datetime import date, timedelta

st.title("📈 Trade-in Performance Dashboard")

# Load data from session
if 'data' not in st.session_state or not st.session_state.data:
    st.warning("No data available yet. Please add trade-in entries.")
    st.stop()

# Prepare main DataFrame
df = pd.DataFrame(st.session_state.data)
df["Date"] = pd.to_datetime(df["Date"])

# Date Filters
st.markdown("### 📅 Select Date Filter")
col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input("Start Date", value=date.today() - timedelta(days=7))
with col2:
    end_date = st.date_input("End Date", value=date.today())

filtered_df = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]

# KPI Section
st.markdown("### 🧮 Key Performance Indicators (KPI)")
total_target = filtered_df['Trade-in Target April Month'].sum()
total_maple = filtered_df['Maple & Mserv TOTAL'].sum()
total_cashify = filtered_df['Trade-in Lost with Cashify'].sum()
mtd_achieved_pct = (total_maple / total_target) * 100 if total_target else 0
market_share_pct = (total_maple / (total_maple + total_cashify)) * 100 if (total_maple + total_cashify) else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("🎯 Total Target", total_target)
col2.metric("📦 Maple Achieved", total_maple)
col3.metric("📦 Lost to Cashify", total_cashify)
col4.metric("📊 MTD Achieved %", f"{mtd_achieved_pct:.2f}%")
col5.metric("📈 Market Share %", f"{market_share_pct:.2f}%")

# SPOC Performance (Above 50%)
st.markdown("### 🏅 SPOC Performance (Above 50% Target)")
spoc_summary = filtered_df.groupby(["Spoc Name", "Store Name"]).agg({
    "Maple & Mserv TOTAL": "sum",
    "Trade-in Target April Month": "mean"
}).reset_index()
spoc_summary["Achieved %"] = (spoc_summary["Maple & Mserv TOTAL"] / spoc_summary["Trade-in Target April Month"]) * 100
above_50 = spoc_summary[spoc_summary["Achieved %"] >= 50]

fig = px.bar(
    above_50,
    x="Spoc Name",
    y="Maple & Mserv TOTAL",
    color_discrete_sequence=["#00FF7F"],
    text="Maple & Mserv TOTAL",
    hover_data=["Store Name", "Achieved %"]
)
fig.update_layout(title="SPOCs with >50% Target Achieved", xaxis_title="SPOC", yaxis_title="Trade-in Count")
st.plotly_chart(fig, use_container_width=True)

# Weekly Off Day Impact
st.markdown("### 📆 Weekly Off-Day Impact Analysis")
weekly_off_days = filtered_df["Weekly Off"].unique().tolist()
selected_off_day = st.selectbox("Select Weekly Off Day", weekly_off_days)

weekly_df = filtered_df[filtered_df["Weekly Off"] == selected_off_day]
impact = weekly_df.groupby("Date").agg({
    "Maple & Mserv TOTAL": "sum",
    "Trade-in Lost with Cashify": "sum"
}).reset_index()
impact_melted = impact.melt(id_vars="Date", var_name="Channel", value_name="Trade-ins")
impact_melted["Channel"] = impact_melted["Channel"].map({
    "Maple & Mserv TOTAL": "Maple",
    "Trade-in Lost with Cashify": "Cashify"
})

fig2 = px.bar(
    impact_melted,
    x="Date",
    y="Trade-ins",
    color="Channel",
    text="Trade-ins",
    color_discrete_map={"Maple": "#39FF14", "Cashify": "#228B22"}
)
fig2.update_layout(title=f"Trade-ins on {selected_off_day}s", xaxis_title="Date", yaxis_title="Number of Trade-ins")
st.plotly_chart(fig2, use_container_width=True)

# Underperforming SPOCs by Location
st.markdown("### 🔍 Underperforming SPOCs (< 50% Market Share)")
locations = filtered_df["Location"].unique().tolist()
selected_location = st.selectbox("Select Location", locations)

location_df = filtered_df[filtered_df["Location"] == selected_location]
market_share_df = location_df.groupby(["Spoc Name", "Store Name"]).agg({
    "Maple & Mserv TOTAL": "sum",
    "Trade-in Lost with Cashify": "sum"
}).reset_index()
market_share_df["Market Share %"] = (
    market_share_df["Maple & Mserv TOTAL"] /
    (market_share_df["Maple & Mserv TOTAL"] + market_share_df["Trade-in Lost with Cashify"]) * 100
).fillna(0)
underperformers = market_share_df[market_share_df["Market Share %"] < 50]

fig3 = px.bar(
    underperformers,
    x="Spoc Name",
    y="Maple & Mserv TOTAL",
    color_discrete_sequence=["#FF6347"],
    text="Maple & Mserv TOTAL",
    hover_data=["Store Name", "Market Share %"]
)
fig3.update_layout(title="Underperforming SPOCs", xaxis_title="SPOC", yaxis_title="Trade-in Count")
st.plotly_chart(fig3, use_container_width=True)
