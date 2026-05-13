from django.urls import path,include
from .views import ValidatePassword, ValidateUsername, ValidateEmail, SignupView, activate_account, LoginView, ProfileView, CustomerPasswordResetView, PasswordResetConfirmView, ProfilePasswordChangeView, custom_logout
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('login')), name='logout'),
    path('register/', SignupView.as_view(), name='signup'),
    path('password_reset/', CustomerPasswordResetView.as_view(), name='password_reset'),
    path('password_reset_confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('activate/<str:uidb64>/<str:token>/', activate_account, name='activate'),
    path('password_change/', ProfilePasswordChangeView.as_view(), name='password_change'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('validate-username/', ValidateUsername.as_view(), name='validate_username'),
    path('validate-email/', ValidateEmail.as_view(), name='validate_email'),
    path('validate-password/', ValidatePassword.as_view(), name='validate_password'),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('logout/', custom_logout, name='logout'),
]