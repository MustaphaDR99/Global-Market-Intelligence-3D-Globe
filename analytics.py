import pandas as pd
import numpy as np
import os


def run_analytics(csv_file):
    try:
        df = pd.read_csv(csv_file, index_col=0, parse_dates=True)
    except FileNotFoundError:
        print(f"CRITICAL: {csv_file} not found. Run pipeline.py first")
        return pd.DataFrame()

    results = {}
    cities = [col.replace("_Price", "") for col in df.columns if col.endswith("_Price")]
    print(f"The cities found in the database: {', '.join(cities)}\n")

    for city in cities:
        print(f"Analyzing {city}...")

        # 1. Calculate Daily Log Returns
        # Formula: ln(Price_today / Price_yesterday)
        df[f'{city}_Ret'] = np.log(df[f'{city}_Price'] / df[f'{city}_Price'].shift(1))

        # 2. Annualized Return (Average daily return * 252 days)
        ann_return = df[f'{city}_Ret'].mean() * 252

        # 3. Annualized Volatility (Std Dev of daily returns * sqrt(252))
        ann_vol = df[f'{city}_Ret'].std() * np.sqrt(252)

        # 4. Get the most recent Risk-Free Rate (Yield) from our data
        # We divide by 100 because FRED yields are in percent
        risk_free_rate = df[f'{city}_Yield'].dropna().iloc[-1] / 100

        # 5. The Sharpe Ratio
        sharpe = (ann_return - risk_free_rate) / ann_vol

        results[city] = {
            "Annual_Return": ann_return,
            "Volatility_Risk": ann_vol,
            "Sharpe_Ratio": sharpe,
            "Last_Price": df[f'{city}_Price'].iloc[-1] # Phase 3 will load this
        }

    report = pd.DataFrame(results).T.sort_values(by="Sharpe_Ratio", ascending=False)
    return report


if __name__ == "__main__":
    try:
        report = run_analytics("master_market_data.csv")
        if not report.empty:
            print("\n--- Global Market Ranking (formatted for view) ---")
            display_df = report.copy()
            display_df['Annual_Return'] = display_df['Annual_Return'].apply(lambda x: f"{x:.2%}")
            display_df['Volatility_Risk'] = display_df['Volatility_Risk'].apply(lambda x: f"{x:.2%}")
            print(display_df)

            # Saving to a .csv file for predictions
            filename = "market_insight.csv"
            report.to_csv(filename)
            # Check if file exists to confirm success
            if os.path.exists(filename):
                print(f"SUCCESS: Data saved to {filename}")
            else:
                print("ERROR: CSV function finished but file not found.")
    except Exception as e:
        print(f"Unexpected error occurred during analysis: {e}")