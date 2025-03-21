from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'}))
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords do not match")
        return cleaned_data
