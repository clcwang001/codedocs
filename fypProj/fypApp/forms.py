
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Users

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = Users
        fields = ['email', 'username', 'password1', 'password2', 'contactNumber', 'isOrganisation']