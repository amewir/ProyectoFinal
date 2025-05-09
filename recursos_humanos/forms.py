from django import forms
from .models import Empleado, Nomina, SolicitudViaje
from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.models import User
User = get_user_model()
from django import forms
from django.contrib.auth import get_user_model
from .models import Empleado, Nomina, SolicitudViaje

User = get_user_model()

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class EmpleadoForm(forms.ModelForm):
    fecha_contratacion = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    salario_base = forms.DecimalField(widget=forms.NumberInput(attrs={'step': '0.01'}))

    class Meta:
        model = Empleado
        fields = ['puesto', 'fecha_contratacion', 'salario_base', 'departamento', 'activo']

   
class EmpleadoCreacionForm(forms.ModelForm):
    email = forms.EmailField()
    username = forms.CharField()
    fecha_contratacion = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    salario_base = forms.DecimalField(widget=forms.NumberInput(attrs={'step': '0.01'}))

    class Meta:
        model = Empleado
        fields = ['username', 'email', 'puesto', 'fecha_contratacion', 'salario_base', 'departamento', 'activo']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("El nombre de usuario ya está en uso.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está en uso.")
        return email

    def save(self, commit=True):
        # Crear un nuevo usuario
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password='usuario123'  # Puedes cambiar esta contraseña a algo más seguro
        )

        # Guardar el empleado con la referencia al usuario creado
        empleado = super().save(commit=False)
        empleado.usuario = user

        if commit:
            empleado.save()

        return empleado


    
class NominaForm(forms.ModelForm):
    class Meta:
        model = Nomina
        fields = ['empleado', 'horas_extras', 'bonos', 'deducciones']
        widgets = {
            'horas_extras': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'bonos': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'deducciones': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
        }
        labels = {
            'horas_extras': 'Horas Extras',
            'bonos': 'Bonos (Q)',
            'deducciones': 'Deducciones (Q)'
        }
class SolicitudViajeForm(forms.ModelForm):
    class Meta:
        model = SolicitudViaje
        fields = ['empleado', 'destino', 'fecha_inicio', 'fecha_fin', 'motivo', 'presupuesto']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
            'presupuesto': forms.NumberInput(attrs={'step': '0.01'}),
        }

    empleado = forms.ModelChoiceField(queryset=Empleado.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))


