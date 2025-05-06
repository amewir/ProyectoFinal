from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
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
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        if username and password:
            try:
                user = Usuario.objects.get(username=username)
                
                if user.bloqueado:
                    raise ValidationError("Cuenta bloqueada. Contacta al administrador.")
                
                if not user.check_password(password):
                    user.intentos_fallidos += 1
                    user.save()
                    
                    if user.intentos_fallidos >= 3:
                        user.bloqueado = True
                        user.save()
                        raise ValidationError("Demasiados intentos fallidos. Cuenta bloqueada.")
                    
                    raise ValidationError("Credenciales inválidas")
                
                # Resetear intentos si el login es exitoso
                user.intentos_fallidos = 0
                user.save()

            except Usuario.DoesNotExist:
                raise ValidationError("Credenciales inválidas")

        return cleaned_data

class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'telefono','dpi'] 
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'dpi': forms.TextInput(attrs={'class': 'form-control'}),
        }