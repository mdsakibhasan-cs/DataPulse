import pandas as pd


def run_eda(df):
    """Generate core exploratory statistics for DataPulse."""
    data = df.copy()

    data["InvoiceDate"] = pd.to_datetime(data["InvoiceDate"])

    invoice_totals = data.groupby("Invoice")["TotalAmount"].sum()

    monthly_sales = (
        data.set_index("InvoiceDate")
        .resample("ME")["TotalAmount"]
        .sum()
    )

    top_products = (
        data.groupby("Description")["TotalAmount"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    country_sales = (
        data.groupby("Country")["TotalAmount"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    return {
        "total_revenue": round(data["TotalAmount"].sum(), 2),
        "total_quantity": int(data["Quantity"].sum()),
        "unique_orders": int(data["Invoice"].nunique()),
        "unique_products": int(data["StockCode"].nunique()),
        "unique_customers": int(data["Customer ID"].nunique()),
        "unique_countries": int(data["Country"].nunique()),
        "average_order_value": round(invoice_totals.mean(), 2),
        "monthly_sales": monthly_sales,
        "top_products": top_products,
        "country_sales": country_sales,
    }


if __name__ == "__main__":
    from data_loader import load_clean_data

    df = load_clean_data()
    results = run_eda(df)

    print("DataPulse EDA successful.")
    print(f"Total revenue: {results['total_revenue']:,.2f}")
    print(f"Total quantity: {results['total_quantity']:,}")
    print(f"Unique orders: {results['unique_orders']:,}")
    print(f"Unique products: {results['unique_products']:,}")
    print(f"Unique customers: {results['unique_customers']:,}")
    print(f"Unique countries: {results['unique_countries']:,}")
    print(f"Average order value: {results['average_order_value']:,.2f}")

    print("\nTop 10 products:")
    print(results["top_products"])
