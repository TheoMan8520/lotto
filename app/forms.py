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
