import duckdb

# 1. Path to our taxi dataset
file_path = "data/raw/yellow_tripdata_2025-01.parquet"
zone_path = "data/lookup/taxi_zone_lookup.csv"

# 2. Count total taxi trips
print("=== Total Trips ===")

duckdb.sql(f"""
    SELECT COUNT(*) AS total_trips
    FROM read_parquet('{file_path}')
""").show()

# 3. See the first five records
print("=== First 5 Trips ===")

duckdb.sql(f"""
    SELECT
        tpep_pickup_datetime,
        PULocationID,
        trip_distance,
        total_amount
    FROM read_parquet('{file_path}')
    LIMIT 5
""").show()

# 4. Analyze taxi demand by hour
print("=== Taxi Demand by Hour ===")

duckdb.sql(f"""
    SELECT
        EXTRACT(HOUR FROM tpep_pickup_datetime) AS hour,
        COUNT(*) AS total_trips
    FROM read_parquet('{file_path}')
    WHERE tpep_pickup_datetime >= '2025-01-01'
      AND tpep_pickup_datetime < '2025-02-01'
    GROUP BY hour
    ORDER BY hour
""").show(max_rows=30)

# 5. Find the busiest hour
print("=== Busiest Hour ===")

duckdb.sql(f"""
    SELECT
        EXTRACT(HOUR FROM tpep_pickup_datetime) AS hour,
        COUNT(*) AS total_trips
    FROM read_parquet('{file_path}')
    WHERE tpep_pickup_datetime >= '2025-01-01'
      AND tpep_pickup_datetime < '2025-02-01'
    GROUP BY hour
    ORDER BY total_trips DESC
    LIMIT 1
""").show()

# 6. Compare weekday vs weekend demand
print("=== Weekday vs Weekend ===")

duckdb.sql(f"""
    WITH daily_counts AS (
        SELECT
            CAST(tpep_pickup_datetime AS DATE) AS trip_date,
            CASE
                WHEN EXTRACT(DOW FROM tpep_pickup_datetime)
                     IN (0, 6)
                THEN 'Weekend'
                ELSE 'Weekday'
            END AS day_type,
            COUNT(*) AS trip_count
        FROM read_parquet('{file_path}')
        WHERE tpep_pickup_datetime >= '2025-01-01'
          AND tpep_pickup_datetime < '2025-02-01'
        GROUP BY trip_date, day_type
    )
    SELECT
        day_type,
        COUNT(*) AS num_days,
        ROUND(AVG(trip_count), 0) AS avg_trips_per_day
    FROM daily_counts
    GROUP BY day_type
    ORDER BY avg_trips_per_day DESC
""").show()

# 7. Compare hourly demand on weekdays and weekends
print("=== Hourly Demand: Weekday vs Weekend ===")

duckdb.sql(f"""
    WITH daily_hourly AS (
        SELECT
            CAST(tpep_pickup_datetime AS DATE) AS trip_date,
            EXTRACT(HOUR FROM tpep_pickup_datetime) AS hour,
            CASE
                WHEN EXTRACT(DOW FROM tpep_pickup_datetime)
                     IN (0, 6)
                THEN 'Weekend'
                ELSE 'Weekday'
            END AS day_type,
            COUNT(*) AS trips
        FROM read_parquet('{file_path}')
        WHERE tpep_pickup_datetime >= '2025-01-01'
          AND tpep_pickup_datetime < '2025-02-01'
        GROUP BY trip_date, hour, day_type
    )
    SELECT
        day_type,
        hour,
        ROUND(AVG(trips), 0) AS avg_trips
    FROM daily_hourly
    GROUP BY day_type, hour
    ORDER BY hour, day_type
""").show(max_rows=50)

# 8. Compare 1 AM demand by day of week
print("=== 1 AM Demand by Day of Week ===")

