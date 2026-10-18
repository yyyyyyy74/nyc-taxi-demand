import duckdb

# 1. File path
input_path = "data/processed/ml_features_2025_Q1.parquet"

# 2. Evaluate baseline models on February
print("=== Baseline Model Evaluation ===")

results = duckdb.sql(f"""
    WITH validation AS (
        SELECT
            pickup_count,
            lag_24h,
            lag_168h
        FROM read_parquet('{input_path}')
        WHERE pickup_hour >= '2025-02-01'
          AND pickup_hour < '2025-03-01'
    ),

    predictions AS (
        SELECT
            'Yesterday Baseline' AS model,
            pickup_count AS actual,
            lag_24h AS predicted
        FROM validation

        UNION ALL

        SELECT
            'Last Week Baseline' AS model,
            pickup_count AS actual,
            lag_168h AS predicted
        FROM validation
    )

    SELECT
        model,
        COUNT(*) AS evaluated_rows,
        ROUND(AVG(ABS(actual - predicted)), 2) AS MAE,
        ROUND(
            SQRT(AVG(POWER(actual - predicted, 2))),
            2
        ) AS RMSE
    FROM predictions
    WHERE predicted IS NOT NULL
    GROUP BY model
    ORDER BY MAE
""")

results.show()

print("=== Baseline Evaluation Complete ===")
