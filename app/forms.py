from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm

from .models import Transaction


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class TransactionForm(ModelForm):
    class Meta:
        model = Transaction
        fields = ['user', 'lotto', 'share']
