import duckdb

# 1. File paths
input_path = "data/processed/hourly_demand_complete_2025_Q1.parquet"
output_path = "data/processed/ml_features_2025_Q1.parquet"

# 2. Create machine learning features
print("=== Creating ML Features ===")

duckdb.sql(f"""
    COPY (
        SELECT
            pickup_hour,
            pickup_location_id,
            borough,
            pickup_zone,
            pickup_count,

            -- Time features
            EXTRACT(HOUR FROM pickup_hour) AS hour,
            EXTRACT(DOW FROM pickup_hour) AS day_of_week,

            -- Historical demand features
            LAG(pickup_count, 1) OVER (
                PARTITION BY pickup_location_id
                ORDER BY pickup_hour
            ) AS lag_1h,

            LAG(pickup_count, 24) OVER (
                PARTITION BY pickup_location_id
                ORDER BY pickup_hour
            ) AS lag_24h,

            LAG(pickup_count, 168) OVER (
                PARTITION BY pickup_location_id
                ORDER BY pickup_hour
            ) AS lag_168h

        FROM read_parquet('{input_path}')
    )
    TO '{output_path}'
    (FORMAT PARQUET)
""")

# 3. Verify feature dataset
print("=== ML Feature Summary ===")

duckdb.sql(f"""
    SELECT
        COUNT(*) AS total_rows,
        COUNT(*) FILTER (
            WHERE lag_1h IS NULL
        ) AS missing_lag_1h,
        COUNT(*) FILTER (
            WHERE lag_24h IS NULL
        ) AS missing_lag_24h,
        COUNT(*) FILTER (
            WHERE lag_168h IS NULL
        ) AS missing_lag_168h
    FROM read_parquet('{output_path}')
""").show()

print("=== ML Feature Creation Complete ===")