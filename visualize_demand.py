import duckdb
import matplotlib.pyplot as plt
from pathlib import Path

# 1. File paths
input_path = "data/processed/hourly_demand_complete_2025-01.parquet"
output_path = "charts/hourly_demand.png"

# 2. Create charts folder
Path("charts").mkdir(exist_ok=True)

# 3. Calculate average hourly demand
print("=== Average Hourly Taxi Demand ===")

df = duckdb.sql(f"""
    SELECT
        EXTRACT(HOUR FROM pickup_hour) AS hour,
        ROUND(SUM(pickup_count) / 31.0, 1) AS avg_pickups
    FROM read_parquet('{input_path}')
    GROUP BY hour
    ORDER BY hour
""").df()

print(df)

# 4. Create line chart
plt.figure(figsize=(10, 5))

plt.plot(
    df["hour"],
    df["avg_pickups"],
    marker="o"
)

plt.title("NYC Taxi Demand by Hour - January 2025")
plt.xlabel("Hour of Day")
plt.ylabel("Average Pickups per Day")

plt.xticks(range(0, 24, 2))
plt.grid(alpha=0.3)
plt.tight_layout()

# 5. Save and display chart
plt.savefig(output_path, dpi=150)
plt.show()

print("Chart saved successfully!")
