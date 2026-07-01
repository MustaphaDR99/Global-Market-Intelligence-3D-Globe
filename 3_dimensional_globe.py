"""
Reads the pipeline's csv outputs, builds the JS data constants,
and injects them into the HTML template to produce global_market_globe.html.

Called by main.py after analytics.py and predictions.py have run.
No external dependencies beyond what's already in requirements.txt.
"""


import pandas as pd
import numpy as np
import json
import os
import re

# Mapping cities as they appear in market_insight.csv to display info
# Add a new entry here whenever there's a market added to MARKET_CONFIG in pipeline.py
CITY_MAP = {
    "New_York":  {"index": "S&P 500",    "ticker": "^GSPC",  "currency": "$"},
    "London":    {"index": "FTSE 100",   "ticker": "^FTSE",  "currency": "£"},
    "Frankfurt": {"index": "DAX",        "ticker": "^GDAXI", "currency": "€"},
    "Tokyo":     {"index": "Nikkei 225", "ticker": "^N225",  "currency": "¥"},
    "Paris":     {"index": "CAC 40",     "ticker": "^FCHI",  "currency": "€"},
}

def load_analytics(path="market_insight.csv") -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"'{path}' not found. Run analytics.py first or main.py."
        )
    return pd.read_csv(path, index_col=0)

def load_predictions(path="market_predictions.xlsx") -> tuple[dict, dict]:
    """
    New function that returns from loading phase 3 (predictions):
        mc_summary - which is the dict of Monte Carlo results for the top market
        arima_info - which is the dict with last ARIMA forecast price and horizon
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"'{path}' not found. Run predictions.py first or main.py."
        )

    mc_df = pd.read_excel(path, sheet_name="Monte_Carlo_Summary")
    arima_df = pd.read_excel(path, sheet_name="ARIMA_Forecast", index_col=0)

    # Monte Carlo sheet has two columns: Metric and Value
    # Converting it to a dict keyed by Metric for easy lookup
    mc_dict = dict(zip(mc_df["Metric"], mc_df["Value"]))

    arima_info = {
        "startForecast": float(arima_df.iloc[0, 0]),
        "endForecast": float(arima_df.iloc[-1, 0]),
        "days": len(arima_df),
    }

    mc_summary = {
        "startPrice": float(mc_dict.get("Starting Price", 0)),
        "expectedPrice": float(mc_dict.get("Expected Mean Price", 0)),
        "worstCase": float(mc_dict.get("Worst Case (5th Pct)", 0)),
        "bestCase": float(mc_dict.get("Best Case (95th Pct)", 0)),
        "probProfit": float(mc_dict.get("Probability of Profit", 0)),
    }

    return mc_summary, arima_info

def load_coordinates(path="city_coordinates.json") -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"'{path}' not found. Run geo_utils.get_coordinates() first"
        )
    with open(path) as f:
        return json.load(f)

def build_market_data(analytics: pd.DataFrame, coords: dict, master_csv="master_market_data.csv")
    """
    New function that converts the analytics DataFrame into the JavaScript MARKET_DATA array literal.
    We determin whether the last price is above or below the 20-day moving average.
    Falls back to 'UP' if master data isn't available.
    """
    trend_map = {}
    if os.path.exists(master_csv):
        try:
            df_master = pd.read_csv(master_csv, index_col=0, parese_dates=True)
            for city in analytics.index:
                col = f"{city}_Price"
                if col in df_master.columns:
                    prices = df_master[col].dropna()
                    ma20 = prices.rolling(20).mean().iloc[-1]
                    last = prices.iloc[-1]
                    trend_map[city] = "UP" if last > ma20 else "DOWN"

        except Exception as e:
            print(f" Warning: could not compute trend signals - {e}")
    entries = []
    for city in analytics.index:
        row = analytics.loc[city]
        meta = CITY_MAP.get(city, {"index": city, "ticker": "N/A", "currency": "$"})
        coord = coords.get(city, {})
        trend = trend_map.get(city, "UP")

        # Round to 4dp for cleanliness; prices keep 2dp
        entry = (
            "  {\n"
            f'    city:         "{city}",\n'
            f'    index:        "{meta["index"]}",\n'
            f'    ticker:       "{meta["ticker"]}",\n'
            f'    currency:     "{meta["currency"]}",\n'
            f'    lat:          {coord.get("lat", 0):.4f},\n'
            f'    lon:          {coord.get("lon", 0):.4f},\n'
            f'    lastPrice:    {row["Last_Price"]:.2f},\n'
            f'    annReturn:    {row["Annual_Return"]:.4f},\n'
            f'    volatility:   {row["Volatility_Risk"]:.4f},\n'
            f'    sharpe:       {row["Sharpe_Ratio"]:.4f},\n'
            f'    trend:        "{trend}"\n'
            "  }"
        )
        entries.append(entry)

    return "const MARKET_DATA = [\n" + ",\n".join(entries) + "\n];"

def build_mc_summary(top_city: str, mc: dict) -> str
    return (
        "const MC_SUMMARY = {\n"
        f'  city:           "{top_city}",\n'
        f'  startPrice:     {mc["startPrice"]:.2f},\n'
        f'  expectedPrice:  {mc["expectedPrice"]:.2f},\n'
        f'  worstCase:      {mc["worstCase"]:.2f},\n'
        f'  bestCase:       {mc["bestCase"]:.2f},\n'
        f'  probProfit:     {mc["probProfit"]:.4f}\n'
        "};"
    )

def build_arima(arima: dict) -> str
    return (
        "const ARIMA = {\n"
        f' startForecast: {arima["startForecast"]:.2f},\n'
        f'  endForecast:    {arima["endForecast"]:.2f},\n'
        f'  days:           {arima["days"]}\n'
        "};"
    )

def build_globe()

if __name__ == "__main__":
    build_globe()