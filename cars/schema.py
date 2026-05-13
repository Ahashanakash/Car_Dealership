import graphene
from graphene_django import DjangoObjectType
from .models import Car

class carinfo(DjangoObjectType):
    class Meta:
        model = Car
        fields = ('brand',
            'car_model',
            'category',
            'image',
            'prod_year',
            'price',
            'levy',
            'mileage',
            'fuel_type',
            'gear_box_type',
            'description',
            'color',
            'leather_interior',
            'drive_wheels',
            'doors',
            'wheel',
            'engine_volume',
            'cylinders',
            'airbags',)

class Query(graphene.ObjectType):
    all_cars = graphene.List(carinfo)
    def resolve_all_cars(root, info):
        # We can easily optimize query count in the resolve method
        return Car.objects.all()

schema = graphene.Schema(query=Query)