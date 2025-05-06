from django import forms
from .models import Mascota

class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = ['nombre', 'especie', 'raza', 'edad', 'peso', 'foto', 'historial_medico']
        widgets = {
            'historial_medico': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Alergias, tratamientos previos...'
            }),
            'edad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'peso': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1'
            }),
            'foto': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }