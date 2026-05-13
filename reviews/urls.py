from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .api_views import ReviewViewSet

app_name = "review"

router = DefaultRouter()
router.register('reviews', ReviewViewSet)


urlpatterns = [
    path('api/', include(router.urls)),
    # path("car/<int:car_id>/", views.review_list, name="review_list"),
    # path("modal/<int:car_id>/", views.review_modal, name="review-modal"),
    # path("save/<int:car_id>/", views.review_save, name="review-save"),
]