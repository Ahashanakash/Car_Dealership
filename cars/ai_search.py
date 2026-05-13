import json
import logging
import re
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from google import genai
from google.genai import types

from .models import (
    Brand,
    CATEGOTY,
    LEATHER_INTERIOR,
    FUEL_TYPE,
    GEAR_BOX_TYPE,
    DRIVE_WHEELS,
    DOORS,
    WHEEL,
    COLOR_CHOICES,
)

logger = logging.getLogger(__name__)


AI_FILTER_SCHEMA = {
    "type": "object",
    "properties": {
        "brand_name": {"type": "string", "nullable": True},
        "car_model": {"type": "string", "nullable": True},
        "category": {"type": "string", "nullable": True},
        "color": {"type": "string", "nullable": True},
        "fuel_type": {"type": "string", "nullable": True},
        "leather_interior": {"type": "string", "nullable": True},
        "engine_volume": {"type": "string", "nullable": True},
        "cylinders": {"type": "integer", "nullable": True},
        "gear_box_type": {"type": "string", "nullable": True},
        "drive_wheels": {"type": "string", "nullable": True},
        "doors": {"type": "string", "nullable": True},
        "wheel": {"type": "string", "nullable": True},
        "min_price": {"type": "number", "nullable": True},
        "max_price": {"type": "number", "nullable": True},
        "min_year": {"type": "integer", "nullable": True},
        "max_year": {"type": "integer", "nullable": True},
        "min_mileage": {"type": "integer", "nullable": True},
        "max_mileage": {"type": "integer", "nullable": True},
        "min_airbags": {"type": "integer", "nullable": True},
        "max_airbags": {"type": "integer", "nullable": True},
        "available_only": {"type": "boolean", "nullable": True},
        "keywords": {"type": "string", "nullable": True},
    },
    "required": [
        "brand_name",
        "car_model",
        "category",
        "color",
        "fuel_type",
        "leather_interior",
        "engine_volume",
        "cylinders",
        "gear_box_type",
        "drive_wheels",
        "doors",
        "wheel",
        "min_price",
        "max_price",
        "min_year",
        "max_year",
        "min_mileage",
        "max_mileage",
        "min_airbags",
        "max_airbags",
        "available_only",
        "keywords",
    ],
}


def _choice_text(title, choices):
    values = []
    for key, label in choices:
        values.append(f"{key} = {label}")
    return f"{title}: " + ", ".join(values)


def _brand_text():
    names = Brand.objects.values_list("name", flat=True).order_by("name")
    return "Brands: " + ", ".join(names)


def _to_decimal(value):
    if value in [None, ""]:
        return None

    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _to_int(value):
    if value in [None, ""]:
        return None

    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _normalize_money_text(text):
    """
    Converts:
    30k -> 30000
    30 thousand -> 30000
    1.5k -> 1500
    """
    if not text:
        return None

    text = text.lower().replace(",", "").replace("$", "").strip()

    match = re.search(r"(\d+(?:\.\d+)?)\s*(k|thousand)?", text)
    if not match:
        return None

    amount = Decimal(match.group(1))
    unit = match.group(2)

    if unit in ["k", "thousand"]:
        amount *= 1000

    return amount


def _local_choice_match(query, choices):
    query = query.lower()

    for key, label in choices:
        key_text = str(key).lower()
        label_text = str(label).lower()

        if key_text in query or label_text in query:
            return str(key)

    return None


