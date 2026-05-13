from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from functools import lru_cache
import re

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "xgboost_car_price_model.pkl"


def normalize_text(value):
    if value is None:
        return "unknown"

    text = str(value).strip()

    if text == "" or text.lower() in ["nan", "none", "null"]:
        return "unknown"

    return text.lower()


def money(value):
    if value is None:
        return None

    return Decimal(str(value)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


def extract_number(value):
    if value is None:
        return None

    text = str(value).replace(",", "").strip()

    if text in ["", "-", "--", "nan", "None", "null"]:
        return None

    match = re.search(r"\d+(\.\d+)?", text)

    if not match:
        return None

    return float(match.group(0))


@lru_cache(maxsize=1)
def load_model_bundle():
    if not MODEL_PATH.exists():
        return None

    return joblib.load(MODEL_PATH)


def make_prediction_dataframe_from_car(car):
    engine_text = str(car.engine_volume or "")
    engine_volume_num = extract_number(engine_text)

    if engine_volume_num is None:
        engine_volume_num = 0

    engine_is_turbo = 1 if "turbo" in engine_text.lower() else 0

    levy_value = getattr(car, "levy", None)

    if levy_value in [None, "", "-"]:
        levy_num = 0
        levy_missing = 1
    else:
        levy_num = extract_number(levy_value)

        if levy_num is None:
            levy_num = 0
            levy_missing = 1
        else:
            levy_missing = 0

    data = {
        "brand": normalize_text(car.brand.name),
        "car_model": normalize_text(car.car_model),
        "category": normalize_text(car.category),
        "leather_interior": normalize_text(car.leather_interior),
        "fuel_type": normalize_text(car.fuel_type),
        "gear_box_type": normalize_text(car.gear_box_type),
        "drive_wheels": normalize_text(car.drive_wheels),
        "doors": normalize_text(car.doors),
        "wheel": normalize_text(car.wheel),
        "color": normalize_text(car.color),

        "levy_num": levy_num,
        "levy_missing": levy_missing,
        "prod_year": car.prod_year,
        "mileage_num": car.mileage,
        "cylinders": car.cylinders,
        "airbags": car.airbags or 0,
        "engine_volume_num": engine_volume_num,
        "engine_is_turbo": engine_is_turbo,
    }

    return pd.DataFrame([data])


def predict_car_price(car):
    bundle = load_model_bundle()

    if bundle is None:
        return {
            "predicted_price": None,
            "metrics": {},
        }

    model = bundle["model"]
    input_df = make_prediction_dataframe_from_car(car)

    predicted_price = model.predict(input_df)[0]

    if predicted_price < 0:
        predicted_price = 0

    return {
        "predicted_price": money(predicted_price),
        "metrics": bundle.get("metrics", {}),
    }


def classify_car_price(car, predicted_price):
    if predicted_price is None:
        return {
            "status": "insufficient_data",
            "lower_limit": None,
            "upper_limit": None,
        }

    predicted_price = money(predicted_price)
    seller_price = money(car.price)

    lower_limit = money(predicted_price * Decimal("0.85"))
    upper_limit = money(predicted_price * Decimal("1.15"))

    if seller_price < lower_limit:
        status = "low"
    elif seller_price > upper_limit:
        status = "high"
    else:
        status = "regular"

    return {
        "status": status,
        "lower_limit": lower_limit,
        "upper_limit": upper_limit,
    }