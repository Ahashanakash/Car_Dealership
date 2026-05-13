from django.db import models
from .constants import *
from embed_video.fields import EmbedVideoField
from django.core.exceptions import ValidationError
from profiles.models import User
from autoslug import AutoSlugField

# Create your models here.

class Brand(models.Model):
    name = models.CharField(max_length=50, unique=True)
    logo = models.ImageField(upload_to='brands/', blank=True)
    slug = AutoSlugField(populate_from='name', max_length=100, unique=True, null=True, blank=True)

    def __str__(self):
        return self.name


class Car(models.Model):
    seller = models.ForeignKey('profiles.User', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    levy = models.IntegerField(blank=True, null=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    car_model = models.CharField(max_length=50)
    category = models.CharField(max_length=10, choices=CATEGOTY)
    leather_interior = models.CharField(max_length=10, choices=LEATHER_INTERIOR)
    fuel_type = models.CharField(max_length=10, choices=FUEL_TYPE)
    engine_volume = models.CharField(max_length= 11)
    mileage = models.PositiveIntegerField(help_text="KM driven")
    cylinders = models.IntegerField()
    gear_box_type = models.CharField(
        max_length=10, choices=GEAR_BOX_TYPE)
    drive_wheels = models.CharField(max_length=10, choices=DRIVE_WHEELS)
    serial_number = models.IntegerField(blank=True, null=True, unique=True)
    doors = models.CharField(max_length=10, choices=DOORS)
    wheel = models.CharField(max_length=30, choices=WHEEL)
    color = models.CharField(max_length=30, choices=COLOR_CHOICES)
    airbags = models.PositiveIntegerField(blank=True, null=True, )
    image = models.ImageField(upload_to='cars/')
    prod_year = models.PositiveIntegerField()
    description = models.TextField()
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField('profiles.User', related_name='liked_cars', blank=True)
    dislikes = models.ManyToManyField(User, related_name='disliked_cars', blank=True)
    slug = AutoSlugField(populate_from='category', max_length=100, unique=True, null=True, blank=True) 
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save first to get PK
        if self.serial_number is None:  # Only set if not already set
            self.serial_number = 1234 + self.pk
            super().save(update_fields=['serial_number'])  # Update serial number

    def __str__(self):
        return f"{self.car_model}"
    
class CarVideo(models.Model):
    model = models.OneToOneField(Car, on_delete=models.CASCADE)
    video = EmbedVideoField() 
    def __str__(self):
        return f"{self.model}"
    

class CarPricePrediction(models.Model):
    PRICE_STATUS = (
        ("low", "Low Price"),
        ("regular", "Regular Price"),
        ("high", "High Price"),
        ("insufficient_data", "Insufficient Data"),
    )

    car = models.OneToOneField(
        Car,
        on_delete=models.CASCADE,
        related_name="price_prediction"
    )

    predicted_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True
    )

    lower_price_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True
    )

    upper_price_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True
    )

    seller_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True
    )

    price_status = models.CharField(
        max_length=30,
        choices=PRICE_STATUS,
        default="insufficient_data"
    )

    model_mae = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True
    )

    model_r2_score = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        blank=True,
        null=True
    )

    model_mape = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.car} - {self.price_status}"