def _local_fallback_filters(query):
    """
    Used if Gemini API fails or free API limit is reached.
    Handles common commands:
    under, below, less than, cheaper than, up to, within
    above, over, more than, minimum, from
    between X and Y
    """
    q = query.lower()
    filters = {
        "brand_name": None,
        "car_model": None,
        "category": None,
        "color": None,
        "fuel_type": None,
        "leather_interior": None,
        "engine_volume": None,
        "cylinders": None,
        "gear_box_type": None,
        "drive_wheels": None,
        "doors": None,
        "wheel": None,
        "min_price": None,
        "max_price": None,
        "min_year": None,
        "max_year": None,
        "min_mileage": None,
        "max_mileage": None,
        "min_airbags": None,
        "max_airbags": None,
        "available_only": None,
        "keywords": query,
    }

    # Choices
    filters["color"] = _local_choice_match(q, COLOR_CHOICES)
    filters["fuel_type"] = _local_choice_match(q, FUEL_TYPE)
    filters["category"] = _local_choice_match(q, CATEGOTY)
    filters["leather_interior"] = _local_choice_match(q, LEATHER_INTERIOR)
    filters["gear_box_type"] = _local_choice_match(q, GEAR_BOX_TYPE)
    filters["drive_wheels"] = _local_choice_match(q, DRIVE_WHEELS)
    filters["doors"] = _local_choice_match(q, DOORS)
    filters["wheel"] = _local_choice_match(q, WHEEL)

    # Brand
    for brand in Brand.objects.all():
        if brand.name.lower() in q:
            filters["brand_name"] = brand.name
            break

    # Price: between 20k and 40k
    between_price = re.search(
        r"(?:between|from)\s+(\d+(?:\.\d+)?\s*(?:k|thousand)?)\s+(?:and|to)\s+(\d+(?:\.\d+)?\s*(?:k|thousand)?)",
        q,
    )
    if between_price:
        filters["min_price"] = float(_normalize_money_text(between_price.group(1)))
        filters["max_price"] = float(_normalize_money_text(between_price.group(2)))

    # Price: under/below/less than/cheaper than/up to/within 30k
    max_price = re.search(
        r"(?:under|below|less than|cheaper than|up to|within|max|maximum)\s+(\d+(?:\.\d+)?\s*(?:k|thousand)?)",
        q,
    )
    if max_price:
        filters["max_price"] = float(_normalize_money_text(max_price.group(1)))

    # Price: above/over/more than/minimum/from 20k
    min_price = re.search(
        r"(?:above|over|more than|minimum|min|from)\s+(\d+(?:\.\d+)?\s*(?:k|thousand)?)",
        q,
    )
    if min_price and not between_price:
        filters["min_price"] = float(_normalize_money_text(min_price.group(1)))

    # Year
    newer = re.search(r"(?:after|newer than|from year|year after)\s+(\d{4})", q)
    older = re.search(r"(?:before|older than|year before)\s+(\d{4})", q)

    if newer:
        filters["min_year"] = int(newer.group(1))

    if older:
        filters["max_year"] = int(older.group(1))

    # Mileage
    mileage_under = re.search(
        r"(?:mileage|km|kilometer|kilometre).{0,20}(?:under|below|less than|up to)\s+(\d+)",
        q,
    )
    if mileage_under:
        filters["max_mileage"] = int(mileage_under.group(1))

    # Cylinders
    cylinders = re.search(r"(\d+)\s*(?:cylinder|cylinders)", q)
    if cylinders:
        filters["cylinders"] = int(cylinders.group(1))

    # Airbags
    airbags = re.search(r"(\d+)\s*(?:airbag|airbags)", q)
    if airbags:
        filters["min_airbags"] = int(airbags.group(1))

    # Available / sold
    if "available" in q or "unsold" in q or "not sold" in q:
        filters["available_only"] = True

    if "sold" in q and "not sold" not in q and "unsold" not in q:
        filters["available_only"] = False

    return filters


def _extract_with_gemini(query):
    api_key = getattr(settings, "GEMINI_API_KEY", None)
    model_name = getattr(settings, "GEMINI_MODEL", "gemini-2.5-flash")

    if not api_key:
        return _local_fallback_filters(query)

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are an AI search parser for a Django car dealership website.

Convert the user's natural language query into JSON filters only.

