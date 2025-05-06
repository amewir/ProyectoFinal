from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.core.exceptions import ValidationError
from .forms import LoginForm, RegistroForm, EditarPerfilForm
from .models import Usuario
from mascotas.forms import MascotaForm
from mascotas.models import Mascota
from citas.forms import CitaForm
from citas.models import Cita
from django.contrib.auth.decorators import login_required
import cv2
import numpy as np
import os
import logging
import base64


logger = logging.getLogger(__name__)

# Vistas de autenticación
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                return redirect('perfil_usuario')
            except Exception as e:
                logger.error(f"Error en registro: {str(e)}")
                return render(request, 'usuarios/registro.html', {
                    'form': form,
                    'error': 'Error al crear la cuenta. Intente nuevamente.'
                })
        return render(request, 'usuarios/registro.html', {
            'form': form,
            'errors': form.errors
        })
    return render(request, 'usuarios/registro.html', {'form': RegistroForm()})

def custom_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            # Validar cuenta bloqueada
            if user and user.bloqueado:
                form.add_error(None, "Cuenta bloqueada. Contacte al administrador.")
                return render(request, 'usuarios/login.html', {'form': form})
            
            # Procesar reconocimiento facial si es requerido
            if form.cleaned_data.get('biometrico') and user:
                if not handle_facial_recognition(request, user, form):
                    return render(request, 'usuarios/login.html', {'form': form})

            if user is not None:
                handle_successful_login(user)
                login(request, user)
                return redirect_by_role(request)
        else:
            handle_failed_attempt(request)
            return render(request, 'usuarios/login.html', {
                'form': form,
                'errors': form.errors
            })
    return render(request, 'usuarios/login.html', {'form': LoginForm()})

def redirect_by_role(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('panel_administracion')
        return redirect('perfil_usuario')
    return redirect('inicio')

@login_required
def cerrar_sesion(request):
    logout(request)
    return redirect('inicio')

# Vistas de perfil y administración
@login_required
def perfil_usuario(request):
    mascotas = Mascota.objects.filter(dueno=request.user)
    citas = Cita.objects.filter(usuario=request.user)
    
    if request.method == 'POST':
        mascota_form = MascotaForm(request.POST, request.FILES)
        if mascota_form.is_valid():
            mascota = mascota_form.save(commit=False)
            mascota.dueno = request.user
            mascota.save()
            return redirect('perfil_usuario')
    else:
        mascota_form = MascotaForm()

    return render(request, 'usuarios/perfil.html', {
        'mascotas': mascotas,
        'citas': citas,
        'mascota_form': mascota_form
    })

@login_required
def editar_perfil(request):
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('perfil_usuario')
        return render(request, 'usuarios/editar_perfil.html', {'form': form})
    form = EditarPerfilForm(instance=request.user)
    return render(request, 'usuarios/editar_perfil.html', {'form': form})

@login_required
def panel_administracion(request):
    if not request.user.is_staff:
        return redirect('inicio')
    return render(request, 'admin/panel.html')

# Funcionalidades de citas
@login_required
def agendar_cita(request):
    if request.method == 'POST':
        form = CitaForm(request.user, request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            cita.creado_por = request.user
            cita.save()
            return redirect('detalle_cita', cita_id=cita.id)
    else:
        form = CitaForm(user=request.user)
    return render(request, 'citas/agendar_cita.html', {'form': form})

@login_required
def detalle_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, creado_por=request.user)
    return render(request, 'citas/detalle_cita.html', {'cita': cita})

# Funciones de soporte para reconocimiento facial
def handle_facial_recognition(request, user, form):
    try:
        image_data = request.POST.get('facial_image')
        if not image_data:
            raise ValidationError("Debes capturar un rostro")
        
        img = process_base64_image(image_data)
        label, confidence = predict_face(img)
        
        if not validate_prediction(user.id, label, confidence):
            raise ValidationError("Reconocimiento facial fallido")
        return True
    
    except Exception as e:
        logger.error(f"Error facial: {str(e)}")
        form.add_error(None, str(e))
        increment_failed_attempts(user)
        return False

def process_base64_image(image_data):
    try:
        if ';base64,' in image_data:
            image_data = image_data.split(';base64,')[1]
        
        img_array = np.frombuffer(base64.b64decode(image_data), np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
        img = cv2.resize(img, (150, 150), interpolation=cv2.INTER_CUBIC)
        return cv2.equalizeHist(img)
        
    except Exception as e:
        raise ValidationError("Error procesando imagen facial")

def predict_face(image):
    model_path = os.path.join(os.path.dirname(__file__), 'modelo_lbph.yml')
    
    if not os.path.exists(model_path):
        raise ValidationError("Modelo de reconocimiento no encontrado")
    
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(model_path)
        return recognizer.predict(image)
    except Exception as e:
        raise ValidationError("Error cargando el modelo")

def validate_prediction(user_id, label, confidence):
    CONFIDENCE_THRESHOLD = 70
    return confidence < CONFIDENCE_THRESHOLD and label == user_id

# Manejo de seguridad
def increment_failed_attempts(user):
    if user:
        user.intentos_fallidos += 1
        if user.intentos_fallidos >= 3:
            user.bloqueado = True
            logger.warning(f"Usuario {user.username} bloqueado por intentos fallidos")
        user.save()

def handle_successful_login(user):
    if user.intentos_fallidos > 0:
        user.intentos_fallidos = 0
        user.save()

def handle_failed_attempt(request):
    username = request.POST.get('username')
    try:
        user = Usuario.objects.get(username=username)
        increment_failed_attempts(user)
    except Usuario.DoesNotExist:
        pass

# Vista de inicio
def inicio(request):
    return render(request, 'inicio.html')

@login_required
def agregar_mascota(request):
    if request.method == 'POST':
        form = MascotaForm(request.POST, request.FILES)
        if form.is_valid():
            mascota = form.save(commit=False)
            mascota.dueno = request.user
            mascota.save()
            return redirect('perfil_usuario')
    else:
        form = MascotaForm()
    return render(request, 'mascotas/agregar_mascota.html', {'form': form})