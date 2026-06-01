import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(
    page_title="Bank Retention Intelligence",
    layout="wide",
    page_icon="📊"
)

# ---------------------- CUSTOM CSS ----------------------
st.markdown("""
<style>
body {
    background-color: #0E1117;
}
.metric-card {
    background: linear-gradient(135deg, #1f2937, #111827);
    padding: 20px;
    border-radius: 14px;
    color: white;
    text-align: center;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.4);
}
.kpi-title {
    font-size: 14px;
    color: #9CA3AF;
}
.kpi-value {
    font-size: 30px;
    font-weight: bold;
}
.section-title {
    font-size: 22px;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------- LOAD DATA ----------------------
@st.cache_data
def load_data():
    return pd.read_csv("processed_bank_data.csv")

df = load_data()

# ---------------------- SIDEBAR ----------------------
st.sidebar.title("📊 Navigation")

page = st.sidebar.radio("Go to", [
    "Executive Summary",
    "Engagement Analysis",
    "Product Analysis",
    "High Value Risk",
    "Retention Score",
    "Raw Data"
])

st.sidebar.markdown("---")

# Filters
st.sidebar.subheader("🔎 Filters")

engagement = st.sidebar.multiselect(
    "Engagement",
    df['EngagementCategory'].unique(),
    default=df['EngagementCategory'].unique()
)

products = st.sidebar.slider(
    "Products",
    int(df['NumOfProducts'].min()),
    int(df['NumOfProducts'].max()),
    (1, 4)
)

# Apply filters
df = df[
    (df['EngagementCategory'].isin(engagement)) &
    (df['NumOfProducts'].between(products[0], products[1]))
]

# ---------------------- KPI FUNCTION ----------------------
def kpi_card(title, value):
    return f"""
    <div class="metric-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """

# ---------------------- EXECUTIVE SUMMARY ----------------------
if page == "Executive Summary":

    st.title("🏦 Executive Dashboard")

    total = len(df)
    churn = df['Exited'].mean() * 100
    active = df['IsActiveMember'].mean() * 100
    avg_balance = df['Balance'].mean()

    c1, c2, c3, c4 = st.columns(4)

    c1.markdown(kpi_card("Customers", total), unsafe_allow_html=True)
    c2.markdown(kpi_card("Churn Rate", f"{churn:.2f}%"), unsafe_allow_html=True)
    c3.markdown(kpi_card("Active Rate", f"{active:.2f}%"), unsafe_allow_html=True)
    c4.markdown(kpi_card("Avg Balance", f"{avg_balance:,.0f}"), unsafe_allow_html=True)

    st.markdown("### 📈 Key Insights")

    if churn > 25:
        st.warning("⚠️ High churn rate detected — immediate retention action required")
    else:
        st.success("✅ Churn under control")

    st.info(f"""
    - Customers with low engagement are significantly more likely to churn  
    - Multi-product users show stronger retention  
    - High balance alone does not guarantee loyalty  
    """)

    fig = px.histogram(df, x="EngagementCategory", color="Exited",
                       title="Engagement vs Churn",
                       color_discrete_sequence=["#10B981", "#EF4444"])
    st.plotly_chart(fig, use_container_width=True)

# ---------------------- ENGAGEMENT ----------------------
elif page == "Engagement Analysis":

    st.title("📊 Engagement Analysis")

    fig1 = px.histogram(df, x="EngagementCategory", color="Exited",
                        barmode="group",
                        color_discrete_sequence=["#22C55E", "#EF4444"])
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.box(df, x="IsActiveMember", y="Balance",
                  title="Balance vs Activity")
    st.plotly_chart(fig2, use_container_width=True)

# ---------------------- PRODUCT ----------------------
elif page == "Product Analysis":

    st.title("📦 Product Utilization")

    prod = df.groupby("NumOfProducts")["Exited"].mean().reset_index()

    fig = px.bar(prod, x="NumOfProducts", y="Exited",
                 title="Product vs Churn",
                 color="Exited",
                 color_continuous_scale="reds")
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.box(df, x="NumOfProducts", y="Balance")
    st.plotly_chart(fig2, use_container_width=True)

# ---------------------- HIGH VALUE RISK ----------------------
elif page == "High Value Risk":

    st.title("⚠️ High Value Risk Customers")

    high_risk = df[
        (df['Balance'] > df['Balance'].quantile(0.75)) &
        (df['IsActiveMember'] == 0)
    ]

    st.metric("At Risk Customers", len(high_risk))

    fig = px.scatter(high_risk,
                     x="EstimatedSalary",
                     y="Balance",
                     color="Exited",
                     title="High Value Risk Segment",
                     color_discrete_sequence=["#22C55E", "#EF4444"])
    st.plotly_chart(fig, use_container_width=True)

# ---------------------- RETENTION SCORE ----------------------
elif page == "Retention Score":

    st.title("📊 Retention Strength")

    df['RetentionScore'] = (
        df['EngagementScore'] +
        df['NumOfProducts'] +
        df['Balance'] / 100000
    )

    fig = px.histogram(df, x="RetentionScore",
                       title="Retention Distribution",
                       color_discrete_sequence=["#6366F1"])
    st.plotly_chart(fig, use_container_width=True)

# ---------------------- RAW DATA ----------------------
elif page == "Raw Data":

    st.title("📋 Data Table")

    st.dataframe(df)

    csv = df.to_csv(index=False).encode('utf-8')

    st.download_button(
        "Download Data",
        csv,
        "filtered_data.csv",
        "text/csv"
    )