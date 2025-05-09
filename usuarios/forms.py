from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from .models import Usuario
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import get_user_model
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse_lazy
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from django.core.validators import MinLengthValidator, RegexValidator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.forms import ClearableFileInput
from django.core.validators import FileExtensionValidator, MaxValueValidator
from django.core.exceptions import ValidationError

def validate_max_file_size(value):
    max_size = 5 * 1024 * 1024  # 5MB
    if value.size > max_size:
        raise ValidationError(f'El archivo no puede superar los {max_size // 1024 // 1024}MB')

class CustomMultipleFileInput(ClearableFileInput):
    allow_multiple_selected = True

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('attrs', {})
        kwargs['attrs']['multiple'] = True
        super().__init__(*args, **kwargs)

    def value_from_datadict(self, data, files, name):
        return files.getlist(name)
    

class RegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['facial_data'].widget = forms.HiddenInput()
        self.fields['facial_data'].required = False

    facial_data = forms.FileField(
        required=True,
        label="Captura facial (mínimo 20 imágenes)",
        widget=CustomMultipleFileInput(attrs={
            'accept': 'image/*',
            'capture': 'environment',
            'class': 'file-input'
        }),
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_max_file_size  # Validador personalizado
        ]
    )
    
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
        
class CustomPasswordResetForm(PasswordResetForm):
    dpi = forms.CharField(
        label='DPI (13 dígitos)',
        validators=[
            MinLengthValidator(13, 'El DPI debe tener exactamente 13 dígitos'),
            RegexValidator(r'^\d+$', 'Solo se permiten números')
        ],
        widget=forms.TextInput(attrs={
            'pattern': '\d{13}',
            'title': '13 dígitos numéricos'
        })
    )

    def get_users(self, email):
        dpi = self.cleaned_data.get("dpi")
        return get_user_model().objects.filter(email__iexact=email, dpi=dpi, is_active=True)

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None,
             html_email_template_name=None,
             extra_email_context=None):

        email = self.cleaned_data["email"]
        for user in self.get_users(email):
            context = {
                'email': user.email,
                'domain': domain_override or request.get_host(),
                'site_name': 'Veterinaria',
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }
            if extra_email_context:
                context.update(extra_email_context)

            subject = render_to_string(subject_template_name, context).strip()
            html_message = render_to_string(email_template_name, context)
            plain_message = strip_tags(html_message)

            msg = EmailMultiAlternatives(subject, plain_message, from_email or settings.DEFAULT_FROM_EMAIL, [user.email])
            msg.attach_alternative(html_message, "text/html")  # << aquí se adjunta correctamente
            msg.send()
    dpi = forms.CharField(
        label='DPI (13 dígitos)',
        validators=[
            MinLengthValidator(13, 'El DPI debe tener exactamente 13 dígitos'),
            RegexValidator(r'^\d+$', 'Solo se permiten números')
        ],
        widget=forms.TextInput(attrs={
            'pattern': '\d{13}',
            'title': '13 dígitos numéricos'
        })
    )

    def get_users(self, email):
        dpi = self.cleaned_data.get("dpi")
        return get_user_model().objects.filter(email__iexact=email, dpi=dpi, is_active=True)

class CustomSetPasswordForm(SetPasswordForm):
    dpi = forms.CharField(label="DPI", max_length=13)

    def clean(self):
        cleaned_data = super().clean()
        dpi = cleaned_data.get("dpi")

        if dpi and self.user.dpi != dpi:
            raise ValidationError("El DPI no coincide con el usuario")

        return cleaned_data


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()  # Muy importante: guarda la nueva contraseña
        return super().form_valid(form)
    
