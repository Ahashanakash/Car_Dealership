from rest_framework import serializers
from .models import Brand, Car, CarVideo


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'


class CarSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)

    class Meta:
        model = Car
        fields = '__all__'


class CarVideoSerializer(serializers.ModelSerializer):
    model_name = CarSerializer(read_only=True)

    class Meta:
        model = CarVideo
        fields = '__all__'