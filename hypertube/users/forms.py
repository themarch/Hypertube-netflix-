from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from .models import Profile
import requests

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    last_name = forms.CharField(strip=True)
    first_name = forms.CharField(strip=True)
    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) <= 8:
            raise forms.ValidationError("Your login must have 9 character at least")
        if len(username) >= 18:
            raise forms.ValidationError("Your login must have 18 character maximum")
        return username  # Ne pas oublier de renvoyer le contenu du champ traité
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class EmailValidationOnForgotPassword(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email):
            user = User.objects.get(email=email)
            if user and user.password and check_password('', user.password):
                raise ValidationError("You can't reset your password, register with social")
        else:
            raise ValidationError("You can't reset your password, register with social")
        return email

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']

class UserUpdateMailForm(forms.ModelForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']
    
class ProfileUpdateLanguage(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['language']

class UserUpdateCheck(UserUpdateForm):
    #def clean_email(self):
    #    data = self.cleaned_data['email']
    #    if User.objects.filter(email=data).count() > 0:
    #        raise forms.ValidationError("We have a user with this user email-id")
    #    return data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        username_qs = User.objects.filter(username=username)
        if username_qs.exists():
            raise ValidationError("Username already exists")
        if len(username) <= 8:
            raise forms.ValidationError("Your login must have 9 character at least")
        return username