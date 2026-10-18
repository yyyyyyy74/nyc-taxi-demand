# NYC Taxi Demand Forecasting & Analytics Platform

### End-to-End Data Science | SQL | Machine Learning | Streamlit

An end-to-end data science project that analyzes New York City Yellow Taxi trip records, explores temporal and geographic demand patterns, and predicts hourly taxi demand using machine learning.

The project combines **SQL-based data processing, exploratory data analysis (EDA), feature engineering, machine learning, model evaluation, and an interactive Streamlit dashboard**.

---

## 1. Project Overview

Understanding transportation demand is important for fleet planning, resource allocation, and urban mobility analysis.

This project uses real-world NYC Yellow Taxi trip records from **January through March 2025** to investigate two main questions:

- How does taxi demand vary across different hours, days, and pickup locations?
- Can machine learning predict hourly taxi demand more accurately than simple historical baselines?

### Project Workflow

1. Collect and explore real-world taxi trip data.
2. Clean and transform raw records using SQL and DuckDB.
3. Analyze temporal and geographic demand patterns.
4. Build an interactive analytics dashboard using Streamlit.
5. Engineer time-based and historical demand features.
6. Train and evaluate machine learning models using chronological data splits.
7. Compare model predictions against historical baselines.

---

## 2. Dataset

**Data Source:** [NYC Taxi & Limousine Commission (TLC) Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)

The dataset contains NYC Yellow Taxi trip records from January through March 2025.

### Dataset Summary

| Metric | Value |
|---|---:|
| Data Period | January–March 2025 |
| Records After Cleaning | 11,174,703 |
| Pickup Zones | 260 |
| Total Hours | 2,160 |
| Hourly Zone-Level Observations | 561,600 |

The original TLC dataset is provided in Parquet format and contains pickup timestamps, location identifiers, trip distances, fare amounts, and additional trip information.

For demand forecasting, individual trip records are aggregated into hourly pickup counts for each taxi zone.

Missing zone-hour combinations are filled with zero under the assumption that the source records adequately cover the reporting period.

Large raw datasets are excluded from the GitHub repository.

---

## 3. Technologies Used

| Category | Technologies |
|---|---|
| Programming | Python, SQL |
| Data Processing | DuckDB, pandas |
| Data Storage | Parquet |
| Machine Learning | scikit-learn, Random Forest |
| Data Visualization | Matplotlib, Streamlit |
| Model Evaluation | MAE, RMSE |
| Model Persistence | joblib |
| Development Tools | VS Code, Git, GitHub |

---

## 4. Data Processing and Exploratory Analysis

### Data Cleaning

Raw trip records are processed using DuckDB and SQL.

The cleaning workflow includes:

- Filtering trips to the January–March 2025 reporting period.
- Removing records with missing or unrecognized pickup locations.
- Joining taxi zone lookup data to obtain borough and zone names.
- Identifying invalid timestamps and other data quality issues.
- Aggregating individual trips into hourly pickup counts.
- Generating continuous hourly observations for each pickup zone.

A cross-month data quality audit also identified 30 January pickup records stored in the February source file. No matching records were found in the January file using the selected comparison fields.

### Exploratory Data Analysis

The project investigates several demand patterns:

**Hourly Demand**
- Analyzes average pickup demand by hour.
- Identifies peak and low-demand periods.

**Weekday vs. Weekend Demand**
- Compares hourly demand patterns between weekdays and weekends.
- Examines differences in morning and late-night activity.

**Geographic Demand**
- Identifies the busiest taxi pickup zones.
- Compares pickup activity across boroughs.

**Daily Demand Trends**
- Examines day-to-day changes in pickup activity.
- Supports interactive date-range analysis.

---

## 5. Interactive Streamlit Dashboard

The project includes an interactive dashboard developed using Streamlit.

### Dashboard Features

