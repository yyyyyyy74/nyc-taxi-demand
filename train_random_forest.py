import duckdb
import numpy as np

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# 1. Load ML features
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

# 2. Remove rows with missing lag features
df = df.dropna(subset=features)

# 3. Chronological train / validation split
train = df[df["pickup_hour"] < "2025-02-01"]
valid = df[df["pickup_hour"] >= "2025-02-01"]

X_train = train[features]
y_train = train["pickup_count"]

X_valid = valid[features]
y_valid = valid["pickup_count"]

print("Training rows:", len(train))
print("Validation rows:", len(valid))

# 4. Train Random Forest
print("=== Training Random Forest ===")

model = RandomForestRegressor(
    n_estimators=60,
    max_depth=15,
    min_samples_leaf=5,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# 5. Make predictions
predictions = model.predict(X_valid)
predictions = np.maximum(predictions, 0)

# 6. Compare with Last Week Baseline
print("=== Model Comparison ===")

baseline_predictions = valid["lag_168h"]

for name, predicted in [
    ("Last Week Baseline", baseline_predictions),
    ("Random Forest", predictions)
]:
    mae = mean_absolute_error(y_valid, predicted)
    rmse = np.sqrt(mean_squared_error(y_valid, predicted))

    print(f"{name}")
    print(f"  MAE:  {mae:.2f}")
    print(f"  RMSE: {rmse:.2f}")

print("=== Training Complete ===")
