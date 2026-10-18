import duckdb
import numpy as np
import joblib
from pathlib import Path

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# 1. Paths
input_path = "data/processed/ml_features_2025_Q1.parquet"
model_path = "models/random_forest_q1_2025.joblib"

Path("models").mkdir(exist_ok=True)

features = [
    "pickup_location_id",
    "hour",
    "day_of_week",
    "lag_1h",
    "lag_24h",
    "lag_168h"
]

# 2. Load data
df = duckdb.sql(f"""
    SELECT *
    FROM read_parquet('{input_path}')
    WHERE pickup_hour >= '2025-01-08'
      AND pickup_hour < '2025-04-01'
""").df()

df = df.dropna(subset=features)

# 3. Chronological split
train = df[df["pickup_hour"] < "2025-03-01"]
test = df[df["pickup_hour"] >= "2025-03-01"]

X_train = train[features]
y_train = train["pickup_count"]

X_test = test[features]
y_test = test["pickup_count"]

print("Training rows:", len(train))
print("Test rows:", len(test))

# 4. Train final model
print("=== Training Final Random Forest ===")

model = RandomForestRegressor(
    n_estimators=60,
    max_depth=15,
    min_samples_leaf=5,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# 5. Save trained model
joblib.dump(model, model_path)
print("Model saved successfully!")

# 6. Evaluate on March
print("=== March Test Results ===")

rf_predictions = np.maximum(model.predict(X_test), 0)
baseline_predictions = test["lag_168h"]

for name, predicted in [
    ("Last Week Baseline", baseline_predictions),
    ("Random Forest", rf_predictions)
]:
    mae = mean_absolute_error(y_test, predicted)
    rmse = np.sqrt(mean_squared_error(y_test, predicted))

    print(f"{name}")
    print(f"  MAE:  {mae:.2f}")
    print(f"  RMSE: {rmse:.2f}")

print("=== Final Model Complete ===")