Important rules:
1. Do not invent missing values.
2. If a value is missing, return null.
3. Use only database-compatible values from the available choices.
4. For brand_name, return the brand name text, not ID.
5. For color, fuel_type, category, leather_interior, gear_box_type, drive_wheels, doors, and wheel, return the CHOICE KEY, not the display label.
6. Convert 30k, 30 thousand, and 30,000 to 30000.
7. under / below / less than / cheaper than / up to / within = max value.
8. above / over / more than / minimum / from = min value.
9. between 20k and 40k = min_price 20000 and max_price 40000.
10. newer than / after 2018 = min_year 2018.
11. older than / before 2020 = max_year 2020.
12. low mileage under 50000 km = max_mileage 50000.
13. available / not sold / unsold = available_only true.
14. sold cars = available_only false.
15. If a remaining useful keyword exists, put it in keywords.
16. Return JSON only.
17. For pickup car, pickup truck, or pick-up, return category using the closest valid category key and set keywords to null.
18. For minivan, mini van, van, or MPV, return category using the closest valid category key and set keywords to null.
19. For SUV car, sedan car, hatchback car, jeep car, return category using the closest valid category key and set keywords to null.
20. Do not put category words into keywords if category is already detected.
21. Do not put color words into keywords if color is already detected.
22. Do not put brand words into keywords if brand_name is already detected.

Available database values:
{_brand_text()}
{_choice_text("Categories", CATEGOTY)}
{_choice_text("Leather Interior", LEATHER_INTERIOR)}
{_choice_text("Fuel Types", FUEL_TYPE)}
{_choice_text("Gearbox Types", GEAR_BOX_TYPE)}
{_choice_text("Drive Wheels", DRIVE_WHEELS)}
{_choice_text("Doors", DOORS)}
{_choice_text("Wheel", WHEEL)}
{_choice_text("Colors", COLOR_CHOICES)}

