from django.urls import path
from .views import CustomerDashBoardView

urlpatterns = [
    path('customer_dashboard/', CustomerDashBoardView.as_view(), name='customer_dashboard'),
    
]