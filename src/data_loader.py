import pandas as pd
from pathlib import Path
import urllib.request
import zipfile


DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "online_retail_II.xlsx"
CLEAN_FILE = DATA_DIR / "cleaned_sales.csv"

DATA_URL = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
ZIP_FILE = DATA_DIR / "online_retail_ii.zip"


def ensure_dataset():
    """Download and locate the UCI Online Retail II Excel dataset."""
    DATA_DIR.mkdir(exist_ok=True)

    if DATA_FILE.exists():
        return

    urllib.request.urlretrieve(DATA_URL, ZIP_FILE)

    with zipfile.ZipFile(ZIP_FILE, "r") as zip_ref:
        zip_ref.extractall(DATA_DIR)

    # Find the Excel file regardless of the filename used inside the ZIP.
    excel_files = list(DATA_DIR.glob("*.xlsx"))

    if not excel_files:
        raise FileNotFoundError(
            "Dataset ZIP was downloaded, but no Excel file was found."
        )

    downloaded_excel = excel_files[0]

    if downloaded_excel != DATA_FILE:
        downloaded_excel.rename(DATA_FILE)

    if ZIP_FILE.exists():
        ZIP_FILE.unlink()


def load_raw_data():
    """Load and combine both yearly sheets from the original Excel file."""
    ensure_dataset()

    sheet_1 = pd.read_excel(
        DATA_FILE,
        sheet_name="Year 2009-2010"
    )

    sheet_2 = pd.read_excel(
        DATA_FILE,
        sheet_name="Year 2010-2011"
    )

    return pd.concat(
        [sheet_1, sheet_2],
        ignore_index=True
    )


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
        return pd.read_csv(
            CLEAN_FILE,
            parse_dates=["InvoiceDate"]
        )

    raw_data = load_raw_data()
    clean_data = clean_sales_data(raw_data)

    clean_data.to_csv(
        CLEAN_FILE,
        index=False
    )

    return clean_data


if __name__ == "__main__":
    df = load_clean_data()

    print("DataPulse data loader successful.")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(
        f"Date range: "
        f"{df['InvoiceDate'].min()} "
        f"to {df['InvoiceDate'].max()}"
    )
    print(
        f"Total revenue: "
        f"{df['TotalAmount'].sum():,.2f}"
    )