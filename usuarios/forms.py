from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import Usuario
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

class RegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2']
        
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )
    biometrico = forms.BooleanField(
        required=False,
        label="Iniciar con reconocimiento facial",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        try:
            user = Usuario.objects.get(username=username)
            if user.bloqueado:
                raise ValidationError("Cuenta bloqueada. Contacta al administrador.")
                
            if user.intentos_fallidos >= 3:
                user.bloqueado = True
                user.save()
                raise ValidationError("Demasiados intentos fallidos. Cuenta bloqueada.")

        except Usuario.DoesNotExist:
            raise ValidationError("Credenciales inválidas")

        return super().clean()