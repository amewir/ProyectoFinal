from django import forms
from .models import Cita
from mascotas.models import Mascota
from django.core.validators import MinLengthValidator, RegexValidator
from django.core.exceptions import ValidationError

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
        self.fields['mascota'].queryset = Mascota.objects.filter(dueno=user)
        self.fields['servicio'].empty_label = "Seleccione un servicio"
        self.fields['servicio'].queryset = self.fields['servicio'].queryset.order_by('nombre')
        
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control', 'style': 'margin-bottom: 15px;'})

class SimulacionPagoForm(forms.Form):
    # Campos de facturación
    nombre = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Nombre"
    )
    
    apellido = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Apellido"
    )
    
    direccion = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label="Dirección de Facturación"
    )
    
    departamento = forms.ChoiceField(
        choices=[
            ('guatemala', 'Guatemala'),
            ('sacatepequez', 'Sacatepéquez'),
            # Agregar más departamentos
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Departamento"
    )
    
    municipio = forms.ChoiceField(
        choices=[
            ('mixco', 'Mixco'),
            ('villa_nueva', 'Villa Nueva'),
            # Agregar más municipios
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Municipio"
    )
    
    dpi = forms.CharField(
        max_length=13,
        validators=[
            MinLengthValidator(13),
            RegexValidator(r'^\d+$', 'Solo se permiten números')
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': '\d{13}',
            'title': '13 dígitos numéricos'
        }),
        label="DPI"
    )
    
    nit = forms.CharField(
        max_length=9,
        required=False,
        validators=[
            RegexValidator(r'^\d{9}$', 'Debe tener 09 dígitos')
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': '\d{9}',
            'title': '09 dígitos numéricos'
        }),
        label="NIT"
    )
    
    es_consumidor_final = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'onchange': 'toggleNIT()'
        }),
        label="Consumidor Final (C/F)"
    )

    def clean(self):
        cleaned_data = super().clean()
        es_cf = cleaned_data.get('es_consumidor_final')
        nit = cleaned_data.get('nit')

        if not es_cf and not nit:
            raise ValidationError("Debe ingresar un NIT o marcar C/F")
        
        if not es_cf and len(nit) != 9:
            raise ValidationError("El NIT debe tener exactamente 10 dígitos")
        
        return cleaned_data