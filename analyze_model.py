import duckdb
import numpy as np

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# 1. Load dataset
input_path = "data/processed/ml_features_2025_Q1.parquet"

features = [
    "pickup_location_id",
    "hour",
    "day_of_week",
    "lag_1h",
    "lag_24h",
    "lag_168h"
]

df = duckdb.sql(f"""
    SELECT *
    FROM read_parquet('{input_path}')
    WHERE pickup_hour >= '2025-01-08'
      AND pickup_hour < '2025-03-01'
""").df()

df = df.dropna(subset=features)

# 2. Train / validation split
train = df[df["pickup_hour"] < "2025-02-01"]
valid = df[df["pickup_hour"] >= "2025-02-01"]

X_train = train[features]
y_train = train["pickup_count"]

X_valid = valid[features]
y_valid = valid["pickup_count"]

# 3. Train the same Random Forest
print("=== Training Random Forest ===")

model = RandomForestRegressor(
    n_estimators=60,
    max_depth=15,
    min_samples_leaf=5,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

predictions = np.maximum(model.predict(X_valid), 0)

# 4. Feature importance
print("=== Feature Importance ===")

importance = sorted(
    zip(features, model.feature_importances_),
    key=lambda x: x[1],
    reverse=True
)

for feature, score in importance:
    print(f"{feature}: {score:.4f}")

# 5. Find the 5 busiest zones in training data
top_zones = (
    train
    .groupby(
        ["pickup_location_id", "pickup_zone"],
        as_index=False
    )["pickup_count"]
    .sum()
    .nlargest(5, "pickup_count")
)

print("=== Top 5 Training Zones ===")
print(top_zones)

# 6. Compare errors for different groups
print("=== Error Analysis ===")

groups = [
    (
        "All February Rows",
        valid["pickup_count"] >= 0
    ),
    (
        "Top 5 Busiest Zones",
        valid["pickup_location_id"].isin(
            top_zones["pickup_location_id"]
        )
    ),
    (
        "Nonzero Demand Rows",
        valid["pickup_count"] > 0
    )
]

for group_name, mask in groups:
    actual = y_valid.loc[mask]
    baseline = valid.loc[mask, "lag_168h"]
    rf_pred = predictions[mask.to_numpy()]

    print(f"\n{group_name} ({len(actual)} rows)")

    for name, predicted in [
        ("Last Week Baseline", baseline),
        ("Random Forest", rf_pred)
    ]:
        mae = mean_absolute_error(actual, predicted)
        rmse = np.sqrt(
            mean_squared_error(actual, predicted)
        )

        print(f"{name}: MAE={mae:.2f}, RMSE={rmse:.2f}")

print("\n=== Analysis Complete ===")
