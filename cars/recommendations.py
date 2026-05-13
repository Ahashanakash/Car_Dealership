from decimal import Decimal

from django.db.models import Case, When, Value, IntegerField

from .models import Car


def get_recommended_cars(car, limit=4):
    """
    Content-based recommendation system.

    It recommends cars similar to the current car based on:
    - Brand
    - Category
    - Fuel type
    - Color
    - Gearbox
    - Drive wheels
    - Production year range
    - Price range
    """

    price_min = car.price * Decimal("0.80")
    price_max = car.price * Decimal("1.20")

    year_min_close = car.prod_year - 2
    year_max_close = car.prod_year + 2

    year_min_loose = car.prod_year - 5
    year_max_loose = car.prod_year + 5

    score_expression = (
        Case(
            When(brand=car.brand, then=Value(40)),
            default=Value(0),
            output_field=IntegerField()
        )
        +
        Case(
            When(category=car.category, then=Value(35)),
            default=Value(0),
            output_field=IntegerField()
        )
        +
        Case(
            When(fuel_type=car.fuel_type, then=Value(20)),
            default=Value(0),
            output_field=IntegerField()
        )
        +
        Case(
            When(color=car.color, then=Value(10)),
            default=Value(0),
            output_field=IntegerField()
        )
        +
        Case(
            When(gear_box_type=car.gear_box_type, then=Value(10)),
            default=Value(0),
            output_field=IntegerField()
        )
        +
        Case(
            When(drive_wheels=car.drive_wheels, then=Value(8)),
            default=Value(0),
            output_field=IntegerField()
        )
        +
        Case(
            When(leather_interior=car.leather_interior, then=Value(5)),
            default=Value(0),
            output_field=IntegerField()
        )
        +
        Case(
            When(prod_year__gte=year_min_close, prod_year__lte=year_max_close, then=Value(15)),
            When(prod_year__gte=year_min_loose, prod_year__lte=year_max_loose, then=Value(8)),
            default=Value(0),
            output_field=IntegerField()
        )
        +
        Case(
            When(price__gte=price_min, price__lte=price_max, then=Value(15)),
            default=Value(0),
            output_field=IntegerField()
        )
    )

    recommended_cars = (
        Car.objects
        .filter(is_sold=False)
        .exclude(id=car.id)
        .select_related("brand")
        .annotate(recommendation_score=score_expression)
        .filter(recommendation_score__gt=0)
        .order_by("-recommendation_score", "-created_at")[:limit]
    )

    return recommended_cars