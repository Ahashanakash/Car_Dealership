from django import forms
from profiles.models import User, Profile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
# from .constants import GENDER_CHOICES
import re

class SignUpform(UserCreationForm):
    ROLE_CHOICE = (('customer','Customer'),('seller','Seller'))
    role = forms.ChoiceField(choices=ROLE_CHOICE,widget=forms.Select)
    password1 = forms.CharField(label="Password",widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password",widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username","first_name","last_name","email"]
        
    # clean_fieldname() used to validate a single field from model
    def clean_email(self):
        email = self.cleaned_data.get('email') # cleaned_data is comming from clean()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exist!")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "A user with this username already exists."
            )
        return username
    
    
class PersonalInfoForm(forms.ModelForm):
    address = forms.CharField(widget=forms.Textarea, required=False)
    photo = forms.ImageField(
    required=False,
    widget=forms.FileInput(attrs={
        "class": "form-control"
    })
)
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    gender = forms.ChoiceField(
        choices=Profile.GENDER_CHOICES,
        required=False
    )

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'phone',
        ]

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')

        if first_name and not first_name.replace(" ", "").isalpha():
            raise forms.ValidationError(
                "First name can contain only letters and spaces."
            )

        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')

        if last_name and not last_name.replace(" ", "").isalpha():
            raise forms.ValidationError(
                "Last name can contain only letters and spaces."
            )

        return last_name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        pattern = r'^01\d{9}$'

        if phone and not re.match(pattern, phone):
            raise forms.ValidationError(
                "Phone must start with 01 and be exactly 11 digits."
            )

        return phone
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance:
            try:
                profile = self.instance.profile
            except Profile.DoesNotExist:
                profile = None

            if profile:
                self.fields['address'].initial = profile.address
                self.fields['photo'].initial = profile.photo
                self.fields['date_of_birth'].initial = profile.date_of_birth
                self.fields['gender'].initial = profile.gender

    def save(self, commit=True):
        user = super().save(commit=False)
    
        if commit:
            user.save()
    
            profile, created = Profile.objects.get_or_create(user=user)
    
            profile.address = self.cleaned_data['address']
            profile.date_of_birth = self.cleaned_data['date_of_birth']
            profile.gender = self.cleaned_data['gender']
    
            photo = self.cleaned_data.get("photo")
            if photo:
                profile.photo = photo
    
            profile.save()
    
        return user


class PasswordResetForm(forms.Form):
    email = forms.EmailField(max_length=255,
                             required=True,
                             widget=forms. EmailInput(attrs={'placeholder': 'you@example.com'}))

    def clean_email(self):
        email = self.cleaned_data.get('email')

    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check if a user with this email exists
        if not User.objects.filter(email=email).exists(): 
            raise forms.ValidationError(('No account is associated with this email address.'))
        return email
    
class ProfilePasswordChangeForm(PasswordChangeForm):
    def clean_new_password1(self):
        new_password = self.cleaned_data.get("new_password1")
        old_password = self.cleaned_data.get("old_password")

        if old_password and new_password:
            if old_password == new_password:
                raise ValidationError(
                    "New password cannot be the same as your old password."
                )
        return new_password
    
    
    