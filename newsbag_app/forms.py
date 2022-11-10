from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from newsbag_app.models import Library


class Register(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',)


class LibraryForm(forms.ModelForm):
    name = forms.CharField()

    class Meta:
        model = Library

        fields = [
            "name"
        ]
