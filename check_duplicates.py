import duckdb

print("=== Checking Cross-Month Duplicates ===")

duckdb.sql("""
    WITH feb_january AS (
        SELECT f.*
        FROM read_parquet(
            'data/raw/yellow_tripdata_2025-02.parquet'
        ) AS f
        INNER JOIN read_csv_auto(
            'data/lookup/taxi_zone_lookup.csv'
        ) AS z
            ON f.PULocationID = z.LocationID
        WHERE f.tpep_pickup_datetime >= '2025-01-01'
          AND f.tpep_pickup_datetime < '2025-02-01'
          AND z.Borough IS NOT NULL
          AND z.Zone IS NOT NULL
          AND z.Borough <> 'Unknown'
          AND z.Zone <> 'Unknown'
    ),

    january AS (
        SELECT *
        FROM read_parquet(
            'data/raw/yellow_tripdata_2025-01.parquet'
        )
    ),

    checked AS (
        SELECT
            EXISTS (
                SELECT 1
                FROM january AS j
                WHERE j.tpep_pickup_datetime =
                      f.tpep_pickup_datetime
                  AND j.tpep_dropoff_datetime
                      IS NOT DISTINCT FROM f.tpep_dropoff_datetime
                  AND j.PULocationID
                      IS NOT DISTINCT FROM f.PULocationID
                  AND j.DOLocationID
                      IS NOT DISTINCT FROM f.DOLocationID
                  AND j.trip_distance
                      IS NOT DISTINCT FROM f.trip_distance
                  AND j.fare_amount
                      IS NOT DISTINCT FROM f.fare_amount
                  AND j.total_amount
                      IS NOT DISTINCT FROM f.total_amount
                  AND j.VendorID
                      IS NOT DISTINCT FROM f.VendorID
            ) AS has_match
        FROM feb_january AS f
    )

    SELECT
        COUNT(*) AS feb_january_rows,
        COUNT(*) FILTER (
            WHERE has_match
        ) AS matching_rows,
        COUNT(*) FILTER (
            WHERE NOT has_match
        ) AS nonmatching_rows
    FROM checked
""").show()

print("=== Duplicate Check Complete ===")
