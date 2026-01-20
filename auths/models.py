from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=250, default='')
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=8, null=True, blank=True)
    status = models.BooleanField(default=False)

    phone = models.CharField(max_length=15, null=True, blank=True)
    is_email_varified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=True)

    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(null=True, blank=True, upload_to="profile")

    last_activity = models.DateTimeField(null=True, blank=True)
    
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    ## Delevary Address
    country_or_region = models.CharField(max_length=250, null=True, blank=True)
    address_line_i = models.CharField(max_length=250, null=True, blank=True)
    address_line_ii = models.CharField(max_length=250, null=True, blank=True)
    suburb = models.CharField(max_length=250, null=True, blank=True)
    city = models.CharField(max_length=250, null=True, blank=True)
    postal_code = models.CharField(max_length=250, null=True, blank=True)
    state = models.CharField(max_length=250, null=True, blank=True)
    
    def __str__(self):
        return self.email + self.username