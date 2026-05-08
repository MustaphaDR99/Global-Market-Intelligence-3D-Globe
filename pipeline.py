import yfinance as yf
import pandas as pd
import time
from fredapi import Fred
import os
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
FRED_API_KEY = os.getenv('FRED_API_KEY')
if not FRED_API_KEY:
    print("ERROR: No FRED_API_KEY found in .env file!")

fred = Fred(api_key=FRED_API_KEY)

# Defining the markets via Yahoo Finance Tickers
# Mapping markets to their specific local Tickers and FRED IDs
# CPI = Consumer Price Index (Inflation)
MARKET_CONFIG = {
    "New_York": {
        "ticker": "^GSPC",
        "yield_id": "GS10",           # US 10Y Treasury
        "cpi_id": "CPIAUCSL"          # US CPI
    },
    "London": {
        "ticker": "^FTSE",
        "yield_id": "IRLTLT01GBM156N", # UK 10Y Yield
        "cpi_id": "CPALTT01GBM657N"    # UK CPI
    },
    "Frankfurt": {
        "ticker": "^GDAXI",
        "yield_id": "IRLTLT01DEM156N", # Germany 10Y Yield
        "cpi_id": "CPALTT01DEM657N"    # Germany CPI
    },
    "Tokyo": {
        "ticker": "^N225",
        "yield_id": "IRLTLT01JPM156N", # Japan 10Y Yield
        "cpi_id": "JPNCPIALLMINMEI"    # Japan CPI
    },
    "Paris": {
        "ticker": "^FCHI",
        "yield_id": "IRLTLT01FRM156N", # France 10Y Yield
        "cpi_id": "CPALTT01FRM657N"    # France CPI
    }
}


def fetch_regional_data(config, period="5y"):
    """Fetches and merges all data for a specific market configuration."""
    print(f"--- Synchronizing Global Markets ({period}) ---")

    master_frames = []

    for city, ids in config.items():
        try:
            time.sleep(1)
            print(f"Processing: {city}...")

            # 1. Fetch Market Price (Daily)
            price_df = yf.Ticker(ids['ticker']).history(period=period)[['Close']]
            price_df.index = price_df.index.tz_localize(None)
            if price_df.empty:
                print(f"No price data found for {city}")
                continue
            price_df.columns = [f"{city}_Price"]

            # 2. Fetch Macro Data (Monthly)
            start_date = price_df.index.min().strftime('%Y-%m-%d')

            yield_series = fred.get_series(ids['yield_id'], observation_start=start_date)
            cpi_series = fred.get_series(ids['cpi_id'], observation_start=start_date)

            # Combine into one frame for this city
            city_df = price_df.copy()
            city_df[f"{city}_Yield"] = yield_series
            city_df[f"{city}_CPI"] = cpi_series

            # Monthly macroeconomic indicators are forward-filled to match daily financial data frequency
            city_df = city_df.ffill()
            master_frames.append(city_df)
            print(f"Retrivial successfull {city}")
        except Exception as e:
            print(f"Error fetching data for {city}: {e}")


    if not master_frames:
        print("CRITICAL: No data was collected")
        return pd.DataFrame()

    # Merge all cities into one massive Master Table
    final_df = pd.concat(master_frames, axis=1, sort=True)
    final_df = final_df.ffill().bfill() # Fill the gaps because of days' discrepancy between regions
    return final_df

if __name__ == "__main__":
    final_data = fetch_regional_data(MARKET_CONFIG)
    if not final_data.empty:
        print("\n--- Master Data Table View ---")
        print(final_data)
        print(f"\nTotal Rows Collected: {len(final_data)}")

        # Saving to a .csv file for calculation
        filename = "master_market_data.csv"
        try:
            final_data.to_csv(filename)
            # Check if file exists to confirm success
            if os.path.exists(filename):
                print(f"SUCCESS: Data saved to {filename}")
            else:
                print("ERROR: CSV function finished but file not found.")
        except Exception as e:
            print(f"Could not save to file: {e}")
    else:
        print("Pipeline ended with no data to save.")



