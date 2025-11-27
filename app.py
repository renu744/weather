import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests
import os

st.set_page_config(page_title="Weather Data Insights", layout="wide")

# ==========================
# Load Dataset Safely
# ==========================
@st.cache_data
def load_data():
    file_path = "data/weather.csv"   # <-- your CSV location

    # Check if file exists
    if not os.path.exists(file_path):
        st.error(f"❌ File not found: {file_path}")
        st.info("Make sure your folder structure looks like:\n\n"
                "weather/\n"
                "   app.py\n"
                "   data/\n"
                "       weather.csv")
        st.stop()

    df = pd.read_csv(file_path, parse_dates=["date"])
    df = df.sort_values("date")
    return df


# Load dataset
df = load_data()

# ==========================
# Sidebar Controls
# ==========================
st.sidebar.title("Weather Controls")

metric = st.sidebar.selectbox(
    "Select Metric for Analysis",
    ["temp_max", "temp_min", "precipitation", "humidity", "wind_speed"]
)

show_anomalies = st.sidebar.checkbox("Show Anomalies", value=False)

city = st.sidebar.text_input("City for Live Weather", "Delhi")

# ==========================
# App Header
# ==========================
st.title("🌤️ Weather Data Insights Dashboard")
st.caption("Analyze historical weather trends, seasonality, anomalies, and live conditions.")

# ==========================
# Time Series Trend
# ==========================
st.subheader(f"📈 {metric.upper()} Over Time")

fig = px.line(df, x="date", y=metric, title=f"{metric} Trend")
st.plotly_chart(fig, use_container_width=True)

# ==========================
# Anomaly Detection
# ==========================
if show_anomalies:
    st.subheader("🚨 Anomaly Detection (Z-score > 2)")

    df["zscore"] = (df[metric] - df[metric].mean()) / df[metric].std()
    df_anom = df[df["zscore"].abs() > 2]

    if df_anom.empty:
        st.success("No anomalies detected!")
    else:
        fig2 = px.scatter(
            df_anom,
            x="date",
            y=metric,
            color="zscore",
            color_continuous_scale="Turbo",
            title="Detected Anomalies"
        )
        st.plotly_chart(fig2, use_container_width=True)

# ==========================
# Seasonality Analysis
# ==========================
st.subheader("📆 Monthly Seasonality")

df["month"] = df["date"].dt.month_name()

seasonal = df.groupby("month")[metric].mean().reset_index()

fig3 = px.bar(seasonal, x="month", y=metric, title="Average by Month")
st.plotly_chart(fig3, use_container_width=True)

# ==========================
# Live Weather Section
# ==========================
st.subheader(f"📡 Live Weather in {city}")

API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"  # <-- Replace

if API_KEY == "YOUR_OPENWEATHERMAP_API_KEY":
    st.warning("⚠️ Please add your OpenWeatherMap API key in the code to enable live weather.")
else:
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"

    try:
        response = requests.get(url).json()

        if response.get("cod") != 200:
            st.error("Invalid city name or API error.")
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Temperature", f"{response['main']['temp']}°C")
            col2.metric("Humidity", f"{response['main']['humidity']}%")
            col3.metric("Wind", f"{response['wind']['speed']} m/s")

    except Exception as e:
        st.error(f"Error fetching live weather: {e}")