duckdb.sql(f"""
    WITH daily_counts AS (
        SELECT
            CAST(tpep_pickup_datetime AS DATE) AS trip_date,
            DAYNAME(tpep_pickup_datetime) AS day_name,
            COUNT(*) AS trips
        FROM read_parquet('{file_path}')
        WHERE tpep_pickup_datetime >= '2025-01-01'
          AND tpep_pickup_datetime < '2025-02-01'
          AND EXTRACT(HOUR FROM tpep_pickup_datetime) = 1
        GROUP BY trip_date, day_name
    )
    SELECT
        day_name,
        ROUND(AVG(trips), 0) AS avg_trips_at_1am
    FROM daily_counts
    GROUP BY day_name
    ORDER BY avg_trips_at_1am DESC
""").show()

# 9. Find the top 10 pickup zones
print("=== Top 10 Pickup Zones ===")

duckdb.sql(f"""
    WITH trip_counts AS (
        SELECT
            PULocationID,
            COUNT(*) AS total_trips
        FROM read_parquet('{file_path}')
        WHERE tpep_pickup_datetime >= '2025-01-01'
          AND tpep_pickup_datetime < '2025-02-01'
        GROUP BY PULocationID
    )
    SELECT
        z.Borough,
        z.Zone AS pickup_zone,
        t.total_trips
    FROM trip_counts AS t
    INNER JOIN read_csv_auto('{zone_path}') AS z
        ON t.PULocationID = z.LocationID
    ORDER BY t.total_trips DESC
    LIMIT 10
""").show()

# 10. Check data quality
print("=== Data Quality: Time ===")

duckdb.sql(f"""
    SELECT
        COUNT(*) AS total_rows,

        COUNT(*) FILTER (
            WHERE tpep_pickup_datetime IS NULL
        ) AS missing_pickup,

        COUNT(*) FILTER (
            WHERE tpep_dropoff_datetime IS NULL
        ) AS missing_dropoff,

        COUNT(*) FILTER (
            WHERE tpep_dropoff_datetime < tpep_pickup_datetime
        ) AS invalid_time,

        COUNT(*) FILTER (
            WHERE tpep_pickup_datetime < '2025-01-01'
               OR tpep_pickup_datetime >= '2025-02-01'
        ) AS outside_january

    FROM read_parquet('{file_path}')
""").show()

print("=== Data Quality: Distance & Payment ===")

duckdb.sql(f"""
    SELECT
        COUNT(*) FILTER (
            WHERE trip_distance < 0
        ) AS negative_distance,

        COUNT(*) FILTER (
            WHERE trip_distance = 0
        ) AS zero_distance,

        COUNT(*) FILTER (
            WHERE total_amount < 0
        ) AS negative_amount,

        COUNT(*) FILTER (
            WHERE total_amount IS NULL
        ) AS missing_amount,

        COUNT(*) FILTER (
            WHERE PULocationID IS NULL
        ) AS missing_location

    FROM read_parquet('{file_path}')
""").show()

# 11. Check usable pickup records
print("=== Pickup Data Cleaning Summary ===")

duckdb.sql(f"""
    WITH checked_trips AS (
        SELECT
            CASE
                WHEN t.tpep_pickup_datetime IS NULL
                    THEN 'Missing pickup time'

                WHEN t.tpep_pickup_datetime < '2025-01-01'
                  OR t.tpep_pickup_datetime >= '2025-02-01'
                    THEN 'Outside January'

                WHEN z.LocationID IS NULL
                    THEN 'Unmatched location'

                WHEN z.Borough IS NULL
                  OR z.Zone IS NULL
                  OR z.Borough = 'Unknown'
                  OR z.Zone = 'Unknown'
                    THEN 'Unknown zone'

                ELSE 'Usable pickup'
            END AS quality_status

        FROM read_parquet('{file_path}') AS t
        LEFT JOIN read_csv_auto('{zone_path}') AS z
            ON t.PULocationID = z.LocationID
    )

    SELECT
        quality_status,
        COUNT(*) AS total_trips
    FROM checked_trips
    GROUP BY quality_status
    ORDER BY total_trips DESC
""").show()
