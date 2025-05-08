from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.core.exceptions import ValidationError
from .forms import LoginForm, RegistroForm, EditarPerfilForm
from .models import Usuario
from mascotas.forms import MascotaForm
from mascotas.models import Mascota
from citas.models import Cita
from servicios.models import Servicio
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.timezone import now
from django.contrib import messages
import cv2, numpy as logging
import logging
from django.shortcuts import render
from .forms import EditarPerfilForm
from django.contrib.auth.views import PasswordResetView
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
def inicio(request):
    return render(request, 'inicio.html')

logger = logging.getLogger(__name__)

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.timezone import now
from django.contrib import messages
import cv2, numpy as np, os, logging, base64

from .forms import LoginForm, RegistroForm, EditarPerfilForm
from .models import Usuario
from mascotas.models import Mascota
from citas.models import Cita
from servicios.models import Servicio

logger = logging.getLogger(__name__)

from django.contrib.auth.views import PasswordResetConfirmView
from .forms import CustomPasswordResetForm, CustomSetPasswordForm

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm


def is_admin(user):
    return user.is_authenticated and user.is_staff

# Panel y gestión global
@login_required
@user_passes_test(is_admin)
def panel_administracion(request):
    UsuarioModel     = get_user_model()
    context = {
        'total_usuarios':   UsuarioModel.objects.count(),
        'total_mascotas':   Mascota.objects.count(),
        'total_servicios':  Servicio.objects.count(),
        'citas_hoy':        Cita.objects.filter(fecha=now().date()).count(),
        'citas_pendientes': Cita.objects.filter(estado='pendiente').count(),
        'usuarios':         UsuarioModel.objects.all(),
        'mascotas':         Mascota.objects.select_related('dueno').all(),
        'servicios':        Servicio.objects.all(),
        'citas':            Cita.objects.select_related('mascota','usuario').all(),
    }
    return render(request, 'admin/panel.html', context)


@login_required
@user_passes_test(is_admin)
def editar_usuario(request, user_id):
    UsuarioModel = get_user_model()
    usuario = get_object_or_404(UsuarioModel, id=user_id)

    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario {usuario.username} actualizado.')
            return redirect('panel_administracion')
    else:
        form = EditarPerfilForm(instance=usuario)

    return render(request, 'admin/editar_usuario.html', {
        'form': form,
        'usuario': usuario
    })




@login_required
@user_passes_test(is_admin)
def eliminar_usuario(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, f'Usuario {usuario.username} eliminado')
        return redirect('panel_administracion')
    return render(request, 'admin/confirmar_eliminacion_usuario.html', {'usuario': usuario})

# Gestión de citas
@login_required
@user_passes_test(is_admin)
def gestion_citas(request):
    citas = Cita.objects.all().order_by('-fecha')
    return render(request, 'admin/gestion_citas.html', {'citas': citas})

@login_required
@user_passes_test(is_admin)
def cambiar_estado_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    if request.method == 'POST':
        cita.estado = request.POST.get('estado')
        cita.save()
        messages.success(request, f'Estado actualizado: {cita.get_estado_display()}')
    return redirect('gestion_citas')

# Auth y perfil
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('perfil_usuario')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})


def redirect_by_role(request):
    """
    Redirige al usuario tras el login según su rol:
    - staff → panel de administración
    - cliente/vet → perfil de usuario
    """
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('panel_administracion')
        return redirect('perfil_usuario')
    return redirect('inicio')



def custom_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user and user.bloqueado:
                form.add_error(None, "Cuenta bloqueada.")
            elif user:
                login(request, user)
                return redirect('panel_administracion' if user.is_staff else 'perfil_usuario')
    else:
        form = LoginForm()
    return render(request, 'usuarios/login.html', {'form': form})

@login_required
def cerrar_sesion(request):
    logout(request)
    return redirect('inicio')

@login_required
def perfil_usuario(request):
    mascotas = Mascota.objects.filter(dueno=request.user)
    citas    = Cita.objects.filter(usuario=request.user)
    if request.method == 'POST':
        mform = MascotaForm(request.POST, request.FILES)
        if mform.is_valid():
            nueva = mform.save(commit=False)
            nueva.dueno = request.user
            nueva.save()
            return redirect('perfil_usuario')
    else:
        mform = MascotaForm()
    return render(request, 'usuarios/perfil.html', {
        'mascotas': mascotas,
        'citas':    citas,
        'mascota_form': mform,
    })

@login_required
def editar_perfil(request):
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('perfil_usuario')
    else:
        form = EditarPerfilForm(instance=request.user)
    return render(request, 'usuarios/editar_perfil.html', {'form': form})

@login_required
def detalle_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, usuario=request.user)
    return render(request, 'citas/detalle_cita.html', {'cita': cita})

# (Funciones de reconocimiento facial omitidas para brevedad)
