import duckdb

# 1. Input and output files
input_path = "data/processed/taxi_pickups_2025-01.parquet"
output_path = "data/processed/hourly_demand_2025-01.parquet"

# 2. Aggregate trips by hour and zone
print("=== Creating Hourly Demand Dataset ===")

duckdb.sql(f"""
    COPY (
        SELECT
            DATE_TRUNC('hour', pickup_datetime) AS pickup_hour,
            pickup_location_id,
            borough,
            pickup_zone,
            COUNT(*) AS pickup_count
        FROM read_parquet('{input_path}')
        GROUP BY
            pickup_hour,
            pickup_location_id,
            borough,
            pickup_zone
    )
    TO '{output_path}'
    (FORMAT PARQUET)
""")

# 3. Verify the result
print("=== Hourly Demand Summary ===")

duckdb.sql(f"""
    SELECT
        COUNT(*) AS total_rows,
        SUM(pickup_count) AS total_pickups,
        COUNT(DISTINCT pickup_location_id) AS active_zones
    FROM read_parquet('{output_path}')
""").show()

# 4. Preview the first five rows
print("=== Sample Hourly Demand ===")

duckdb.sql(f"""
    SELECT *
    FROM read_parquet('{output_path}')
    ORDER BY pickup_hour, pickup_location_id
    LIMIT 5
""").show()