import pandas as pd
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_clean_data
from src.business_insights import generate_business_insights
from src.customer_segmentation import calculate_rfm, segment_customers


st.set_page_config(
    page_title="DataPulse",
    page_icon="📊",
    layout="wide",
)

st.title("📊 DataPulse")
st.subheader("End-to-End Business Intelligence & Predictive Analytics Platform")

st.write(
    "DataPulse analyzes e-commerce data to uncover business insights, "
    "customer behavior, churn risk, and sales trends."
)

df = load_clean_data()
insights = generate_business_insights(df)

st.success("Data loaded successfully.")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Revenue", f"£{insights['total_revenue']:,.2f}")

with col2:
    st.metric("Total Orders", f"{insights['total_orders']:,}")

with col3:
    st.metric("Total Customers", f"{insights['total_customers']:,}")

with col4:
    st.metric(
        "Average Order Value",
        f"£{insights['average_order_value']:,.2f}",
    )

st.divider()

st.header("📈 Sales Analytics")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Monthly Revenue")
    st.line_chart(insights["monthly_revenue"])

with chart_col2:
    st.subheader("Monthly Orders")
    st.line_chart(insights["monthly_orders"])

st.divider()

st.header("🌍 Product & Geographic Analytics")

product_col, country_col = st.columns(2)

with product_col:
    st.subheader("Top 10 Products by Revenue")
    top_products = insights["top_products"].sort_values(ascending=True)
    st.bar_chart(top_products)

with country_col:
    st.subheader("Top 10 Countries by Revenue")
    top_countries = insights["top_countries"].sort_values(ascending=True)
    st.bar_chart(top_countries)

st.divider()

st.header("👥 Customer Segmentation")

rfm = calculate_rfm(df)
segmented = segment_customers(rfm)

segment_counts = (
    segmented["Segment"]
    .value_counts()
    .sort_values(ascending=True)
)

segment_col1, segment_col2 = st.columns(2)

with segment_col1:
    st.subheader("Customer Segment Distribution")
    st.bar_chart(segment_counts)

with segment_col2:
    st.subheader("Average Monetary Value by Segment")

    segment_value = (
        segmented.groupby("Segment")["Monetary"]
        .mean()
        .sort_values(ascending=True)
    )

    st.bar_chart(segment_value)

import joblib

from src.churn_model import build_churn_dataset


st.divider()

st.header("🤖 Churn Prediction & Risk Analysis")

churn_data = build_churn_dataset(df)

churn_model = joblib.load(
    PROJECT_ROOT / "models" / "churn_gradient_boosting.joblib"
)

churn_features = [
    "Recency",
    "Frequency",
    "Monetary",
    "AvgOrderValue",
    "TotalQuantity",
    "UniqueProducts",
    "TenureDays",
]

churn_data["Churn Probability"] = churn_model.predict_proba(
    churn_data[churn_features]
)[:, 1]

churn_data["Predicted Risk"] = (
    churn_data["Churn Probability"] >= 0.50
).astype(int)

churn_total = len(churn_data)
actual_churned = int(churn_data["Churn"].sum())
actual_active = churn_total - actual_churned
high_risk = int(churn_data["Predicted Risk"].sum())

churn_col1, churn_col2, churn_col3, churn_col4 = st.columns(4)

with churn_col1:
    st.metric("Customers Analyzed", f"{churn_total:,}")

with churn_col2:
    st.metric("Historical Churned", f"{actual_churned:,}")

with churn_col3:
    st.metric("Historical Active", f"{actual_active:,}")

with churn_col4:
    st.metric("Predicted High Risk", f"{high_risk:,}")

st.subheader("Churn Model Performance")

performance = pd.read_csv(
    PROJECT_ROOT / "reports" / "churn_model_evaluation.csv"
)

performance["Value"] = performance["Value"].map(
    lambda x: f"{x:.2%}"
)

st.dataframe(
    performance,
    use_container_width=True,
    hide_index=True,
)

st.subheader("Churn Risk Distribution")

risk_distribution = (
    churn_data["Predicted Risk"]
    .map({0: "Lower Risk", 1: "High Risk"})
    .value_counts()
    .sort_values(ascending=True)
)

