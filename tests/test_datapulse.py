import pandas as pd

from src.data_loader import clean_sales_data
from src.customer_segmentation import calculate_rfm, segment_customers


def test_clean_sales_data_removes_invalid_transactions():
    data = pd.DataFrame(
        {
            "Invoice": ["10001", "C10002", "10003", "10004"],
            "StockCode": ["A", "B", "C", "D"],
            "Description": ["A", "B", "C", "D"],
            "Quantity": [2, 1, -1, 3],
            "InvoiceDate": pd.to_datetime(
                ["2011-01-01", "2011-01-02", "2011-01-03", "2011-01-04"]
            ),
            "Price": [10, 20, 30, 0],
            "Customer ID": [1, 2, 3, 4],
            "Country": ["UK", "UK", "UK", "UK"],
        }
    )

    cleaned = clean_sales_data(data)

    assert len(cleaned) == 1
    assert cleaned.iloc[0]["Invoice"] == "10001"
    assert cleaned.iloc[0]["TotalAmount"] == 20


def test_rfm_calculation():
    data = pd.DataFrame(
        {
            "Invoice": ["10001", "10002", "10003"],
            "StockCode": ["A", "B", "C"],
            "InvoiceDate": pd.to_datetime(
                ["2011-01-01", "2011-01-10", "2011-01-20"]
            ),
            "Quantity": [2, 1, 3],
            "TotalAmount": [20.0, 30.0, 60.0],
            "Customer ID": [1, 1, 2],
        }
    )

    rfm = calculate_rfm(data)

    assert len(rfm) == 2
    assert set(rfm["Customer ID"]) == {1, 2}
    assert rfm["Frequency"].min() >= 1
    assert rfm["Monetary"].min() > 0


def test_customer_segmentation():
    rfm = pd.DataFrame(
        {
            "Customer ID": range(1, 11),
            "Recency": range(1, 11),
            "Frequency": range(1, 11),
            "Monetary": [100 * i for i in range(1, 11)],
        }
    )

    segmented = segment_customers(rfm)

    assert len(segmented) == 10
    assert "Segment" in segmented.columns
    assert segmented["Segment"].notna().all()
    assert set(segmented["Segment"]).issubset(
        {
            "High Value",
            "Loyal",
            "Potential",
            "At Risk",
            "Low Engagement",
            "Regular",
        }
    )
