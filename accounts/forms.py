from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    # Dynamic lookup ഒഴിവാക്കി നേരിട്ട് Text കൊടുത്തു. ഇനി Error വരില്ല.
    password_1 = forms.CharField(
        label="Password", 
        widget=forms.PasswordInput, 
        strip=False, 
        help_text="Your password can't be too similar to your other personal information."
    )
    password_2 = forms.CharField(
        label="Password confirmation", 
        widget=forms.PasswordInput, 
        strip=False, 
        help_text="Enter the same password as before, for verification."
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'role', 'phone_number')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'username', 'role', 'phone_number')