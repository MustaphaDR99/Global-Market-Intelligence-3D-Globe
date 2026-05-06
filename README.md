# Global Market Intelligence Globe 🌍📈

This project runs an automated Python pipeline that ingests global market data, runs quantitative risk-reward analytics, performs predictive forecasting, and visualizes the results on a cinematic, interactive 3D globe.

## 🚀 Key Features
*   **Automated Data Ingestion**: Fetches real-time price data for major global stock market indices and macroeconomic indicators from 5 years to now (Yields, CPI) via Yahoo Finance and FRED.
*   **Quantitative Analytics**: Calculates annualized returns, volatility, and **Sharpe Ratios** to rank markets by risk-adjusted performance.
*   **Predictive Modeling**:
    *   **ARIMA**: Statistical baseline trend forecasting.
    *   **Monte Carlo**: 10,000-simulation Geometric Brownian Motion to determine the probability of profit.
*   **Cinematic 3D Visualization**: A high-performance Plotly globe that auto-rotates on launch, featuring "heartbeat" undulations for top-performing markets and localized currency support.

## 🛠️ Project Structure
*   `pipeline_2.py`: The data engine. Synchronizes global market index prices with macroeconomic data.
*   `analytics.py`: The quant engine. Performs the Sharpe Ratio rankings and risk assessments.
*   `predictions.py`: The forecasting engine. Runs the ARIMA and Monte Carlo simulations.
*   `3_dimensional_globe.py`: The visualization engine. Generates the interactive, high-FPS 3D HTML dashboard.
*   `geo_utils.py`: Utility script for geocoding city coordinates with local JSON caching.
*   `main_2.py`: The orchestrator that executes the entire pipeline in sequence.

## 📊 Data & Markets Tracked
The project tracks the following primary stock market indices to gauge the health of global financial hubs:
*   **New York**: S&P 500 (`^GSPC`)
*   **London**: FTSE 100 (`^FTSE`)
*   **Tokyo**: Nikkei 225 (`^N225`)
*   **Frankfurt**: DAX (`^GDAXI`)
*   **Paris**: CAC 40 (`^FCHI`)

## ⚙️ Installation & Usage

### 1. Clone the Repository
```bash
git clone https://github.com/MustaphaDR99/Global-Market-Intelligence-3D-Globe
cd GlobalMarketIntelligenceGlobe
```
### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
### 3. Run the Pipeline
```bash
python main.py
```
