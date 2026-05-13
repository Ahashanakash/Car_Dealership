from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import BrandViewSet, CarViewSet, CarVideoViewSet
# from django.views.generic import TemplateView
from .views import *

router = DefaultRouter()

router.register('brands', BrandViewSet)
router.register('cars', CarViewSet)
router.register('videos', CarVideoViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('', CarList.as_view(), name='cars'),
    path('details/<int:pk>/', CarDetails.as_view(), name='car_details'),
    path('car/<int:pk>/like/', toggle_like, name='toggle_like'),
    path("car/<int:car_id>/", review_list, name="review_list"),
    path("modal/<int:car_id>/",review_modal, name="review-modal"),
    path("save/<int:car_id>/",review_save, name="review-save"),

]
