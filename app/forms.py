from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.forms import ModelForm

from .models import Transaction


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

class TransactionForm(ModelForm):
    class Meta:
        model = Transaction
        fields = ['user', 'lotto', 'share']