st.bar_chart(risk_distribution)

st.caption(
    "Churn labels are based on a historical 90-day prediction window; "
    "they are not a guarantee of future customer behavior."
)

from src.forecasting import forecast_revenue


st.divider()

st.header("🔮 Sales Forecasting")

forecast_data = forecast_revenue(df, forecast_months=3)

historical_forecast = forecast_data[
    forecast_data["Type"] == "Historical"
][["Month", "Revenue"]].copy()

future_forecast = forecast_data[
    forecast_data["Type"] == "Forecast"
][["Month", "Revenue"]].copy()

historical_forecast["Revenue"] = historical_forecast["Revenue"].round(2)
future_forecast["Revenue"] = future_forecast["Revenue"].round(2)

forecast_chart_data = forecast_data.pivot(
    index="Month",
    columns="Type",
    values="Revenue",
)

st.subheader("Historical Revenue & 3-Month Forecast")

st.line_chart(forecast_chart_data)

st.subheader("Forecast Values")

display_forecast = future_forecast.copy()
display_forecast["Month"] = display_forecast["Month"].dt.strftime("%b %Y")
display_forecast["Revenue"] = display_forecast["Revenue"].map(
    lambda x: f"£{x:,.2f}"
)

st.dataframe(
    display_forecast,
    use_container_width=True,
    hide_index=True,
)

st.caption(
    "Forecast values are model-generated estimates based on historical "
    "monthly revenue patterns and should not be interpreted as guaranteed future sales."
)

# ============================================================
# BUSINESS INSIGHTS & RECOMMENDATIONS
# ============================================================

from src.business_insights import generate_business_insights

business = generate_business_insights(df)

st.divider()

st.header("💡 Business Insights & Recommendations")

st.subheader("Key Business Insights")

yearly_revenue = business["yearly_revenue"]

if len(yearly_revenue) >= 2:
    latest_year = yearly_revenue.index[-1]
    previous_year = yearly_revenue.index[-2]

    latest_revenue = yearly_revenue.iloc[-1]
    previous_revenue = yearly_revenue.iloc[-2]

    revenue_change = (
        (latest_revenue - previous_revenue) / previous_revenue
    ) * 100

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Latest Year Revenue",
            f"£{latest_revenue:,.2f}"
        )

    with col2:
        st.metric(
            "Previous Year Revenue",
            f"£{previous_revenue:,.2f}"
        )

    with col3:
        st.metric(
            "Year-over-Year Change",
            f"{revenue_change:.2f}%"
        )

st.subheader("Top Business Signals")

top_product = business["top_products"].index[0]
top_product_revenue = business["top_products"].iloc[0]

top_country = business["top_countries"].index[0]
top_country_revenue = business["top_countries"].iloc[0]

insight_col1, insight_col2 = st.columns(2)

with insight_col1:
    st.markdown(
        f"""
        **🏆 Top Product by Revenue**

        **{top_product}**

        Revenue: **£{top_product_revenue:,.2f}**
        """
    )

with insight_col2:
    st.markdown(
        f"""
        **🌍 Top Market by Revenue**

        **{top_country}**

        Revenue: **£{top_country_revenue:,.2f}**
        """
    )

st.subheader("Recommended Actions")

st.markdown(
    """
    **1. Focus on high-value customers**  
    Prioritize retention campaigns and personalized offers for high-value customers.

    **2. Monitor at-risk customers**  
    Customers showing declining engagement should receive targeted retention campaigns.

    **3. Optimize top-performing products**  
    Maintain inventory availability and promotional focus on products generating the highest revenue.

    **4. Monitor seasonal demand**  
    Historical revenue patterns can help prepare inventory and marketing campaigns ahead of high-demand periods.

    **5. Use churn predictions for proactive retention**  
    Model-generated churn risk can help prioritize customers for further analysis and intervention.
    """
)

st.caption(
    "Business recommendations are analytical suggestions derived from historical "
    "transaction patterns and predictive model outputs; they should support, "
    "not replace, business judgment."
)

