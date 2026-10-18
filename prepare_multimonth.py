import duckdb
from pathlib import Path

# 1. Output path
output_path = "data/processed/taxi_pickups_2025_Q1.parquet"

Path("data/processed").mkdir(exist_ok=True)

# 2. Combine and clean January, February, March
print("=== Combining 3 Months of Taxi Data ===")

duckdb.sql(f"""
    COPY (
        SELECT
            t.tpep_pickup_datetime AS pickup_datetime,
            t.PULocationID AS pickup_location_id,
            z.Borough AS borough,
            z.Zone AS pickup_zone

        FROM read_parquet(
            [
                'data/raw/yellow_tripdata_2025-01.parquet',
                'data/raw/yellow_tripdata_2025-02.parquet',
                'data/raw/yellow_tripdata_2025-03.parquet'
            ],
            union_by_name = true
        ) AS t

        INNER JOIN read_csv_auto(
            'data/lookup/taxi_zone_lookup.csv'
        ) AS z
            ON t.PULocationID = z.LocationID

        WHERE t.tpep_pickup_datetime >= '2025-01-01'
          AND t.tpep_pickup_datetime < '2025-04-01'
          AND z.Borough IS NOT NULL
          AND z.Zone IS NOT NULL
          AND z.Borough <> 'Unknown'
          AND z.Zone <> 'Unknown'
    )
    TO '{output_path}'
    (FORMAT PARQUET)
""")

# 3. Verify trips for each month
print("=== Monthly Trip Summary ===")

duckdb.sql(f"""
    SELECT
        STRFTIME(pickup_datetime, '%Y-%m') AS month,
        COUNT(*) AS total_trips,
        COUNT(DISTINCT pickup_location_id) AS active_zones
    FROM read_parquet('{output_path}')
    GROUP BY month
    ORDER BY month
""").show()

# 4. Verify total
print("=== Total Q1 Trips ===")

duckdb.sql(f"""
    SELECT COUNT(*) AS total_clean_trips
    FROM read_parquet('{output_path}')
""").show()

print("=== Multi-Month Cleaning Complete ===")
