import duckdb
from pathlib import Path

# 1. File paths
file_path = "data/raw/yellow_tripdata_2025-01.parquet"
zone_path = "data/lookup/taxi_zone_lookup.csv"
output_path = "data/processed/taxi_pickups_2025-01.parquet"

# 2. Create output folder if needed
Path("data/processed").mkdir(parents=True, exist_ok=True)

# 3. Clean data and save as Parquet
print("=== Cleaning Taxi Data ===")

duckdb.sql(f"""
    COPY (
        SELECT
            t.tpep_pickup_datetime AS pickup_datetime,
            t.PULocationID AS pickup_location_id,
            z.Borough AS borough,
            z.Zone AS pickup_zone
        FROM read_parquet('{file_path}') AS t
        INNER JOIN read_csv_auto('{zone_path}') AS z
            ON t.PULocationID = z.LocationID
        WHERE t.tpep_pickup_datetime >= '2025-01-01'
          AND t.tpep_pickup_datetime < '2025-02-01'
          AND z.Borough IS NOT NULL
          AND z.Zone IS NOT NULL
          AND z.Borough <> 'Unknown'
          AND z.Zone <> 'Unknown'
    )
    TO '{output_path}'
    (FORMAT PARQUET)
""")

# 4. Verify cleaned data
print("=== Cleaned Data Summary ===")

duckdb.sql(f"""
    SELECT
        COUNT(*) AS total_clean_trips,
        COUNT(DISTINCT pickup_location_id) AS active_zones
    FROM read_parquet('{output_path}')
""").show()

print("=== Cleaning Complete ===")