import pandas as pd


def calculate_rfm(df):
    """Calculate Recency, Frequency, and Monetary values for each customer."""
    data = df.copy()

    data["InvoiceDate"] = pd.to_datetime(data["InvoiceDate"])
    data = data.dropna(subset=["Customer ID"]).copy()

    reference_date = data["InvoiceDate"].max() + pd.Timedelta(days=1)

    rfm = (
        data.groupby("Customer ID")
        .agg(
            Recency=("InvoiceDate", lambda x: (reference_date - x.max()).days),
            Frequency=("Invoice", "nunique"),
            Monetary=("TotalAmount", "sum"),
        )
        .reset_index()
    )

    rfm["Monetary"] = rfm["Monetary"].round(2)

    return rfm


def segment_customers(rfm):
    """Assign customer segments using RFM scores."""
    data = rfm.copy()

    # Higher score is better for all three dimensions.
    data["R_Score"] = pd.qcut(
        data["Recency"].rank(method="first"),
        5,
        labels=[5, 4, 3, 2, 1],
    ).astype(int)

    data["F_Score"] = pd.qcut(
        data["Frequency"].rank(method="first"),
        5,
        labels=[1, 2, 3, 4, 5],
    ).astype(int)

    data["M_Score"] = pd.qcut(
        data["Monetary"].rank(method="first"),
        5,
        labels=[1, 2, 3, 4, 5],
    ).astype(int)

    data["RFM_Score"] = (
        data["R_Score"] + data["F_Score"] + data["M_Score"]
    )

    def classify(row):
        r = row["R_Score"]
        f = row["F_Score"]
        m = row["M_Score"]

        if r >= 4 and f >= 4 and m >= 4:
            return "High Value"
        elif r >= 4 and f >= 3:
            return "Loyal"
        elif r >= 4 and m >= 3:
            return "Potential"
        elif r <= 2 and f >= 3 and m >= 3:
            return "At Risk"
        elif r <= 2 and f <= 2:
            return "Low Engagement"
        else:
            return "Regular"

    data["Segment"] = data.apply(classify, axis=1)

    return data


if __name__ == "__main__":
    from data_loader import load_clean_data

    df = load_clean_data()
    rfm = calculate_rfm(df)
    segmented = segment_customers(rfm)

    print("DataPulse customer segmentation successful.")
    print(f"Customers analyzed: {len(segmented):,}")

    print("\nSegment distribution:")
    print(segmented["Segment"].value_counts())

    print("\nAverage monetary value by segment:")
    print(
        segmented.groupby("Segment")["Monetary"]
        .mean()
        .sort_values(ascending=False)
    )
