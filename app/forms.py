<<<<<<< HEAD
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm

from .models import Transaction
from .models import Account

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MaxLengthValidator

class SignUpForm(UserCreationForm):
    banknumber = forms.CharField(
        max_length=10,
        min_length=10,
        validators=[MinLengthValidator(10), MaxLengthValidator(10)],
        widget=forms.TextInput(attrs={'placeholder': 'Enter 10-digit bank number'})
    )
    
    bankname = forms.CharField(
        max_length=50,
        widget=forms.Select(
            choices=[
                ('ธนาคารกรุงเทพ', 'Bangkok Bank'),
                ('ธนาคารกสิกรไทย', 'Kasikorn Bank'),
                ('ธนาคารไทยพาณิชย์', 'Siam Commercial Bank'),
                ('ธนาคารกรุงไทย', 'Krung Thai Bank'),
                ('ธนาคารทหารไทยธนชาต', 'TMB Bank'),
                ('ธนาคารออมสิน', 'Government Savings Bank'),
                ('ยูโอบี ประเทศไทย', 'UOB Thailand'),
                ('ซิตี้แบงก์ ประเทศไทย', 'CitiBank Thailand'),
            ]
        ),  
    )
    
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'banknumber', 'bankname']
        
    def clean_banknumber(self):
        banknumber = self.cleaned_data.get('banknumber')
        if len(banknumber) != 10:
            raise forms.ValidationError('Bank number must be exactly 10 digits.')
        return banknumber


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['banknumber', 'bankname']


class TransactionForm(ModelForm):
    class Meta:
        model = Transaction
        fields = ['user', 'lotto', 'share']
=======
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
    
    # Custom error messages
    error_messages = {
        'username': {
            'required': 'Please provide a username.',
            'max_length': 'Your username is too long. Please keep it under 150 characters.',
            'unique': 'This username is already taken. Please choose another one.'
        },
        'email': {
            'required': 'An email address is required to complete registration.',
            'invalid': 'Please provide a valid email address.'
        },
        'password1': {
            'required': 'A password is required.',
            'min_length': 'Your password must be at least 8 characters long.',
        },
        'password2': {
            'required': 'Please confirm your password.',
            'invalid': 'Passwords do not match. Please try again.',
        }
    }


    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two password fields must match.")
        return password2
>>>>>>> cd22856e6f14c9c66eb86c679667a4276cccc41d
