from django import forms
from .models import Empleado, Nomina, SolicitudViaje

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['usuario', 'puesto', 'fecha_contratacion', 'salario_base', 'departamento']
        widgets = {
            'fecha_contratacion': forms.DateInput(attrs={'type': 'date'}),
            'salario_base': forms.NumberInput(attrs={'step': '0.01'}),
        }

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