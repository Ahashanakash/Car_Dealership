from pathlib import Path
import re
import joblib
import numpy as np
import pandas as pd

from xgboost import XGBRegressor

from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "data" / "car_price_data.csv"
MODEL_PATH = BASE_DIR / "xgboost_car_price_model.pkl"


COLUMN_RENAME_MAP = {
    "Price": "price",
    "Levy": "levy",
    "Manufacturer": "brand",
    "Manufact": "brand",
    "Model": "car_model",
    "Prod. year": "prod_year",
    "Category": "category",
    "Leather interior": "leather_interior",
    "Leather in": "leather_interior",
    "Fuel type": "fuel_type",
    "Engine volume": "engine_volume",
    "Engine vol": "engine_volume",
    "Mileage": "mileage",
    "Cylinders": "cylinders",
    "Gear box type": "gear_box_type",
    "Gear box": "gear_box_type",
    "Drive wheels": "drive_wheels",
    "Drive whe": "drive_wheels",
    "Doors": "doors",
    "Wheel": "wheel",
    "Color": "color",
    "Airbags": "airbags",
}


CATEGORICAL_FEATURES = [
    "brand",
    "car_model",
    "category",
    "leather_interior",
    "fuel_type",
    "gear_box_type",
    "drive_wheels",
    "doors",
    "wheel",
    "color",
]


NUMERIC_FEATURES = [
    "levy_num",
    "levy_missing",
    "prod_year",
    "mileage_num",
    "cylinders",
    "airbags",
    "engine_volume_num",
    "engine_is_turbo",
]


ALL_FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES


def normalize_text(value):
    if pd.isna(value):
        return "unknown"

    text = str(value).strip()

    if text == "" or text.lower() in ["nan", "none", "null"]:
        return "unknown"

    return text.lower()


def extract_number(value):
    """
    Handles:
    '186005 km' -> 186005
    '2.0 Turbo' -> 2.0
    '3.5' -> 3.5
    '1,399' -> 1399
    '-' -> NaN
    """
    if pd.isna(value):
        return np.nan

    text = str(value).replace(",", "").strip()

    if text in ["", "-", "--", "nan", "None", "null"]:
        return np.nan

    match = re.search(r"\d+(\.\d+)?", text)

    if not match:
        return np.nan

    return float(match.group(0))


def clean_dataframe(df):
    df = df.copy()

    df = df.rename(columns=COLUMN_RENAME_MAP)

    required_columns = [
        "price",
        "levy",
        "brand",
        "car_model",
        "prod_year",
        "category",
        "leather_interior",
        "fuel_type",
        "engine_volume",
        "mileage",
        "cylinders",
        "gear_box_type",
        "drive_wheels",
        "doors",
        "wheel",
        "color",
        "airbags",
    ]

    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing CSV columns: {missing_columns}")

    # Target
    df["price"] = df["price"].apply(extract_number)

    # Levy
    df["levy_num"] = df["levy"].apply(extract_number)
    df["levy_missing"] = df["levy_num"].isna().astype(int)

    # Numeric fields
    df["prod_year"] = df["prod_year"].apply(extract_number)
    df["mileage_num"] = df["mileage"].apply(extract_number)
    df["cylinders"] = df["cylinders"].apply(extract_number)
    df["airbags"] = df["airbags"].apply(extract_number)

    # Engine volume
    df["engine_volume_text"] = df["engine_volume"].astype(str).str.lower()
    df["engine_volume_num"] = df["engine_volume"].apply(extract_number)
    df["engine_is_turbo"] = df["engine_volume_text"].str.contains("turbo").astype(int)

    # Fill numeric missing values
    df["levy_num"] = df["levy_num"].fillna(0)
    df["airbags"] = df["airbags"].fillna(0)

    if df["engine_volume_num"].notna().sum() > 0:
        df["engine_volume_num"] = df["engine_volume_num"].fillna(df["engine_volume_num"].median())
    else:
        df["engine_volume_num"] = df["engine_volume_num"].fillna(0)

    # Drop rows missing critical values
    df = df.dropna(subset=[
        "price",
        "prod_year",
        "mileage_num",
        "cylinders",
    ])

    # Type conversion
    for col in NUMERIC_FEATURES + ["price"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Remove impossible values
    df = df[df["price"] >= 1500]
    df = df[df["prod_year"] >= 1980]
    df = df[df["prod_year"] <= 2026]
    df = df[df["mileage_num"] >= 0]
    df = df[df["cylinders"] > 0]
    df = df[df["engine_volume_num"] > 0]

    # Remove extreme price outliers
    # This removes values like 30 and extremely inflated prices.
    lower_price = df["price"].quantile(0.01)
    upper_price = df["price"].quantile(0.99)

    df = df[
        (df["price"] >= lower_price) &
        (df["price"] <= upper_price)
    ]

    # Clean categorical columns
    for col in CATEGORICAL_FEATURES:
        df[col] = df[col].apply(normalize_text)

    # Final feature-only dataframe
    df = df[ALL_FEATURES + ["price"]]

    return df


def train_model():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)
    df = clean_dataframe(df)

    print("Rows after cleaning:", len(df))

    if len(df) < 1000:
        print("Warning: Dataset is small. Model may not be reliable.")

    X = df[ALL_FEATURES]
    y = df["price"]

    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="unknown")),
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ])

    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
        ]
    )

    xgb = XGBRegressor(
        objective="reg:squarederror",
        n_estimators=800,
        learning_rate=0.04,
        max_depth=7,
        min_child_weight=3,
        subsample=0.85,
        colsample_bytree=0.85,
        reg_alpha=0.1,
        reg_lambda=1.2,
        random_state=42,
        n_jobs=-1,
    )

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", xgb),
    ])

    model = TransformedTargetRegressor(
        regressor=pipeline,
        func=np.log1p,
        inverse_func=np.expm1,
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    predictions = np.maximum(predictions, 0)

    mae = mean_absolute_error(y_test, predictions)
    rmse = mean_squared_error(y_test, predictions) ** 0.5
    r2 = r2_score(y_test, predictions)

    safe_y_test = y_test.replace(0, np.nan)
    mape = np.nanmean(np.abs((safe_y_test - predictions) / safe_y_test)) * 100

    print("Training completed.")
    print(f"MAE: {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")
    print(f"R2 Score: {r2:.4f}")
    print(f"MAPE: {mape:.2f}%")

    bundle = {
        "model": model,
        "all_features": ALL_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "numeric_features": NUMERIC_FEATURES,
        "metrics": {
            "mae": round(float(mae), 2),
            "rmse": round(float(rmse), 2),
            "r2": round(float(r2), 4),
            "mape": round(float(mape), 2),
        },
    }

    joblib.dump(bundle, MODEL_PATH)

    print(f"Model saved to: {MODEL_PATH}")


if __name__ == "__main__":
    train_model()