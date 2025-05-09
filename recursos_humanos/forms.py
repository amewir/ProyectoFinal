from django import forms
from .models import Empleado, Nomina, SolicitudViaje
from django.contrib.auth.models import User

class EmpleadoForm(forms.ModelForm):
    email = forms.EmailField()
    username = forms.CharField()
    
    class Meta:
        model = Empleado
        fields = ['username', 'email', 'puesto', 'departamento']  # Corrige esta lista con tus campos reales

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password='temp_password'
        )
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


