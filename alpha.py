import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# Page Config
# =========================
st.set_page_config(page_title="Sales Compensation Dashboard", layout="wide")

# =========================
# Title
# =========================
st.title("Sales Compensation Dashboard")
st.markdown("Interactive dashboard for compensation, billing, revenue codes, and account analysis.")

# =========================
# Load Excel File
# =========================
file_path = "/Users/kpatel878@cable.comcast.com/Documents/ValidationFileMay2026.xlsx"
df = pd.read_excel(file_path, engine="openpyxl")

# =========================
# Clean Columns
# =========================
df.columns = df.columns.str.strip()

# =========================
# Convert Date Columns
# =========================
date_cols = ["INVOICE_DATE", "CHARGE_START_DATE", "CHARGE_END_DATE", "ACTV_DATE", "Cbfiscal"]
for col in date_cols:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

# =========================
# Convert Numeric Columns
# =========================
num_cols = ["COMP_AMT", "BILLABLE_AMT", "AGT_RATE"]
for col in num_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# =========================
# Fill Null Values
# =========================
fill_cols = [
    "ACCOUNT_NAME",
    "AGT_NAME",
    "AGT_NAME2",
    "CHARGE_TYPE",
    "REV_CD_DESC",
    "COUNTRY",
    "LOCATION"
]
for col in fill_cols:
    if col in df.columns:
        df[col] = df[col].fillna("Unknown")

# =========================
# Extra Derived Columns
# =========================
if "INVOICE_DATE" in df.columns:
    df["INVOICE_MONTH"] = df["INVOICE_DATE"].dt.to_period("M").astype(str)

# =========================
# Sidebar
# =========================
st.sidebar.markdown("## Dashboard Filters")
st.sidebar.markdown("Use the filters below to slice the dashboard.")

account_filter = st.sidebar.multiselect(
    "Select Account",
    options=sorted(df["ACCOUNT_NAME"].dropna().unique()) if "ACCOUNT_NAME" in df.columns else []
)

agent_filter = st.sidebar.multiselect(
    "Select Agent",
    options=sorted(df["AGT_NAME"].dropna().unique()) if "AGT_NAME" in df.columns else []
)

charge_filter = st.sidebar.multiselect(
    "Select Charge Type",
    options=sorted(df["CHARGE_TYPE"].dropna().unique()) if "CHARGE_TYPE" in df.columns else []
)

rev_filter = st.sidebar.multiselect(
    "Select Revenue Code",
    options=sorted(df["REV_CD_DESC"].dropna().unique()) if "REV_CD_DESC" in df.columns else []
)

month_filter = st.sidebar.multiselect(
    "Select Invoice Month",
    options=sorted(df["INVOICE_MONTH"].dropna().unique()) if "INVOICE_MONTH" in df.columns else []
)

top_n = st.sidebar.slider("Top N Agents", min_value=5, max_value=20, value=10)

# =========================
# Apply Filters
# =========================
filtered_df = df.copy()

if account_filter:
    filtered_df = filtered_df[filtered_df["ACCOUNT_NAME"].isin(account_filter)]

if agent_filter:
    filtered_df = filtered_df[filtered_df["AGT_NAME"].isin(agent_filter)]

if charge_filter:
    filtered_df = filtered_df[filtered_df["CHARGE_TYPE"].isin(charge_filter)]

if rev_filter:
    filtered_df = filtered_df[filtered_df["REV_CD_DESC"].isin(rev_filter)]

if month_filter:
    filtered_df = filtered_df[filtered_df["INVOICE_MONTH"].isin(month_filter)]

# =========================
# KPI Calculations
# =========================
total_billable = filtered_df["BILLABLE_AMT"].sum() if "BILLABLE_AMT" in filtered_df.columns else 0
total_comp = filtered_df["COMP_AMT"].sum() if "COMP_AMT" in filtered_df.columns else 0
avg_agt_rate = filtered_df["AGT_RATE"].mean() if "AGT_RATE" in filtered_df.columns else 0
total_records = len(filtered_df)

