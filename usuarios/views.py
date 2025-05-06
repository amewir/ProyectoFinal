from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.core.exceptions import ValidationError
from .forms import LoginForm
from .models import Usuario
import cv2
import numpy as np
import os
import logging
import base64
import logging
from django.shortcuts import render
from .forms import RegistroForm
from django.contrib.auth import login
from .forms import RegistroForm
from django.shortcuts import redirect
from django.contrib.auth import logout



# Configurar logging
logger = logging.getLogger(__name__)

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()  # Guarda el usuario en la base de datos
            login(request, user)  # Opcional: Iniciar sesión automáticamente
            return redirect('inicio')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})


def redirect_by_role(request):
    if request.user.is_authenticated:
        if request.user.is_staff:  # Ejemplo para administradores
            return redirect('panel_administracion')
        else:  # Usuarios regulares
            return redirect('perfil_usuario')
    return redirect('inicio')


def inicio(request):
    """Vista para la página de inicio"""
    return render(request, 'inicio.html')

def custom_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            # Validación de reconocimiento facial
            if form.cleaned_data.get('biometrico'):
                if not handle_facial_recognition(request, user, form):
                    return render(request, 'usuarios/login.html', {'form': form})

            if user is not None:
                handle_successful_login(user)
                login(request, user)
                return redirect_by_role(request)
        else:
            handle_failed_attempt(request)
    
    else:
        form = LoginForm()
    
    return render(request, 'usuarios/login.html', {'form': form})

def handle_facial_recognition(request, user, form):
    """Maneja la lógica de reconocimiento facial"""
    try:
        # Obtener imagen codificada en base64 del campo oculto
        image_data = request.POST.get('facial_image')
        if not image_data:
            raise ValidationError("Debes capturar un rostro")
        
        # Convertir base64 a imagen OpenCV
        img = process_base64_image(image_data)
        
        # Realizar predicción
        label, confidence = predict_face(img)
        
        # Validar coincidencia
        if not validate_prediction(user.id, label, confidence):
            raise ValidationError("Reconocimiento facial fallido")
        
        return True
    
    except Exception as e:
        logger.error(f"Error en reconocimiento facial: {str(e)}")
        form.add_error(None, str(e))
        increment_failed_attempts(user)
        return False

def process_base64_image(image_data):
    """Convierte base64 a imagen procesable por OpenCV"""
    try:
        # Eliminar el prefijo del base64 si existe
        if ';base64,' in image_data:
            image_data = image_data.split(';base64,')[1]
        
        # Decodificar la imagen
        img_array = np.frombuffer(base64.b64decode(image_data), np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
        
        # Preprocesamiento
        img = cv2.resize(img, (150, 150), interpolation=cv2.INTER_CUBIC)
        return cv2.equalizeHist(img)  # Mejorar contraste
        
    except Exception as e:
        raise ValidationError("Error procesando imagen facial")

def predict_face(image):
    """Realiza la predicción usando el modelo LBPH"""
    model_path = os.path.join(os.path.dirname(__file__), 'modelo_lbph.yml')
    
    if not os.path.exists(model_path):
        raise ValidationError("Modelo de reconocimiento no encontrado")
    
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(model_path)
        return recognizer.predict(image)
    except Exception as e:
        raise ValidationError("Error cargando el modelo de reconocimiento")

def validate_prediction(user_id, label, confidence):
    """Valida los resultados de la predicción"""
    CONFIDENCE_THRESHOLD = 70  # Ajustar según pruebas
    return confidence < CONFIDENCE_THRESHOLD and label == user_id

def increment_failed_attempts(user):
    """Maneja el incremento de intentos fallidos"""
    if user:
        user.intentos_fallidos += 1
        if user.intentos_fallidos >= 3:
            user.bloqueado = True
        user.save()

def handle_successful_login(user):
    """Restablece los intentos fallidos después de un login exitoso"""
    if user.intentos_fallidos > 0:
        user.intentos_fallidos = 0
        user.save()

def handle_failed_attempt(request):
    """Maneja intentos fallidos de login"""
    username = request.POST.get('username')
    try:
        user = Usuario.objects.get(username=username)
        increment_failed_attempts(user)
    except Usuario.DoesNotExist:
        pass
from django.contrib.auth.decorators import login_required, user_passes_test

@login_required
def panel_administracion(request):
    if not request.user.is_staff:
        return redirect('inicio')
    return render(request, 'admin/panel.html')

@login_required
def perfil_usuario(request):
    return render(request, 'usuarios/perfil.html')
@login_required
def editar_perfil(request):
    return render(request, 'usuarios/editar_perfil.html')
@login_required
def cerrar_sesion(request):
    logout(request)
    return redirect('inicio')