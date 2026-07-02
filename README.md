# Global Market Intelligence Globe 🌍📈

This project is a full-stack quantitative finance pipeline that ingests live global market data, runs risk-adjusted analytics and predictive models, then renders the results on a **cinematic Three.js / WebGL 3D globe** — replacing the original Plotly visualisation with GPU-accelerated rendering at 60fps.

---

## ✨ What Changed (v2.0)

| | v1 (Plotly) | v2 (Three.js / WebGL) |
|---|---|---|
| Renderer | CPU-side SVG/Canvas | GPU — WebGL via Three.js |
| FPS | ~15–25, laggy on rotate | Locked 60fps |
| Globe quality | Flat projection illusion | True orthographic 3D sphere |
| Borders | None | Latitude/longitude graticule |
| Markers | Static scatter dots | Pulsing torus rings + spike + glow halo |
| Atmosphere | None | Layered rim glow + fog |
| Hover | Plotly tooltip | Raycasted HUD tooltip |
| Stars | Fake scatter on geo plane | 6,000-point 3D particle system |
| Aesthetic | Default Plotly dark | WarWatch-inspired dark-space terminal |

---

## 🚀 Key Features

- **Automated Data Ingestion** — Live 5-year price history for 5 global indices + macroeconomic indicators (yields, CPI) via Yahoo Finance and FRED API
- **Quantitative Analytics** — Annualised return, volatility, Sharpe ratio; markets ranked by risk-adjusted performance using local risk-free rates per currency
- **Predictive Modelling**
  - ARIMA(1,1,1) — 30-day statistical trend baseline
  - Monte Carlo — 10,000-simulation Geometric Brownian Motion with Itô correction; probability of profit, worst/best case
- **Three.js WebGL Globe**
  - True sphere with latitude/longitude graticule
  - Atmospheric rim glow + starfield particle system
  - Pulsing torus rings + vertical spikes per market, colour-coded by Sharpe ratio
  - Raycasted mouse-hover tooltips (no lag)
  - OrbitControls: drag to rotate, scroll to zoom, auto-spin when idle, pause on hover
  - Scanline CRT overlay + corner brackets HUD
  - Market cards + Monte Carlo / ARIMA prediction panel

---

## 🛠️ Project Structure

```
GlobalMarketIntelligenceGlobe/
├── main.py                    # Orchestrator: runs pipeline → opens server
├── pipeline.py                # Data engine: Yahoo Finance + FRED API → master_market_data.csv
├── analytics.py               # Quant engine: Sharpe ranking → market_insight.csv
├── predictions.py             # Forecast engine: ARIMA + Monte Carlo → market_predictions.xlsx
├── 3_dimensional_globe.py     # Globe builder: reads CSV/Excel → injects into global_market_globe.html
├── geo_utils.py               # Geocoding utility with local JSON cache
├── city_coordinates.json      # Cached lat/lon per market city
├── requirements.txt           # Python dependencies
├── .env.example               # FRED API key template
└── global_market_globe.html   # ← Generated output: Three.js WebGL globe (open in browser)
```

---

## 📊 Markets Tracked

| City | Index | Ticker | Currency |
|---|---|---|---|
| New York | S&P 500 | `^GSPC` | USD $ |
| London | FTSE 100 | `^FTSE` | GBP £ |
| Tokyo | Nikkei 225 | `^N225` | JPY ¥ |
| Frankfurt | DAX | `^GDAXI` | EUR € |
| Paris | CAC 40 | `^FCHI` | EUR € |

---

## ⚙️ Installation & Usage

### 1. Clone

```bash
git clone https://github.com/MustaphaDR99/Global-Market-Intelligence-3D-Globe
cd Global-Market-Intelligence-3D-Globe
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up FRED API key

```bash
cp .env.example .env
# Edit .env and add: FRED_API_KEY=your_key_here
# Free key at: https://fred.stlouisfed.org/docs/api/api_key.html
```

### 4. Run

```bash
python main.py
```

The pipeline runs all four stages sequentially and opens `http://127.0.0.1:8000/global_market_globe.html` automatically.

### 5. Controls

| Action | Result |
|---|---|
| Click + drag | Rotate globe |
| Scroll wheel | Zoom in/out |
| Hover a marker | Show market tooltip |
| Release mouse | Resume auto-rotation |

---

## 🔁 Pipeline Flow

```
pipeline.py         →  master_market_data.csv
    ↓ Yahoo Finance (5y daily OHLCV)
    ↓ FRED API (monthly yield + CPI, forward-filled)

analytics.py        →  market_insight.csv
    ↓ Log returns → annualised return + volatility
    ↓ Sharpe ratio using local risk-free rate per currency

predictions.py      →  market_predictions.xlsx
    ↓ ARIMA(1,1,1) — 30-day price forecast
    ↓ Monte Carlo GBM — 10,000 simulations → P(profit), E[price], VaR

3_dimensional_globe.py  →  global_market_globe.html
    ↓ Reads CSV/Excel outputs
    ↓ Injects market data as JS constants
    ↓ Renders Three.js WebGL globe
```

---

## 🎨 Visualisation — Technical Notes

The globe is rendered entirely in **WebGL via Three.js r128** — no more server required after generation. All rendering is GPU-side.

**Key Three.js concepts used:**
- `SphereGeometry` — globe mesh (64×64 segments)
- `LineSegments` + `BufferGeometry` — lat/lon graticule (typed Float32Array, zero GC)
- `TorusGeometry` — pulsing market rings, animated with `Math.sin(t)`
- `Points` + `BufferAttribute` — 6,000-star particle system
- `MeshPhongMaterial` — per-pixel lighting with specular highlights
- `AdditiveBlending` — glow/bloom halos without a post-processing pass
- `Raycaster` — GPU-accurate mouse hover detection
- `OrbitControls` — drag/zoom/auto-rotate with inertia damping
- `WebGLRenderer` — capped at `devicePixelRatio = 2` for retina performance

---

## 📦 Dependencies

### Python
```
yfinance>=0.2.28
pandas>=2.0.0
fredapi>=0.5.1
python-dotenv>=1.0.0
plotly>=5.17.0        # kept for legacy analytics output
numpy>=1.24.0
statsmodels>=0.14.0
geopy>=2.3.0
openpyxl>=3.1.0
```

### JavaScript (CDN — no install)
- [Three.js r128](https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js)
- [OrbitControls](https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js)

---

## Roadmap

- [ ] Wire `3_dimensional_globe.py` to inject live CSV/Excel data into `MARKET_DATA` JS constant at build time (currently hardcoded from last run)
- [ ] Add GLTF Earth texture (NASA Blue Marble) for photorealistic ocean/land
- [ ] Extend to 20+ markets (emerging markets: Mumbai, São Paulo, Seoul, Shanghai)
- [ ] Sortino ratio + CVaR columns in analytics
- [ ] WebSocket live price feed (no pipeline re-run needed)
