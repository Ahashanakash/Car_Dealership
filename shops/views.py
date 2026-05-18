from django.shortcuts import render
from .models import Shop
import json

from django.shortcuts import render
from .models import Shop
from django.conf import settings
import json


def find_us(request):
    shops = Shop.objects.all()

    shop_data = [
        {
            "name": shop.name,
            "lat": shop.latitude,
            "lng": shop.longitude
        }
        for shop in shops
    ]

    return render(request, "shops/find_us.html", {
        "shops_json": json.dumps(shop_data),
    })