import pandas as pd
import numpy as np
import plotly.graph_objects as go
from geo_utils import get_coordinates

# Mapping cities to their respective currency symbols
CURRENCY_MAP = {
    "New_York": "$",
    "London": "£",
    "Frankfurt": "€",
    "Paris": "€",
    "Tokyo": "¥"
}


def build_globe():
    try:
        # Load Data
        analytics = pd.read_csv("market_insight.csv", index_col=0)
        mc_summary = pd.read_excel("market_predictions.xlsx", sheet_name="Monte_Carlo_Summary")
        arima_df = pd.read_excel("market_predictions.xlsx", sheet_name="ARIMA_Forecast", index_col=0)

        city_names = list(analytics.index)
        coords = get_coordinates(city_names)
        best_city = analytics.index[0]

        # I use .loc with a boolean mask to find the profit probability safely
        prob_profit = mc_summary.loc[mc_summary['Metric'] == "Probability of Profit", "Value"].values[0]
        trend = "UP" if arima_df.iloc[-1, 0] > arima_df.iloc[0, 0] else "DOWN"
    except Exception as e:
        print(f"Data Loading Error: {e}")
        return

    # Animation Parameters
    n_frames = 250
    rotation_steps = np.linspace(0, 360, n_frames)
    pulse_sizes = [18 + 6 * np.sin(x) for x in np.linspace(0, 6 * np.pi, n_frames)]

    fig = go.Figure()

    # Trace 0: Starfield
    fig.add_trace(go.Scattergeo(
        lon=np.random.uniform(-180, 180, 300),
        lat=np.random.uniform(-90, 90, 300),
        mode='markers',
        marker=dict(size=1, color="white", opacity=0.3),
        hoverinfo='skip'
    ))

    # Add city markets with currency symbols from the map
    for city in analytics.index:
        if city in coords:
            lat, lon = coords[city]['lat'], coords[city]['lon']
            stats = analytics.loc[city]
            currency = CURRENCY_MAP.get(city, "$") # Put '$' if there is no currency
            color = 'lime' if stats['Sharpe_Ratio'] > 0.4 else 'gold' if stats['Sharpe_Ratio'] > 0.2 else 'crimson'

            if city == best_city:
                hover_label = (
                    f"<b>{city} (Top Market)</b><br>"
                    f"Last Price: {currency}{stats['Last_Price']:,.2f}<br>"
                    f"Volatility: {stats['Volatility_Risk']:.2%}<br>"
                    f"Trend: {trend}<br>"
                    f"Prob. of Profit: {prob_profit:.2%}"
                )
            else:
                hover_label = (
                    f"<b>{city}</b><br>"
                    f"Last Price: {currency}{stats['Last_Price']:,.2f}<br>"
                    f"Sharpe: {stats['Sharpe_Ratio']:.3f}"
                )

            fig.add_trace(go.Scattergeo(
                lat=[lat], lon=[lon],
                mode='markers',
                marker=dict(size=15, color=color, line=dict(width=1, color='white')),
                text=hover_label,
                hoverinfo='text',
                name=city
            ))

    # Build Animation Frames
    frames = []
    for i in range(n_frames):
        frame_data = [go.Scattergeo(marker=dict(size=float(pulse_sizes[i])))]

        for city_idx, city in enumerate(analytics.index):
            if city in coords:
                # All cities pulsate; the top market pulses more intensely
                size = pulse_sizes[i] if city == best_city else (10 + 3 * np.sin(i * 0.5))
                frame_data.append(go.Scattergeo(
                    lat=[coords[city]['lat']], lon=[coords[city]['lon']],
                    marker=dict(size=float(size))
                ))

        frames.append(go.Frame(
            data=frame_data,
            layout=dict(geo=dict(projection_rotation_lon=rotation_steps[i])),
            name=f"frame{i}",
            traces=[city_names.index(best_city) + 1]
        ))

    fig.frames = frames

    # Layout with hidden Play button (for auto-start) and Pause/Resume toggle
    fig.update_layout(
        paper_bgcolor="black", width=900, height=900,
        margin=dict(l=0, r=0, t=0, b=0),
        geo=dict(
            projection_type="orthographic", bgcolor="black",
            showland=True, landcolor="#111", showcountries=True, countrycolor="#333",
            projection_scale=0.8
        ),
        updatemenus=[dict(
            type="buttons", showactive=False, visible=False,
            buttons=[
                # Hidden button triggered by JavaScript injection
                dict(label="Play", method="animate", visible=False,
                     args=[None, dict(frame=dict(duration=30, redraw=True),
                                      transition=dict(duration=0),
                                      fromcurrent=True, loop=True)])
            ]
        )]
    )

    # This is the JavaScript injection
    # Auto-click Play on launch
    post_script = """
    var checkExist = setInterval(function() {
       var playBtn = document.querySelector('.updatemenu-button');
       if (playBtn) {
          playBtn.click();
          clearInterval(checkExist);
       }
    }, 100);
    """

    fig.write_html("global_market_global.html", post_script=post_script)
    print("SUCCESS: Globe generated with stock index prices and currencies.")


if __name__ == "__main__":
    build_globe()