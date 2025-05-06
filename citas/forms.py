from django import forms
from .models import Cita
from mascotas.models import Mascota  # Importación necesaria para el filtrado

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['mascota', 'servicio', 'fecha', 'hora', 'notas']
        widgets = {
            'fecha': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'Seleccione una fecha'
            }),
            'hora': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'placeholder': 'Seleccione una hora'
            }),
            'notas': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Ingrese notas adicionales...'
            }),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrado de mascotas del usuario actual
        self.fields['mascota'].queryset = Mascota.objects.filter(dueno=user)
        
        # Estilizado uniforme para todos los campos
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'style': 'margin-bottom: 15px;'
            })
            
        # Mejora para el campo servicio
        self.fields['servicio'].empty_label = "Seleccione un servicio"
        
        # Ordenar opciones alfabéticamente
        self.fields['servicio'].queryset = self.fields['servicio'].queryset.order_by('nombre')