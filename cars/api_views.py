from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Brand, Car, CarVideo
from .serializers import BrandSerializer, CarSerializer, CarVideoSerializer

class CarPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50
    
    
class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = CarPagination


class CarVideoViewSet(viewsets.ModelViewSet):
    queryset = CarVideo.objects.all()
    serializer_class = CarVideoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]