from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import Profile


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control'}))  # default reqd = true

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        name = self.cleaned_data['username']
        email_exists = User.objects.filter(email=email)
        if 'inbov03.com' in email:
            raise ValidationError('"inbov03.com" is not allowed')
        for user in email_exists:
            if email_exists and user.username != name:
                raise ValidationError("This email is already registered")

        return email


class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['about_author', 'image']
