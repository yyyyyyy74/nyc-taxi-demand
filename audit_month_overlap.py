import duckdb

print("=== January Records by Source File ===")

duckdb.sql("""
    SELECT
        CASE
            WHEN t.filename LIKE '%2025-01.parquet'
                THEN 'January File'
            WHEN t.filename LIKE '%2025-02.parquet'
                THEN 'February File'
            WHEN t.filename LIKE '%2025-03.parquet'
                THEN 'March File'
        END AS source_file,

        COUNT(*) AS january_trips

    FROM read_parquet(
        [
            'data/raw/yellow_tripdata_2025-01.parquet',
            'data/raw/yellow_tripdata_2025-02.parquet',
            'data/raw/yellow_tripdata_2025-03.parquet'
        ],
        union_by_name = true,
        filename = true
    ) AS t

    INNER JOIN read_csv_auto(
        'data/lookup/taxi_zone_lookup.csv'
    ) AS z
        ON t.PULocationID = z.LocationID

    WHERE t.tpep_pickup_datetime >= '2025-01-01'
      AND t.tpep_pickup_datetime < '2025-02-01'
      AND z.Borough IS NOT NULL
      AND z.Zone IS NOT NULL
      AND z.Borough <> 'Unknown'
      AND z.Zone <> 'Unknown'

    GROUP BY source_file
    ORDER BY source_file
""").show()

print("=== Audit Complete ===")
