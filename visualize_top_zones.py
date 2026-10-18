import duckdb
import matplotlib.pyplot as plt
from pathlib import Path

# 1. File paths
input_path = "data/processed/hourly_demand_complete_2025-01.parquet"
output_path = "charts/top_10_pickup_zones.png"

Path("charts").mkdir(exist_ok=True)

# 2. Find top 10 pickup zones
df = duckdb.sql(f"""
    SELECT
        pickup_zone,
        borough,
        SUM(pickup_count) AS total_pickups
    FROM read_parquet('{input_path}')
    GROUP BY pickup_location_id, pickup_zone, borough
    ORDER BY total_pickups DESC
    LIMIT 10
""").df()

print("=== Top 10 Pickup Zones ===")
print(df)

# 3. Create horizontal bar chart
plt.figure(figsize=(11, 6))

plt.barh(
    df["pickup_zone"],
    df["total_pickups"]
)

plt.gca().invert_yaxis()

plt.title("Top 10 NYC Taxi Pickup Zones - January 2025")
plt.xlabel("Total Pickups")
plt.ylabel("Pickup Zone")

plt.tight_layout()

# 4. Save chart
plt.savefig(output_path, dpi=150)
plt.close()

print("Chart saved successfully!")