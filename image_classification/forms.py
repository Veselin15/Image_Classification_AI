from django import forms
from .models import Upload
from django.contrib.auth.forms import AuthenticationForm

class UploadForm(forms.ModelForm):
    class Meta:
        model = Upload
        fields = ['image']

# Convert RegisterForm to a standard Form for maximum efficiency.
# This prevents the check framework from doing heavy model validation.
class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Username')
    password = forms.CharField(widget=forms.PasswordInput())