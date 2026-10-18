import duckdb
import matplotlib.pyplot as plt
from pathlib import Path

# 1. File paths
input_path = "data/processed/hourly_demand_complete_2025-01.parquet"
output_path = "charts/weekday_vs_weekend.png"

Path("charts").mkdir(exist_ok=True)

# 2. Calculate average demand by hour and day type
df = duckdb.sql(f"""
    WITH daily_hourly AS (
        SELECT
            CAST(pickup_hour AS DATE) AS trip_date,
            EXTRACT(HOUR FROM pickup_hour) AS hour,
            CASE
                WHEN EXTRACT(DOW FROM pickup_hour) IN (0, 6)
                THEN 'Weekend'
                ELSE 'Weekday'
            END AS day_type,
            SUM(pickup_count) AS daily_pickups
        FROM read_parquet('{input_path}')
        GROUP BY trip_date, hour, day_type
    )
    SELECT
        hour,
        day_type,
        ROUND(AVG(daily_pickups), 1) AS avg_pickups
    FROM daily_hourly
    GROUP BY hour, day_type
    ORDER BY hour, day_type
""").df()

print("=== Weekday vs Weekend Demand ===")
print(df)

# 3. Separate weekday and weekend data
weekday = df[df["day_type"] == "Weekday"]
weekend = df[df["day_type"] == "Weekend"]

# 4. Create line chart
plt.figure(figsize=(10, 5))

plt.plot(
    weekday["hour"],
    weekday["avg_pickups"],
    marker="o",
    label="Weekday"
)

plt.plot(
    weekend["hour"],
    weekend["avg_pickups"],
    marker="o",
    label="Weekend"
)

plt.title("NYC Taxi Demand: Weekday vs Weekend - January 2025")
plt.xlabel("Hour of Day")
plt.ylabel("Average Pickups per Day")

plt.xticks(range(0, 24, 2))
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

# 5. Save chart
plt.savefig(output_path, dpi=150)
plt.close()

print("Chart saved successfully!")
