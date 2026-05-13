from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    car = serializers.StringRelatedField(read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = '__all__'