- **Borough Filtering:** Explore taxi demand across different NYC boroughs.
- **Taxi Zone Selection:** Analyze individual pickup zones.
- **Date Range Filtering:** Explore historical demand between January and March 2025.
- **Hourly Demand Visualization:** View average pickup counts by hour.
- **Daily Demand Trends:** Examine daily changes in taxi demand.
- **Top 10 Pickup Zones:** Identify the busiest locations within a selected borough.
- **Machine Learning Backtesting:** Compare actual demand with Random Forest predictions and historical baseline estimates.
- **Prediction Accuracy Metrics:** Display MAE and RMSE for selected historical backtest dates.

The dashboard allows users to explore transportation demand without writing SQL queries or Python code.

---

## 6. Machine Learning Methodology

### Prediction Objective

The machine learning model predicts:

**The number of taxi pickups in a particular zone during a given hour.**

This is a supervised regression problem.

### Feature Engineering

The following features are used:

| Feature | Description |
|---|---|
| `pickup_location_id` | Taxi pickup zone identifier |
| `hour` | Hour of day |
| `day_of_week` | Day of the week |
| `lag_1h` | Pickup demand one hour earlier |
| `lag_24h` | Pickup demand 24 hours earlier |
| `lag_168h` | Pickup demand one week earlier |

Historical demand features are constructed independently for each pickup zone using SQL window functions.

### Chronological Data Split

To preserve the chronological order of observations, the project uses time-based rather than random data splits.

| Dataset | Period | Purpose |
|---|---|---|
| Training | January 8–31, 2025 | Initial Model Training |
| Validation | February 2025 | Model Evaluation and Selection |
| Final Training | January 8–February 28, 2025 | Final Model Training |
| Testing | March 2025 | Final Out-of-Sample Evaluation |

The first seven days are excluded from training because the model requires up to 168 hours of historical demand.

### Models

Two historical baselines were evaluated:

- **Yesterday Baseline:** Uses the pickup count from the same hour on the previous day.
- **Last Week Baseline:** Uses the pickup count from the same hour one week earlier.

The machine learning model is a **Random Forest Regressor** implemented with scikit-learn.

### Random Forest Configuration

| Hyperparameter | Value |
|---|---:|
| Number of Trees | 60 |
| Maximum Depth | 15 |
| Minimum Samples per Leaf | 5 |
| Random State | 42 |

---

## 7. Model Evaluation and Results

Models are evaluated using:

- **MAE (Mean Absolute Error):** The average absolute difference between actual and predicted pickup counts.
- **RMSE (Root Mean Squared Error):** A measure of prediction error that penalizes larger errors more heavily.

Lower values indicate better predictive performance.

### February 2025 Validation Results

| Model | MAE | RMSE |
|---|---:|---:|
| Yesterday Baseline | 7.00 | 25.75 |
| Last Week Baseline | 4.65 | 14.53 |
| Random Forest | **3.82** | **11.41** |

Random Forest outperformed both historical baselines on the February validation dataset.

### March 2025 Final Test Results

| Model | MAE | RMSE |
|---|---:|---:|
| Last Week Baseline | 4.83 | 14.92 |
| Random Forest | **3.93** | **12.05** |

On the March test set, Random Forest achieved:

- **18.6% lower MAE** than the last-week baseline.
- **19.2% lower RMSE** than the last-week baseline.

The evaluation contains **193,440 zone-hour observations** from March 2025.

### Feature Importance

Random Forest feature importance analysis showed that historical pickup demand is especially informative.

| Feature | Importance |
|---|---:|
| `lag_1h` | 0.8009 |
| `lag_168h` | 0.1550 |
| `lag_24h` | 0.0307 |
| `hour` | 0.0062 |
| `day_of_week` | 0.0045 |
| `pickup_location_id` | 0.0027 |

The previous hour's demand was the most influential feature according to the model's impurity-based importance scores.

Feature importance does not establish causation.

### Error Analysis

Additional analysis examined prediction performance across different demand levels.

On the February validation set:

| Evaluation Group | Baseline MAE | Random Forest MAE |
|---|---:|---:|
| All Zones | 4.65 | **3.82** |
| Top 5 Busiest Zones | 34.26 | **28.14** |
| Nonzero Demand Hours | 7.73 | **6.21** |

