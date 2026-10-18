import duckdb

# 1. File paths
input_path = "data/processed/hourly_demand_2025-01.parquet"
output_path = "data/processed/hourly_demand_complete_2025-01.parquet"

# 2. Create complete hourly dataset
print("=== Completing Hourly Demand Dataset ===")

duckdb.sql(f"""
    COPY (
        WITH zones AS (
            SELECT DISTINCT
                pickup_location_id,
                borough,
                pickup_zone
            FROM read_parquet('{input_path}')
        ),
        hours AS (
            SELECT pickup_hour
            FROM generate_series(
                TIMESTAMP '2025-01-01 00:00:00',
                TIMESTAMP '2025-01-31 23:00:00',
                INTERVAL 1 HOUR
            ) AS h(pickup_hour)
        )
        SELECT
            h.pickup_hour,
            z.pickup_location_id,
            z.borough,
            z.pickup_zone,
            COALESCE(t.pickup_count, 0) AS pickup_count
        FROM zones AS z
        CROSS JOIN hours AS h
        LEFT JOIN read_parquet('{input_path}') AS t
            ON z.pickup_location_id = t.pickup_location_id
           AND h.pickup_hour = t.pickup_hour
    )
    TO '{output_path}'
    (FORMAT PARQUET)
""")

# 3. Verify completed dataset
print("=== Complete Hourly Demand Summary ===")

duckdb.sql(f"""
    SELECT
        COUNT(*) AS total_rows,
        SUM(pickup_count) AS total_pickups,
        COUNT(*) FILTER (
            WHERE pickup_count = 0
        ) AS zero_demand_rows,
        COUNT(DISTINCT pickup_hour) AS total_hours,
        COUNT(DISTINCT pickup_location_id) AS active_zones
    FROM read_parquet('{output_path}')
""").show()
