import pandas as pd
import numpy as np
import os
import warnings
from statsmodels.tsa.arima.model import ARIMA

# From documentations, it is mentioned that ARIMA can be noisy when fitting raw stock data
warnings.filterwarnings("ignore")

def load_target_market():
    """Loads Phase 2 data and automatically selects the #1 ranked city."""
    df_insight = pd.read_csv("market_insight.csv", index_col=0)
    best_city = df_insight.index[0]
    stats = df_insight.loc[best_city]
    return best_city, stats


def run_arima(city, df_prices, days=30):
    """Runs an ARIMA model to find the statistical baseline trend."""
    print(f"--- Running ARIMA Model for {city} ({days} days) ---")

    # Isolate the historical prices for our target city
    prices = df_prices[f"{city}_Price"].dropna()

    # Fit a basic ARIMA(1, 1, 1) model
    # (1 autoregressive term, 1 difference to make it stationary, 1 moving average term)
    model = ARIMA(prices, order=(1, 1, 1))
    fitted_model = model.fit()

    # Forecast the next 'n' days
    forecast = fitted_model.forecast(steps=days)

    # Create future business dates for the index
    last_date = prices.index[-1]
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=days, freq='B')

    df_forecast = pd.DataFrame({"ARIMA_Forecast_Price": forecast.values}, index=future_dates)

    # Check the trend direction
    start_price = prices.iloc[-1]
    end_price = forecast.iloc[-1]
    trend = "UP" if end_price > start_price else "DOWN"
    print(f"ARIMA Trend Conclusion: {trend} (From {start_price:.2f} to {end_price:.2f})\n")

    return df_forecast


def run_monte_carlo(city, stats, days=30, sims=10000):
    """Runs 10,000 Geometric Brownian Motion simulations."""
    print(f"--- Running Monte Carlo for {city} ({sims} simulations) ---")

    S0 = stats['Last_Price']
    # Convert annual stats back to daily for the simulation steps
    mu_daily = stats['Annual_Return'] / 252
    sigma_daily = stats['Volatility_Risk'] / np.sqrt(252)

    # Setup the simulation grid: 30 days rows, 10,000 simulation columns
    prices = np.zeros((days, sims))
    prices[0] = S0

    # Loop through each day and apply the Geometric Brownian Motion formula
    for t in range(1, days):
        # Generate random 'shocks' from a standard normal distribution
        Z = np.random.standard_normal(sims)
        # Calculate the next day's price for all 10,000 universes at once
        prices[t] = prices[t - 1] * np.exp((mu_daily - 0.5 * sigma_daily ** 2) + sigma_daily * Z)

    # Analyze the final day across all 10,000 simulations
    final_prices = prices[-1]
    prob_profit = np.mean(final_prices > S0)
    expected_price = np.mean(final_prices)
    worst_case = np.percentile(final_prices, 5)  # Bottom 5%
    best_case = np.percentile(final_prices, 95)  # Top 5%

    print(f"Monte Carlo Probability of Profit: {prob_profit:.2%}")
    print(f"Expected Mean Price: {expected_price:.2f}")
    print(f"Worst-Case Scenario (5%): {worst_case:.2f}")
    print(f"Best-Case Scenario (95%): {best_case:.2f}\n")

    # A summary DataFrame to save
    df_mc_summary = pd.DataFrame({
        "Metric": ["Starting Price", "Expected Mean Price", "Worst Case (5th Pct)", "Best Case (95th Pct)",
                   "Probability of Profit"],
        "Value": [S0, expected_price, worst_case, best_case, prob_profit]
    })

    return df_mc_summary


if __name__ == "__main__":
    try:
        target_city, target_stats = load_target_market()
        print(f"Prediction on target Market: {target_city} (Ranked #1)\n")
        df_master = pd.read_csv("master_market_data.csv", index_col=0, parse_dates=True)

        df_arima = run_arima(target_city, df_master)
        df_mc = run_monte_carlo(target_city, target_stats)


        filename = "market_predictions.xlsx"
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df_arima.to_excel(writer, sheet_name="ARIMA_Forecast")
            df_mc.to_excel(writer, sheet_name="Monte_Carlo_Summary", index=False)

        if os.path.exists(filename):
            print(
                f"SUCCESS: Predictive data saved to {filename} to sheets: ARIMA_Forecast, Monte_Carlo_Summary)")

    except Exception as e:
        print(f"CRITICAL ERROR in Prediction Pipeline: {e}")