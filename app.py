import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import requests

st.set_page_config(page_title="Weather Data Insights", layout="wide")

# ==========================
# Load Dataset
# ==========================
@st.cache_data
def load_data():
    df = pd.read_csv("data/weather.csv", parse_dates=["date"])
    df = df.sort_values("date")
    return df

df = load_data()

# ==========================
# Sidebar
# ==========================
st.sidebar.title("Weather Controls")

metric = st.sidebar.selectbox(
    "Select Metric", 
    ["temp_max", "temp_min", "precipitation", "humidity", "wind_speed"]
)

show_anomalies = st.sidebar.checkbox("Show Anomalies")
city = st.sidebar.text_input("City for Live Weather", "Delhi")

# ==========================
# Header
# ==========================
st.title("🌤️ Weather Data Insights Dashboard")
st.write("Analyze historical weather patterns, trends, anomalies & live conditions.")

# ==========================
# Trend Plot
# ==========================
st.subheader(f"{metric} Over Time")
fig = px.line(df, x="date", y=metric)
st.plotly_chart(fig, use_container_width=True)

# ==========================
# Anomaly Detection
# ==========================
if show_anomalies:
    st.subheader("Anomaly Detection")

    df["zscore"] = (df[metric] - df[metric].mean()) / df[metric].std()
    df_anom = df[df["zscore"].abs() > 2]

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
# Seasonality (Monthly Averages)
# ==========================
st.subheader("Monthly Seasonality")
df["month"] = df["date"].dt.month
seasonal = df.groupby("month")[metric].mean().reset_index()

fig3 = px.bar(seasonal, x="month", y=metric, title="Average by Month")
st.plotly_chart(fig3, use_container_width=True)

# ==========================
# Live Weather API
# ==========================
st.subheader(f"📡 Live Weather in {city}")

API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"
url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"

try:
    response = requests.get(url).json()
    col1, col2, col3 = st.columns(3)
    col1.metric("Temperature", f"{response['main']['temp']}°C")
    col2.metric("Humidity", f"{response['main']['humidity']}%")
    col3.metric("Wind", f"{response['wind']['speed']} m/s")
except:
    st.error("Invalid city name or API error")
