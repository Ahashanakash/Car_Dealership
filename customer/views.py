from django.shortcuts import render
from django.contrib.auth import logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import TemplateView
# from .forms import PasswordResetForm
from django.contrib.auth.mixins import LoginRequiredMixin

from profiles.mixins import IsCustomerMixin

# Create your views here.

class CustomerDashBoardView(LoginRequiredMixin,IsCustomerMixin, TemplateView):
    template_name = 'customer_dashboard.html'
    # def get(self, request, *args, **kwargs):
    #     return render(request, 'profiles/login.html')
    
    # # def post(self, request, *args, **kwargs):
        