import pandas as pd
from pathlib import Path


DATA_FILE = Path("data/online_retail_II.xlsx")
CLEAN_FILE = Path("data/cleaned_sales.csv")


def load_raw_data():
    """Load and combine both yearly sheets from the original Excel file."""
    sheet_1 = pd.read_excel(DATA_FILE, sheet_name="Year 2009-2010")
    sheet_2 = pd.read_excel(DATA_FILE, sheet_name="Year 2010-2011")

    df = pd.concat([sheet_1, sheet_2], ignore_index=True)

    return df


def clean_sales_data(df):
    """Clean transaction data for sales analytics."""
    data = df.copy()

    data["Invoice"] = data["Invoice"].astype(str)
    data["StockCode"] = data["StockCode"].astype(str)

    data = data[
        (data["Quantity"] > 0)
        & (data["Price"] > 0)
        & (~data["Invoice"].str.startswith("C"))
    ].copy()

    data["TotalAmount"] = data["Quantity"] * data["Price"]

    return data


def load_clean_data():
    """Load cleaned data, creating it from the raw dataset if necessary."""
    if CLEAN_FILE.exists():
        return pd.read_csv(CLEAN_FILE, parse_dates=["InvoiceDate"])

    raw_data = load_raw_data()
    clean_data = clean_sales_data(raw_data)

    clean_data.to_csv(CLEAN_FILE, index=False)

    return clean_data


if __name__ == "__main__":
    df = load_clean_data()

    print("DataPulse data loader successful.")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Date range: {df['InvoiceDate'].min()} to {df['InvoiceDate'].max()}")
    print(f"Total revenue: {df['TotalAmount'].sum():,.2f}")
