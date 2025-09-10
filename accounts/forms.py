from django import forms
from django.contrib.auth.forms import UserCreationForm

from accounts.models import CustomUser


class RegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'username', 'password1', 'password2', 'role')