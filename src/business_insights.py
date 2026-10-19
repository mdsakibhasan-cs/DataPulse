import pandas as pd


def generate_business_insights(df):
    """Generate business KPIs and analytical summaries for DataPulse."""
    data = df.copy()

    data["InvoiceDate"] = pd.to_datetime(data["InvoiceDate"])
    data["Year"] = data["InvoiceDate"].dt.year
    data["Month"] = data["InvoiceDate"].dt.to_period("M").astype(str)

    # Core KPIs
    total_revenue = data["TotalAmount"].sum()
    total_quantity = data["Quantity"].sum()
    total_orders = data["Invoice"].nunique()
    total_products = data["StockCode"].nunique()
    total_customers = data["Customer ID"].nunique()

    order_values = data.groupby("Invoice")["TotalAmount"].sum()
    average_order_value = order_values.mean()

    # Monthly revenue
    monthly_revenue = (
        data.groupby("Month")["TotalAmount"]
        .sum()
        .sort_index()
    )

    # Yearly revenue
    yearly_revenue = (
        data.groupby("Year")["TotalAmount"]
        .sum()
        .sort_index()
    )

    # Monthly order count
    monthly_orders = (
        data.groupby("Month")["Invoice"]
        .nunique()
        .sort_index()
    )

    # Top products by revenue
    top_products = (
        data.groupby("Description")["TotalAmount"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    # Top countries by revenue
    top_countries = (
        data.groupby("Country")["TotalAmount"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    # Customer revenue
    customer_revenue = (
        data.dropna(subset=["Customer ID"])
        .groupby("Customer ID")["TotalAmount"]
        .sum()
        .sort_values(ascending=False)
    )

    return {
        "total_revenue": round(total_revenue, 2),
        "total_quantity": int(total_quantity),
        "total_orders": int(total_orders),
        "total_products": int(total_products),
        "total_customers": int(total_customers),
        "average_order_value": round(average_order_value, 2),
        "monthly_revenue": monthly_revenue,
        "yearly_revenue": yearly_revenue,
        "monthly_orders": monthly_orders,
        "top_products": top_products,
        "top_countries": top_countries,
        "customer_revenue": customer_revenue,
    }


if __name__ == "__main__":
    from data_loader import load_clean_data

    df = load_clean_data()
    insights = generate_business_insights(df)

    print("DataPulse Business Insights successful.")
    print(f"Total revenue: GBP {insights['total_revenue']:,.2f}")
    print(f"Total orders: {insights['total_orders']:,}")
    print(f"Total customers: {insights['total_customers']:,}")
    print(f"Average order value: GBP {insights['average_order_value']:,.2f}")

    print("\nYearly revenue:")
    print(insights["yearly_revenue"])

    print("\nTop 5 countries:")
    print(insights["top_countries"].head(5))
