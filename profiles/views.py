# from urllib import request
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import FormView
from .forms import SignUpform, PasswordResetForm
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import SetPasswordForm
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from profiles.models import User
from profiles.utils import send_activation_email, send_reset_password_email
from django.contrib.auth.password_validation import validate_password, get_default_password_validators
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.views import View
from django.views.generic import FormView
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.views import View
from .forms import ProfilePasswordChangeForm
from django.views.generic import TemplateView
from django.core.exceptions import ValidationError
from .forms import PersonalInfoForm
from .models import Profile
from django.contrib.auth import logout

# utils.py (or inside views.py)
from django.shortcuts import redirect

# def unauthenticated_user(view_func):
#     def wrapper(request, *args, **kwargs):
#         if request.user.is_authenticated:
#             return redirect('customer_dashboard')
#         else:
#             return view_func(request, *args, **kwargs)
#     return wrapper

# @method_decorator(unauthenticated_user, name='dispatch')
class SignupView(FormView):
    form_class = SignUpform
    template_name = 'profiles/signup.html'

    def form_valid(self, form):
        user = form.save(commit=False)
        # user.set_password(form.cleaned_data['password'])
        user.is_active = False
        role = form.cleaned_data['role']
        if role=="seller":
            user.is_seller = True
            user.is_customer = False
        else:
            user.is_seller = False
            user.is_customer = True
        user.save()

        # Send Account Activation Email
        uidb64 = urlsafe_base64_encode(force_bytes(user. pk))
        token = default_token_generator.make_token(user)
        activation_link = reverse(
            'activate', kwargs={'uidb64': uidb64, 'token': token})
        activation_url = f'{settings.SITE_DOMAIN}{activation_link}'
        send_activation_email(user.email, activation_url)
        messages.success(
            self.request, 'Signup successful! Please check your email to activate account.')
        return redirect('login')


def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):

        if user.is_active:
            messages.warning(request, "This account is already activated.")
            return redirect('login')

        user.is_active = True
        user.save()

        messages.success(request, "Your account has been activated successfully!")
        return redirect('login')

    else:
        messages.error(request, "Invalid or expired activation link.")
        return redirect('login')


# method_decorator(unauthenticated_user, name='dispatch')
class LoginView(View):
    def dispatch(self, request, *args, **kwargs): 
        if request.user.is_authenticated:
            if request.user.is_seller:
                return redirect('seller:seller_dashboard')
            elif request.user.is_customer:
                return redirect('customer_dashboard') 
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        return render(request, 'profiles/login.html')

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            messages.error(request, "Bothe fields are required.")
            return redirect('login')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return redirect('login')

        if not user.is_active:
            messages.error(
                request, "Yor account is inactive. Please activate your account.")
            return redirect('login')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            if user.is_seller:
                return redirect('seller:seller_dashboard')
            elif user.is_customer:
                return redirect('home')
            else:
                messages.error(
                    request, "You do not have permission to access this area.")
                return redirect('home')
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('login')



        return super().form_invalid(form)


from django.contrib.auth import logout
from django.shortcuts import redirect

from django.contrib.auth import logout
from django.shortcuts import redirect

def custom_logout(request):
    if request.method == "POST":
        # 1. Save the cart data from the old session
        cart = request.session.get('cart')

        # 2. Flush the old session (clears user auth and data)
        logout(request)

        # 3. Restore the cart to the NEW session
        if cart:
            request.session['cart'] = cart
            # FORCE Django to save this new session immediately
            request.session.modified = True 

    return redirect('home')

        
    
