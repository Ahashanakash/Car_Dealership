from django.urls import path
from .views import find_us

urlpatterns = [
    path("find-us/",find_us,name="find_us"),
]