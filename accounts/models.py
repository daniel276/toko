from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
    ('admin', 'Admin'),
    ('supervisor', 'Supervisor'),
    ('staff', 'Staff'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff')
    pin_code = models.CharField(max_length=4, blank=True, null=True)


