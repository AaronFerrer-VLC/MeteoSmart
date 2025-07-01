# clima/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class BuscarCiudadForm(forms.Form):
    ciudad = forms.CharField(
        label="Ciudad",
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Introduce ciudad'})
    )
