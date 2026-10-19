import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor


def prepare_monthly_sales(df):
    """Aggregate cleaned transactions into monthly revenue."""
    data = df.copy()

    data["InvoiceDate"] = pd.to_datetime(data["InvoiceDate"])

    monthly = (
        data.set_index("InvoiceDate")["TotalAmount"]
        .resample("ME")
        .sum()
        .reset_index()
    )

    monthly.columns = ["Month", "Revenue"]

    return monthly


def create_forecast_dataset(monthly):
    """Create lag-based features for monthly revenue forecasting."""
    data = monthly.copy()

    data["Lag_1"] = data["Revenue"].shift(1)
    data["Lag_2"] = data["Revenue"].shift(2)
    data["Lag_3"] = data["Revenue"].shift(3)

    data["MonthNumber"] = data["Month"].dt.month
    data["Year"] = data["Month"].dt.year

    data = data.dropna().reset_index(drop=True)

    return data


def forecast_revenue(df, forecast_months=3):
    """Forecast future monthly revenue using Gradient Boosting."""
    monthly = prepare_monthly_sales(df)
    model_data = create_forecast_dataset(monthly)

    feature_columns = [
        "Lag_1",
        "Lag_2",
        "Lag_3",
        "MonthNumber",
        "Year",
    ]

    X = model_data[feature_columns]
    y = model_data["Revenue"]

    model = GradientBoostingRegressor(
        n_estimators=200,
        random_state=42,
    )

    model.fit(X, y)

    history = monthly.copy()
    forecasts = []

    for _ in range(forecast_months):
        next_month = history["Month"].max() + pd.offsets.MonthEnd(1)

        lag_1 = history["Revenue"].iloc[-1]
        lag_2 = history["Revenue"].iloc[-2]
        lag_3 = history["Revenue"].iloc[-3]

        features = pd.DataFrame(
            {
                "Lag_1": [lag_1],
                "Lag_2": [lag_2],
                "Lag_3": [lag_3],
                "MonthNumber": [next_month.month],
                "Year": [next_month.year],
            }
        )

        predicted_revenue = model.predict(features)[0]

        forecasts.append(
            {
                "Month": next_month,
                "Revenue": predicted_revenue,
                "Type": "Forecast",
            }
        )

        history = pd.concat(
            [
                history,
                pd.DataFrame(
                    {
                        "Month": [next_month],
                        "Revenue": [predicted_revenue],
                    }
                ),
            ],
            ignore_index=True,
        )

    historical = monthly.copy()
    historical["Type"] = "Historical"

    forecast_df = pd.DataFrame(forecasts)

    result = pd.concat(
        [historical, forecast_df],
        ignore_index=True,
    )

    return result


if __name__ == "__main__":
    from data_loader import load_clean_data

    df = load_clean_data()

    result = forecast_revenue(df, forecast_months=3)

    print("DataPulse forecasting successful.")

    print("\n--- HISTORICAL DATA ---")
    print(result[result["Type"] == "Historical"].tail(5))

    print("\n--- NEXT 3 MONTH FORECAST ---")
    print(result[result["Type"] == "Forecast"].to_string(index=False))