# =========================
# KPI Cards
# =========================
st.markdown("### Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div style='background-color:#f5f7fb;padding:18px;border-radius:12px;border:1px solid #e6eaf2;'>
            <div style='font-size:15px;color:#555;'>Total Billable Amount</div>
            <div style='font-size:28px;font-weight:bold;color:#111;'>${total_billable:,.2f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div style='background-color:#f5f7fb;padding:18px;border-radius:12px;border:1px solid #e6eaf2;'>
            <div style='font-size:15px;color:#555;'>Total Compensation</div>
            <div style='font-size:28px;font-weight:bold;color:#111;'>${total_comp:,.2f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div style='background-color:#f5f7fb;padding:18px;border-radius:12px;border:1px solid #e6eaf2;'>
            <div style='font-size:15px;color:#555;'>Average Agent Rate</div>
            <div style='font-size:28px;font-weight:bold;color:#111;'>{avg_agt_rate:.2%}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div style='background-color:#f5f7fb;padding:18px;border-radius:12px;border:1px solid #e6eaf2;'>
            <div style='font-size:15px;color:#555;'>Record Count</div>
            <div style='font-size:28px;font-weight:bold;color:#111;'>{total_records:,}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# =========================
# Charts Row 1
# =========================
st.markdown("### Revenue & Distribution")

chart1, chart2 = st.columns(2)

with chart1:
    if "REV_CD_DESC" in filtered_df.columns and "BILLABLE_AMT" in filtered_df.columns:
        rev_df = filtered_df.groupby("REV_CD_DESC", as_index=False)["BILLABLE_AMT"].sum()
        rev_df = rev_df.sort_values("BILLABLE_AMT", ascending=False)

        fig_rev = px.bar(
            rev_df,
            x="REV_CD_DESC",
            y="BILLABLE_AMT",
            title="Billable Amount by Revenue Code",
            color="BILLABLE_AMT",
            color_continuous_scale="Blues",
            text="BILLABLE_AMT"
        )
        fig_rev.update_traces(
            texttemplate="$%{text:,.2f}",
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Billable Amount: $%{y:,.2f}<extra></extra>"
        )
        fig_rev.update_layout(
            xaxis_title="Revenue Code",
            yaxis_title="Billable Amount ($)",
            yaxis_tickprefix="$",
            height=450
        )
        st.plotly_chart(fig_rev, use_container_width=True)

with chart2:
    if "CHARGE_TYPE" in filtered_df.columns:
        charge_df = filtered_df["CHARGE_TYPE"].value_counts().reset_index()
        charge_df.columns = ["CHARGE_TYPE", "COUNT"]

        fig_charge = px.pie(
            charge_df,
            names="CHARGE_TYPE",
            values="COUNT",
            title="Charge Type Distribution",
            hole=0.45
        )
        fig_charge.update_traces(
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}<extra></extra>"
        )
        fig_charge.update_layout(height=450)
        st.plotly_chart(fig_charge, use_container_width=True)

# =========================
# Charts Row 2
# =========================
st.markdown("### Trends & Agent Performance")

chart3, chart4 = st.columns(2)

with chart3:
    if "INVOICE_DATE" in filtered_df.columns and "BILLABLE_AMT" in filtered_df.columns:
        trend_df = filtered_df.groupby("INVOICE_DATE", as_index=False)["BILLABLE_AMT"].sum()
        trend_df = trend_df.sort_values("INVOICE_DATE")

        fig_trend = px.line(
            trend_df,
            x="INVOICE_DATE",
            y="BILLABLE_AMT",
            title="Invoice Trend by Date",
            markers=True
        )
        fig_trend.update_traces(
            hovertemplate="<b>%{x}</b><br>Billable Amount: $%{y:,.2f}<extra></extra>"
        )
        fig_trend.update_layout(
            xaxis_title="Invoice Date",
            yaxis_title="Billable Amount ($)",
            yaxis_tickprefix="$",
            height=450
        )
        st.plotly_chart(fig_trend, use_container_width=True)

with chart4:
    if "AGT_NAME" in filtered_df.columns and "COMP_AMT" in filtered_df.columns:
        agent_df = filtered_df.groupby("AGT_NAME", as_index=False)["COMP_AMT"].sum()
        agent_df = agent_df.sort_values("COMP_AMT", ascending=False).head(top_n)

        fig_agent = px.bar(
            agent_df,
            x="AGT_NAME",
            y="COMP_AMT",
            title=f"Top {top_n} Agents by Compensation",
            color="COMP_AMT",
            color_continuous_scale="Greens",
            text="COMP_AMT"
        )
        fig_agent.update_traces(
            texttemplate="$%{text:,.2f}",
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Compensation: $%{y:,.2f}<extra></extra>"
        )
        fig_agent.update_layout(
            xaxis_title="Agent Name",
            yaxis_title="Compensation ($)",
            yaxis_tickprefix="$",
            height=450
        )
        st.plotly_chart(fig_agent, use_container_width=True)

st.markdown("---")

# =========================
# Top Accounts Summary
# =========================
st.subheader("Top Accounts Summary")

if "ACCOUNT_NAME" in filtered_df.columns:
    summary_cols = ["ACCOUNT_NAME"]
    if "BILLABLE_AMT" in filtered_df.columns:
        summary_cols.append("BILLABLE_AMT")
    if "COMP_AMT" in filtered_df.columns:
        summary_cols.append("COMP_AMT")

    if len(summary_cols) > 1:
        top_accounts = filtered_df.groupby("ACCOUNT_NAME", as_index=False)[summary_cols[1:]].sum()

        if "BILLABLE_AMT" in top_accounts.columns:
            top_accounts = top_accounts.sort_values("BILLABLE_AMT", ascending=False)

        display_top_accounts = top_accounts.copy()

        if "BILLABLE_AMT" in display_top_accounts.columns:
            display_top_accounts["BILLABLE_AMT"] = display_top_accounts["BILLABLE_AMT"].map(
                lambda x: f"${x:,.2f}" if pd.notna(x) else ""
            )

        if "COMP_AMT" in display_top_accounts.columns:
            display_top_accounts["COMP_AMT"] = display_top_accounts["COMP_AMT"].map(
                lambda x: f"${x:,.2f}" if pd.notna(x) else ""
            )

        st.dataframe(display_top_accounts.head(10), use_container_width=True)

st.markdown("---")

# =========================
# Detailed Data View
# =========================
st.subheader("Detailed Data View")

display_df = filtered_df.copy()

# Format dates
for col in ["INVOICE_DATE", "CHARGE_START_DATE", "CHARGE_END_DATE", "ACTV_DATE", "Cbfiscal"]:
    if col in display_df.columns:
        display_df[col] = pd.to_datetime(display_df[col], errors="coerce").dt.strftime("%Y-%m-%d")

# Format amount columns with $
amount_cols = ["COMP_AMT", "BILLABLE_AMT"]
for col in amount_cols:
    if col in display_df.columns:
        display_df[col] = display_df[col].map(lambda x: f"${x:,.2f}" if pd.notna(x) else "")

# Format percentage
if "AGT_RATE" in display_df.columns:
    display_df["AGT_RATE"] = display_df["AGT_RATE"].map(lambda x: f"{x:.2%}" if pd.notna(x) else "")

# Clean invoice number if needed
if "INVOICE_NUMBER" in display_df.columns:
    display_df["INVOICE_NUMBER"] = display_df["INVOICE_NUMBER"].astype(str).str.replace(".0", "", regex=False)

st.dataframe(display_df, use_container_width=True)

# =========================
# Download Button
# =========================
csv_data = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Filtered Data as CSV",
    data=csv_data,
    file_name="filtered_sales_comp_data.csv",
    mime="text/csv"
)