Random Forest performed better across all three evaluation groups.

However, prediction errors were substantially larger in high-demand zones, indicating that overall MAE alone does not fully describe model performance.

### Forecasting Scope

The model is evaluated for **one-hour-ahead prediction with recently observed demand available**.

Historical lag features use actual pickup counts recorded before each predicted hour.

The results should not be interpreted as the accuracy of forecasting an entire future day or month without updated observations.

---

## 8. Project Structure

```text
nyc-taxi-demand/
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── raw/
│   ├── lookup/
│   └── processed/
│       ├── hourly_demand_complete_2025_Q1.parquet
│       └── ml_features_2025_Q1.parquet
│
├── models/
│   └── random_forest_q1_2025.joblib
│
├── charts/
│   ├── hourly_demand.png
│   ├── weekday_vs_weekend.png
│   └── top_10_pickup_zones.png
│
├── explore_data.py
├── prepare_data.py
├── prepare_multimonth.py
├── create_hourly_demand.py
├── complete_hourly_demand.py
├── create_q1_hourly_demand.py
├── create_ml_features.py
├── visualize_demand.py
├── visualize_weekday_weekend.py
├── visualize_top_zones.py
├── evaluate_baseline.py
├── train_random_forest.py
├── analyze_model.py
├── final_model.py
├── audit_month_overlap.py
└── check_duplicates.py
```

The `data/raw/` directory and most intermediate processed files are excluded from version control.

The repository includes the small processed datasets required by the dashboard.

---

## 9. Running the Project Locally

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd nyc-taxi-demand
```

Replace `<repository-url>` with the GitHub repository URL after publication.

### Step 2: Install Dependencies

Make sure Python is installed.

Install the required packages:

```bash
python -m pip install -r requirements.txt
```

### Step 3: Launch the Streamlit Dashboard

```bash
python -m streamlit run app.py
```

Open the local URL displayed in the terminal, typically:

```text
http://localhost:8501
```

The dashboard requires:

- `data/processed/hourly_demand_complete_2025_Q1.parquet`
- `data/processed/ml_features_2025_Q1.parquet`
- `models/random_forest_q1_2025.joblib`

### Reproducing the Data Pipeline

To regenerate the processed datasets, download the January, February, and March 2025 Yellow Taxi Parquet files from the NYC TLC website.

Place them in:

```text
data/raw/
```

Make sure the taxi zone lookup CSV is available at:

```text
data/lookup/taxi_zone_lookup.csv
```

Then execute the following scripts in order:

```bash
python prepare_multimonth.py
python create_q1_hourly_demand.py
python create_ml_features.py
python final_model.py
```

These scripts prepare the quarterly dataset, construct the hourly demand observations, generate machine learning features, and train the final model.

---

## 10. Limitations and Future Improvements

### Current Limitations

- The dataset covers only January–March 2025, limiting analysis of annual seasonality.
- The model relies on previously observed pickup counts.
- The current forecasting setup assumes updated historical demand is available before each prediction.
- High-demand zones exhibit larger absolute prediction errors.
- Missing zone-hour combinations are treated as zero demand under a data coverage assumption.
- Weather, holidays, and special events are not included as model features.
- Hourly timestamps are treated as timezone-naive, and daylight saving time transitions are not explicitly handled.

### Potential Future Improvements

- Expand the dataset to cover an entire year or longer.
- Add weather, holiday, and event-related features.
- Evaluate additional regression models.
- Explore multi-hour and multi-day forecasting methods.
- Improve demand predictions for high-volume pickup zones.
- Add automated data quality checks and model monitoring.

---

## 11. Data Source and Acknowledgments

Taxi trip data is provided by the **New York City Taxi & Limousine Commission (NYC TLC)**.

Official Data Source:

[NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)

This is an independent educational and portfolio project developed to demonstrate practical skills in data analytics, machine learning, and data engineering.