class CustomerPasswordResetView(FormView):
    template_name = 'profiles/c_pass_reset.html'
    form_class = PasswordResetForm
    success_url = reverse_lazy('login')
    success_message = ('We have sent you a password reset link. Please check your email.')
    
    def form_valid(self, form):
        email = form.cleaned_data.get('email')

        user = User.objects.filter(email=email).first()

        if user:
            reset_url = self.get_reset_url(user)
            send_reset_password_email(user.email, reset_url)

        messages.success(
            self.request,
            "If this email exists, a password reset link has been sent."
        )

        return super().form_valid(form)
    
    
    def get_reset_url(self, user):
        uid = urlsafe_base64_encode(force_bytes(user.pk)) 
        token = default_token_generator.make_token(user) 
        reset_url = reverse('password_reset_confirm',
                                kwargs={'uidb64': uid, 'token': token})
        return f"{self.request.build_absolute_uri(reset_url)}" 
    
    
class PasswordResetConfirmView(View):
    template_name = 'profiles/password_reset_confirm.html'
    
    def get(self, request, uidb64, token, *args, **kwargs): 
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
            # Check the token
            if default_token_generator.check_token(user, token):
                form = SetPasswordForm (user=user)
                return render(request, self.template_name, {'form': form, 'uidb64': uidb64, 'token': token})
            else:
                messages.error(request, ('This link has expired or is invalid.'))
                return redirect('password_reset')
            
        except Exception as e:
            print("Password reset error:", e)
            messages.error(request, ('An error occured. Please try again later.'))
            return redirect('password_reset')
            
    
    
    def post(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
            # Check the token
            if default_token_generator.check_token (user, token):
                form = SetPasswordForm(user=user, data=request.POST)
                if form.is_valid():
                    form.save()
                    messages.success(request,('Your password has been successfully reset.'))
                    return redirect ('login')
                else:
                    for field, errors in form.errors.items():
                        for error in errors:
                            messages.error(request,error)
                    return render(request, self.template_name,{'form':form, 'uidb64':uidb64, 'token':token})
            else:
                messages.error(request, ('This link has expired or is invalid.'))
                return redirect('password_reset')
            
        except Exception as e:
            messages.error(request,('An error occured. PLease try again later.'))
            return redirect('password_reset')
        
        
        
class ProfilePasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = ProfilePasswordChangeForm
    template_name = 'profiles/password_change.html'
    success_url = reverse_lazy('profile') 

    def form_valid(self, form):
        messages.success(self.request, 'Password updated successfully')
        update_session_auth_hash(self.request, form.user)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Wrong password or invalid input')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'Change password'
        return context
    
    
class ProfileView(LoginRequiredMixin, View):
    template_name = 'profiles/profile.html'

    def get(self, request):
        form = PersonalInfoForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = PersonalInfoForm(
            request.POST,
            request.FILES,
            instance=request.user
        )

        if form.is_valid():
            form.save()
            return redirect('profile')
        print(form.errors)
        return render(request, self.template_name, {'form': form})
        
    
class ValidateUsername(View):
    def get(self, request):
        username = request.GET.get('username', '')
        if username:
            exists = User.objects.filter(username__iexact=username).exists()
            if exists:
                return HttpResponse('<small class="text-danger">Username already taken</small>')
            else:
                return HttpResponse('<small class="text-success">Username available</small>')
        return HttpResponse('')

class ValidateEmail(View):
    def get(self, request):
        email = request.GET.get('email', '')
        if email:
            exists = User.objects.filter(email__iexact=email).exists()
            if exists:
                return HttpResponse('<small class="text-danger">Email already registered</small>')
            else:
                return HttpResponse('<small class="text-success">Email available</small>')
        return HttpResponse('')
    
    
class ValidatePassword(View):
    def get(self, request):
        password1 = request.GET.get('password1', '')
        password2 = request.GET.get('password2', '')

        errors = []

        # Validate password using Django's built-in validators
        try:
            validate_password(password1, password=None, password_validators=get_default_password_validators())
        except ValidationError as e:
            errors.extend(e.messages)

        # Check confirm password
        if password2 and password1 != password2:
            errors.append("Passwords do not match.")

        # Build HTML
        if errors:
            html = ''.join([f'<div class="text-danger">{msg}</div>' for msg in errors])
        else:
            html = '<div class="text-success">Password looks good!</div>'

        return HttpResponse(html)
    
    