User query:
{query}
"""

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json",
            response_schema=AI_FILTER_SCHEMA,
        ),
    )

    return json.loads(response.text)


def extract_ai_filters(query):
    """
    Cached AI filter extraction.
    This prevents repeated Gemini API calls when sidebar filters are changed.
    """
    query = query.strip()

    if not query:
        return None

    cache_key = "ai_car_search:" + query.lower()
    cached = cache.get(cache_key)

    if cached:
        return cached

    try:
        filters = _extract_with_gemini(query)
    except Exception as error:
        logger.exception("Gemini AI search failed. Using local fallback. Error: %s", error)
        filters = _local_fallback_filters(query)

    cache.set(cache_key, filters, timeout=60 * 30)
    return filters


def _normalize_text(value):
    if value in [None, ""]:
        return ""

    return str(value).strip().lower().replace("-", " ")


def _clean_generic_words(value):
    text = _normalize_text(value)

    generic_words = [
        "car",
        "cars",
        "vehicle",
        "vehicles",
        "auto",
        "autos",
        "automobile",
        "automobiles",
    ]

    for word in generic_words:
        text = re.sub(rf"\b{word}\b", "", text)

    return " ".join(text.split())


def _choice_key(value, choices):
    """
    Converts AI-returned value into valid Django choice key.

    Works for:
    - exact key
    - exact label
    - pickup car -> pickup
    - mini van -> minivan
    - pickup truck -> pickup
    """
    if value in [None, ""]:
        return None

    raw = _normalize_text(value)
    cleaned = _clean_generic_words(raw)

    possible_values = {raw, cleaned}

    synonyms = {
        "pickup truck": "pickup",
        "pick up": "pickup",
        "pick up truck": "pickup",
        "pickup car": "pickup",
        "mini van": "minivan",
        "mini bus": "minivan",
        "mpv": "minivan",
        "van": "minivan",
        "suv car": "suv",
        "jeep car": "jeep",
        "sedan car": "sedan",
        "hatchback car": "hatchback",
    }

    if raw in synonyms:
        possible_values.add(synonyms[raw])

    if cleaned in synonyms:
        possible_values.add(synonyms[cleaned])

    for key, label in choices:
        key_text = _normalize_text(key)
        label_text = _normalize_text(label)

        for item in possible_values:
            if item == key_text or item == label_text:
                return key

    for key, label in choices:
        key_text = _normalize_text(key)
        label_text = _normalize_text(label)

        for item in possible_values:
            if item and (item in key_text or item in label_text or key_text in item or label_text in item):
                return key

    return None


def _has_structured_filters(filters):
    structured_keys = [
        "brand_name",
        "car_model",
        "category",
        "color",
        "fuel_type",
        "leather_interior",
        "engine_volume",
        "cylinders",
        "gear_box_type",
        "drive_wheels",
        "doors",
        "wheel",
        "min_price",
        "max_price",
        "min_year",
        "max_year",
        "min_mileage",
        "max_mileage",
        "min_airbags",
        "max_airbags",
        "available_only",
    ]

    for key in structured_keys:
        value = filters.get(key)

        if value not in [None, "", []]:
            return True

    return False


def apply_ai_filters(queryset, filters):
    if not filters:
        return queryset

    brand_name = filters.get("brand_name")
    car_model = filters.get("car_model")

    # Normalize choice fields safely
    category = _choice_key(filters.get("category"), CATEGOTY)
    color = _choice_key(filters.get("color"), COLOR_CHOICES)
    fuel_type = _choice_key(filters.get("fuel_type"), FUEL_TYPE)
    leather_interior = _choice_key(filters.get("leather_interior"), LEATHER_INTERIOR)
    gear_box_type = _choice_key(filters.get("gear_box_type"), GEAR_BOX_TYPE)
    drive_wheels = _choice_key(filters.get("drive_wheels"), DRIVE_WHEELS)
    doors = _choice_key(filters.get("doors"), DOORS)
    wheel = _choice_key(filters.get("wheel"), WHEEL)

    engine_volume = filters.get("engine_volume")
    cylinders = _to_int(filters.get("cylinders"))

    min_price = _to_decimal(filters.get("min_price"))
    max_price = _to_decimal(filters.get("max_price"))

    min_year = _to_int(filters.get("min_year"))
    max_year = _to_int(filters.get("max_year"))

    min_mileage = _to_int(filters.get("min_mileage"))
    max_mileage = _to_int(filters.get("max_mileage"))

    min_airbags = _to_int(filters.get("min_airbags"))
    max_airbags = _to_int(filters.get("max_airbags"))

    available_only = filters.get("available_only")
    keywords = filters.get("keywords")

    if brand_name:
        queryset = queryset.filter(brand__name__icontains=brand_name)

    if car_model:
        queryset = queryset.filter(car_model__icontains=car_model)

    if category:
        queryset = queryset.filter(category=category)

    if color:
        queryset = queryset.filter(color=color)

    if fuel_type:
        queryset = queryset.filter(fuel_type=fuel_type)

    if leather_interior:
        queryset = queryset.filter(leather_interior=leather_interior)

    if engine_volume:
        queryset = queryset.filter(engine_volume__icontains=engine_volume)

    if cylinders is not None:
        queryset = queryset.filter(cylinders=cylinders)

    if gear_box_type:
        queryset = queryset.filter(gear_box_type=gear_box_type)

    if drive_wheels:
        queryset = queryset.filter(drive_wheels=drive_wheels)

    if doors:
        queryset = queryset.filter(doors=doors)

    if wheel:
        queryset = queryset.filter(wheel=wheel)

    if min_price is not None:
        queryset = queryset.filter(price__gte=min_price)

    if max_price is not None:
        queryset = queryset.filter(price__lte=max_price)

    if min_year is not None:
        queryset = queryset.filter(prod_year__gte=min_year)

    if max_year is not None:
        queryset = queryset.filter(prod_year__lte=max_year)

    if min_mileage is not None:
        queryset = queryset.filter(mileage__gte=min_mileage)

    if max_mileage is not None:
        queryset = queryset.filter(mileage__lte=max_mileage)

    if min_airbags is not None:
        queryset = queryset.filter(airbags__gte=min_airbags)

    if max_airbags is not None:
        queryset = queryset.filter(airbags__lte=max_airbags)

    if available_only is True:
        queryset = queryset.filter(is_sold=False)

    if available_only is False:
        queryset = queryset.filter(is_sold=True)

    # Important fix:
    # Keywords should work only as fallback.
    # If structured filters already exist, do not apply keywords.
    if keywords and not _has_structured_filters(filters):
        cleaned_keywords = _clean_generic_words(keywords)

        if cleaned_keywords:
            queryset = queryset.filter(
                Q(car_model__icontains=cleaned_keywords)
                | Q(description__icontains=cleaned_keywords)
                | Q(brand__name__icontains=cleaned_keywords)
                | Q(category__icontains=cleaned_keywords)
                | Q(color__icontains=cleaned_keywords)
                | Q(fuel_type__icontains=cleaned_keywords)
            )

    return queryset