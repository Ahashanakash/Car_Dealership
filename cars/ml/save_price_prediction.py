from decimal import Decimal

from cars.models import CarPricePrediction
from cars.ml.price_predictor import predict_car_price, classify_car_price


def to_decimal_or_none(value):
    if value is None:
        return None

    return Decimal(str(value))


def save_price_prediction_for_car(car):
    prediction_result = predict_car_price(car)

    predicted_price = prediction_result["predicted_price"]
    metrics = prediction_result.get("metrics", {})

    classification = classify_car_price(car, predicted_price)

    mae = metrics.get("mae")
    r2 = metrics.get("r2")
    mape = metrics.get("mape")

    CarPricePrediction.objects.update_or_create(
        car=car,
        defaults={
            "predicted_price": predicted_price,
            "lower_price_limit": classification["lower_limit"],
            "upper_price_limit": classification["upper_limit"],
            "seller_price": car.price,
            "price_status": classification["status"],
            "model_mae": to_decimal_or_none(mae),
            "model_r2_score": to_decimal_or_none(r2),
            "model_mape": to_decimal_or_none(mape),
        }
    )