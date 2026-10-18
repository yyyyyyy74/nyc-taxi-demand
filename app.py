import streamlit as st
import duckdb
import joblib
from datetime import date
from sklearn.metrics import mean_absolute_error, mean_squared_error

# 1. Page settings
st.set_page_config(
    page_title="NYC Taxi Intelligence",
    page_icon="🚕",
    layout="wide"
)

st.title("NYC Taxi Intelligence")
st.write("Explore NYC Yellow Taxi demand - January to March 2025")

# 2. Load cleaned data
@st.cache_data
def load_data():
    return duckdb.sql("""
        SELECT
            pickup_hour,
            pickup_location_id,
            borough,
            pickup_zone,
            pickup_count
        FROM read_parquet(
            'data/processed/hourly_demand_complete_2025_Q1.parquet'
        )
    """).df()

df = load_data()

# 3. Borough selector
boroughs = ["All"] + sorted(df["borough"].unique().tolist())

selected_borough = st.selectbox(
    "Select a Borough",
    boroughs
)

if selected_borough == "All":
    borough_df = df
else:
    borough_df = df[df["borough"] == selected_borough]

# 3.1 Taxi Zone selector
zones = (
    borough_df[["pickup_location_id", "pickup_zone"]]
    .drop_duplicates()
    .sort_values("pickup_zone")
)

zone_ids = zones["pickup_location_id"].tolist()

zone_names = dict(zip(
    zones["pickup_location_id"],
    zones["pickup_zone"]
))

selected_zone = st.selectbox(
    "Select a Taxi Zone",
    options=[None] + zone_ids,
    format_func=lambda zone_id: (
        "All Zones" if zone_id is None
        else f"{zone_names[zone_id]} (ID {zone_id})"
    )
)

# Filter data based on the selected zone
if selected_zone is None:
    filtered_df = borough_df
else:
    filtered_df = borough_df[
        borough_df["pickup_location_id"] == selected_zone
    ]

# 3.2 Date range selector
min_date = df["pickup_hour"].min().date()
max_date = df["pickup_hour"].max().date()

date_range = st.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Wait until both dates are selected
if len(date_range) != 2:
    st.info("Please select a start date and end date.")
    st.stop()

start_date, end_date = date_range

# Filter data by the selected dates
filtered_df = filtered_df[
    filtered_df["pickup_hour"].dt.date.between(start_date, end_date)
]

borough_df = borough_df[
    borough_df["pickup_hour"].dt.date.between(start_date, end_date)
]

# Count the selected days
num_days = (end_date - start_date).days + 1

# 4. Key metrics
total_pickups = int(filtered_df["pickup_count"].sum())
active_zones = filtered_df["pickup_location_id"].nunique()

col1, col2 = st.columns(2)

col1.metric("Total Pickups", f"{total_pickups:,}")
col2.metric("Active Zones", f"{active_zones:,}")

# 5. Average hourly demand
hourly_avg = (
    filtered_df
    .assign(hour=filtered_df["pickup_hour"].dt.hour)
    .groupby("hour")["pickup_count"]
    .sum()
    .reindex(range(24), fill_value=0)
    .div(num_days)
    .rename("Average Pickups")
    .reset_index()
)

# 6. Interactive line chart
st.subheader("Average Taxi Demand by Hour")

st.line_chart(
    hourly_avg,
    x="hour",
    y="Average Pickups"
)

# 6.1 Daily demand trend
st.subheader("Daily Taxi Demand Trend")

daily_trend = (
    filtered_df
    .assign(date=filtered_df["pickup_hour"].dt.normalize())
    .groupby("date", as_index=False)["pickup_count"]
    .sum()
    .rename(columns={"pickup_count": "Daily Pickups"})
)

st.line_chart(
    daily_trend,
    x="date",
    y="Daily Pickups"
)

# 7. Top 10 pickup zones
st.subheader("Top 10 Pickup Zones")

top_zones = (
    borough_df
    .groupby(["pickup_location_id", "pickup_zone"], as_index=False)["pickup_count"]
    .sum()
    .sort_values("pickup_count", ascending=False)
    .head(10)
)

st.bar_chart(
    top_zones,
    x="pickup_zone",
    y="pickup_count",
    horizontal=True
)

st.caption("Source: NYC TLC Yellow Taxi Trip Records")

# 8. Historical ML predictions
st.subheader("Machine Learning Demand Forecast - March 2025")

st.write(
    "Compare actual taxi demand with Random Forest "
    "one-hour-ahead predictions on historical test data."
)

@st.cache_resource
def load_model():
    return joblib.load("models/random_forest_q1_2025.joblib")

@st.cache_data
def load_march_data(zone_id):
    return duckdb.sql(f"""
        SELECT *
        FROM read_parquet(
            'data/processed/ml_features_2025_Q1.parquet'
        )
        WHERE pickup_location_id = {int(zone_id)}
          AND pickup_hour >= '2025-03-01'
          AND pickup_hour < '2025-04-01'
        ORDER BY pickup_hour
    """).df()

if selected_zone is None:
    st.info("Please select a specific Taxi Zone above.")
else:
    selected_day = st.date_input(
        "Select a March Backtest Date",
        value=date(2025, 3, 15),
        min_value=date(2025, 3, 1),
        max_value=date(2025, 3, 31)
    )

    march_df = load_march_data(selected_zone)

    day_df = march_df[
        march_df["pickup_hour"].dt.date == selected_day
    ].copy()

    features = [
        "pickup_location_id",
        "hour",
        "day_of_week",
        "lag_1h",
        "lag_24h",
        "lag_168h"
    ]

    model = load_model()

    predictions = model.predict(day_df[features])
    predictions = predictions.clip(min=0)

    comparison = day_df[
        ["pickup_hour", "pickup_count", "lag_168h"]
    ].copy()

    comparison["Random Forest"] = predictions

    comparison = comparison.rename(columns={
        "pickup_count": "Actual",
        "lag_168h": "Last Week Baseline"
    })

    # Calculate prediction errors for the selected day
    actual = comparison["Actual"]
    rf_pred = comparison["Random Forest"]
    baseline_pred = comparison["Last Week Baseline"]

    rf_mae = mean_absolute_error(actual, rf_pred)
    rf_rmse = mean_squared_error(actual, rf_pred) ** 0.5

    baseline_mae = mean_absolute_error(actual, baseline_pred)
    baseline_rmse = mean_squared_error(actual, baseline_pred) ** 0.5

    # Display evaluation metrics
    st.subheader("Prediction Accuracy")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Random Forest MAE", f"{rf_mae:.2f}")
    col2.metric("Random Forest RMSE", f"{rf_rmse:.2f}")

    col3.metric("Baseline MAE", f"{baseline_mae:.2f}")
    col4.metric("Baseline RMSE", f"{baseline_rmse:.2f}")

    st.line_chart(
        comparison,
        x="pickup_hour",
        y=["Actual", "Random Forest", "Last Week Baseline"]
    )

    st.caption(
        "Historical backtest: the model uses actual earlier "
        "pickup counts available before each predicted hour. "
        "It does not forecast future days all at once."
    )

