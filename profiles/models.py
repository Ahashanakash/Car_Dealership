from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
# from .constants import GENDER_CHOICES

# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        # Create and saves an User with the given email and password
        if not email:
            raise ValueError("User must have an email address")
        if not username:
            raise ValueError("User must have a username")
        if not password:
            raise ValueError("User must have a password")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff = True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser = True.')

        user = self.create_user(email, username, password, **extra_fields)
        # user.is_staff = True
        # user.is_superuser = True
        user.is_customer = True
        user.is_seller = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True, blank=False)
    username = models.CharField(max_length=255, unique=True, blank=False)
    # Only allows letters and space (no numbers or special characters)
    first_name = models.CharField(max_length=255, blank=True,
                                  validators=[RegexValidator(
                                      r'^[a-zA-Z ]+$', 'Enter a valid name (letters only).')],
                                  )

    last_name = models.CharField(max_length=255, blank=True,
                                 validators=[RegexValidator(
                                     r'^[a-zA-Z ]+$', 'Enter a valid name (letters only).')],
                                 )
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    phone = models.CharField(blank=True,
        max_length=11,
        validators=[
            RegexValidator(r'^01\d{9}$', 'Phone number must start with 01 and be exactly 11 digits.'
                           )
        ]
    )
    is_phone_verified = models.BooleanField(default=False)
    # is_superuser = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=True)
    is_seller = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    #createsuperuser asks for username
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.email
    
    class Meta:
        ordering = ["-created_at"]
        
        
        
class Profile(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField(blank=True)
    photo = models.ImageField(upload_to='profiles/profile_photos/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,   # Allow blank if you want it optional
        null=True,    # Allow null in database if you want it optional
        verbose_name="Gender"
    )
    def __str__(self):
        return self.user.username
    
    
class Purchase(models.Model):
    car = models.OneToOneField('cars.Car',on_delete=models.CASCADE,related_name='purchase')
    buyer = models.ForeignKey(User,on_delete=models.CASCADE,related_name='purchases')
    purchased_at = models.DateTimeField(auto_now_add=True)
    price_paid = models.DecimalField(max_digits=90000000, decimal_places=2)
    purchased_type = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.car} bought by {self.buyer}"