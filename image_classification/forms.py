from django import forms
from .models import Upload
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

class UploadForm(forms.ModelForm):
    class Meta:
        model = Upload
        fields = ['image']

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'off'}))
    class Meta:
        model = User
        fields = ['username', 'password']

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Username')
    password = forms.CharField(widget=forms.PasswordInput())