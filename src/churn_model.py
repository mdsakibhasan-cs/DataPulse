import pandas as pd
import joblib

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)


MODEL_PATH = Path("models/churn_gradient_boosting.joblib")
REPORT_PATH = Path("reports/churn_model_evaluation.csv")

MODEL_PATH.parent.mkdir(exist_ok=True)
REPORT_PATH.parent.mkdir(exist_ok=True)


def build_churn_dataset(df, prediction_window_days=90):
    data = df.copy()
    data["InvoiceDate"] = pd.to_datetime(data["InvoiceDate"])
    data = data.dropna(subset=["Customer ID"]).copy()

    max_date = data["InvoiceDate"].max()
    cutoff_date = max_date - pd.Timedelta(days=prediction_window_days)

    historical = data[data["InvoiceDate"] <= cutoff_date].copy()

    future = data[
        (data["InvoiceDate"] > cutoff_date)
        & (data["InvoiceDate"] <= max_date)
    ].copy()

    reference_date = cutoff_date + pd.Timedelta(days=1)

    features = (
        historical.groupby("Customer ID")
        .agg(
            Recency=("InvoiceDate", lambda x: (reference_date - x.max()).days),
            Frequency=("Invoice", "nunique"),
            Monetary=("TotalAmount", "sum"),
            AvgOrderValue=("TotalAmount", lambda x: x.sum() / x.nunique()),
            TotalQuantity=("Quantity", "sum"),
            UniqueProducts=("StockCode", "nunique"),
            FirstPurchase=("InvoiceDate", "min"),
        )
        .reset_index()
    )

    features["TenureDays"] = (
        reference_date - features["FirstPurchase"]
    ).dt.days

    features = features.drop(columns=["FirstPurchase"])

    future_customers = set(future["Customer ID"].unique())

    features["Churn"] = (
        ~features["Customer ID"].isin(future_customers)
    ).astype(int)

    return features


def evaluate_and_save_model(df):
    feature_columns = [
        "Recency",
        "Frequency",
        "Monetary",
        "AvgOrderValue",
        "TotalQuantity",
        "UniqueProducts",
        "TenureDays",
    ]

    X = df[feature_columns]
    y = df["Churn"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = GradientBoostingClassifier(
        n_estimators=200,
        random_state=42,
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(y_test, predictions)
    recall = recall_score(y_test, predictions)
    f1 = f1_score(y_test, predictions)
    roc_auc = roc_auc_score(y_test, probabilities)

    cm = confusion_matrix(y_test, predictions)

    report = pd.DataFrame(
        {
            "Metric": [
                "Accuracy",
                "Precision",
                "Recall",
                "F1 Score",
                "ROC-AUC",
            ],
            "Value": [
                accuracy,
                precision,
                recall,
                f1,
                roc_auc,
            ],
        }
    )

    report.to_csv(REPORT_PATH, index=False)
    joblib.dump(model, MODEL_PATH)

    print("DataPulse churn model evaluation successful.")

    print("\n--- FINAL MODEL ---")
    print("Gradient Boosting")

    print("\n--- PERFORMANCE ---")
    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1 Score : {f1:.4f}")
    print(f"ROC-AUC  : {roc_auc:.4f}")

    print("\n--- CONFUSION MATRIX ---")
    print(cm)

    print("\n--- CLASSIFICATION REPORT ---")
    print(classification_report(y_test, predictions))

    print(f"\nModel saved: {MODEL_PATH}")
    print(f"Report saved: {REPORT_PATH}")


if __name__ == "__main__":
    from data_loader import load_clean_data

    df = load_clean_data()
    churn_data = build_churn_dataset(df)

    evaluate_and_save_model(churn_data)
