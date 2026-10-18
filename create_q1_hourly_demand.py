import duckdb

# 1. File paths
input_path = "data/processed/taxi_pickups_2025_Q1.parquet"
output_path = "data/processed/hourly_demand_complete_2025_Q1.parquet"

# 2. Create hourly demand dataset
print("=== Creating Q1 Hourly Demand Dataset ===")

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
                TIMESTAMP '2025-03-31 23:00:00',
                INTERVAL 1 HOUR
            ) AS h(pickup_hour)
        ),

        hourly_counts AS (
            SELECT
                DATE_TRUNC('hour', pickup_datetime)
                    AS pickup_hour,
                pickup_location_id,
                COUNT(*) AS pickup_count
            FROM read_parquet('{input_path}')
            GROUP BY pickup_hour, pickup_location_id
        )

        SELECT
            h.pickup_hour,
            z.pickup_location_id,
            z.borough,
            z.pickup_zone,
            COALESCE(c.pickup_count, 0) AS pickup_count

        FROM zones AS z
        CROSS JOIN hours AS h
        LEFT JOIN hourly_counts AS c
            ON z.pickup_location_id = c.pickup_location_id
           AND h.pickup_hour = c.pickup_hour
    )
    TO '{output_path}'
    (FORMAT PARQUET)
""")

# 3. Verify the result
print("=== Q1 Hourly Demand Summary ===")

duckdb.sql(f"""
    SELECT
        COUNT(*) AS total_rows,
        SUM(pickup_count) AS total_pickups,
        COUNT(DISTINCT pickup_hour) AS total_hours,
        COUNT(DISTINCT pickup_location_id) AS active_zones,
        COUNT(*) FILTER (
            WHERE pickup_count = 0
        ) AS zero_demand_rows
    FROM read_parquet('{output_path}')
""").show()

# 4. Check monthly totals
print("=== Monthly Demand Verification ===")

duckdb.sql(f"""
    SELECT
        STRFTIME(pickup_hour, '%Y-%m') AS month,
        SUM(pickup_count) AS total_pickups
    FROM read_parquet('{output_path}')
    GROUP BY month
    ORDER BY month
""").show()

print("=== Q1 Dataset Complete ===")
