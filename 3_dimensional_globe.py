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

def build_market_data(analytics: pd.DataFrame, coords: dict, master_csv="master_market_data.csv"):
    """
    New function that converts the analytics DataFrame into the JavaScript MARKET_DATA array literal.
    We determin whether the last price is above or below the 20-day moving average.
    Falls back to 'UP' if master data isn't available.
    """
    trend_map = {}
    if os.path.exists(master_csv):
        try:
            df_master = pd.read_csv(master_csv, index_col=0, parse_dates=True)
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
    for city in analytics.index:          # already sorted by Sharpe descending
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

def build_mc_summary(top_city: str, mc: dict) -> str:
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

def build_arima(arima: dict) -> str:
    return (
        "const ARIMA = {\n"
        f' startForecast: {arima["startForecast"]:.2f},\n'
        f'  endForecast:    {arima["endForecast"]:.2f},\n'
        f'  days:           {arima["days"]}\n'
        "};"
    )

# New injection: HTML
# I add sentinel comments that will delimit the data block inside global_market_globe.html
BLOCK_START = "// SECTION 1 — MARKET DATA"
BLOCK_END   = "// SECTION 2 — THREE.JS SCENE SETUP"

def inject_into_template(
        template_path: str,
        market_data_js: str,
        mc_summary_js: str,
        arima_js: str,
        output_path: str = "global_market_globe.html",
) -> None:
    """
    This function will read the HTML template, finds the data block between the two sentinel
    comments, replaces the JavaScript constants with live values, and writes the result to the output variable.
    """
    with open(template_path, encoding="utf-8") as f:
        html = f.read()

    # IMPORTANT:
    # We keep the sentinel comments so subsequent runs can find the block again.
    new_block = (
        f"// {BLOCK_START.lstrip('// ')}\n"
        "// Auto-generated by 3_dimensional_globe.py — do not edit manually.\n"
        "// Re-run main.py to refresh with latest pipeline data.\n\n"
        f"{market_data_js}\n\n"
        f"{mc_summary_js}\n\n"
        f"{arima_js}\n\n"
        f"// {BLOCK_END.lstrip('// ')}"
    )

    pattern = re.compile(
        rf"// {re.escape(BLOCK_START.lstrip('// '))}.+?// {re.escape(BLOCK_END.lstrip('// '))}",
        re.DOTALL,
    )

    if not pattern.search(html):
        raise ValueError(
            "Could not find the data injection markers in the template.\n"
            f"Make sure '{template_path}' contains both:\n"
            f"  '{BLOCK_START}'\n"
            f"  '{BLOCK_END}'"
        )

    updated_html = pattern.sub(new_block, html)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(updated_html)

    print(f"SUCCESS: Globe written to '{output_path}'")

def build_globe(
        template_path: str = "global_market_globe.html",
        output_path: str = "global_market_globe.html",
) -> None:
    """
    Still miming v.1 function but build sequence is as follows:
    1. Load analytics csv file
    2. Load Monte Carlo / ARIMA predictions
    3.Load city coordinates (.json file)
    4. Build JS constant strings
    5. Inject into HTML template -> write output
    """
    print("--- BUILDING THREE.JS GLOBE ---")

    # 1. Analytics
    print("  Loading market_insight.csv...")
    analytics = load_analytics("market_insight.csv")
    top_city = analytics.index[0]  # rank #1 by Sharpe
    print(f"  Top market: {top_city} (Sharpe {analytics.loc[top_city, 'Sharpe_Ratio']:.4f})")

    # 2. Predictions
    print("  Loading market_predictions.xlsx...")
    mc_summary, arima_info = load_predictions("market_predictions.xlsx")

    # 3. Coordinates
    print("  Loading city_coordinates.json...")
    coords = load_coordinates("city_coordinates.json")

    # 4. Build JS strings
    print("  Building JS constants...")
    market_js = build_market_data(analytics, coords)
    mc_js = build_mc_summary(top_city, mc_summary)
    arima_js = build_arima(arima_info)

    # 5. Inject and write
    print(f"  Injecting into '{template_path}'...")
    inject_into_template(template_path, market_js, mc_js, arima_js, output_path)

if __name__ == "__main__":
    build_globe()