from django.urls import path
from .views import *
app_name = 'seller'
urlpatterns = [
    path('dashboard/', SellerDashBoardView.as_view(), name='seller_dashboard'),
    path('dashboard/add-car/', add_car_htmx, name='add-car'),
    path('dashboard/your-cars/', your_cars_htmx, name='your-cars'),
    path('dashboard/update-car/<int:pk>/', update_car_htmx, name='update-car'),
    path('dashboard/delete-car/<int:pk>/', delete_car_htmx, name='delete-car'),
    path('dashboard/add-video/<int:pk>/', add_video_htmx, name='add-video'),
]