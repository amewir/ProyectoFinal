from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.timezone import now
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.views.decorators.http import require_http_methods
from .models import FacialData
from django.core.files.base import ContentFile
import cv2
import numpy as np
import os
import logging
import base64
import pickle
from django.db import transaction
from datetime import datetime
import cv2
import numpy as np
from io import BytesIO
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import cv2
import numpy as np
import base64
import json
from django.conf import settings

from .forms import (
    LoginForm,
    RegistroForm,
    EditarPerfilForm,
    CustomPasswordResetForm,
    CustomSetPasswordForm
)
from .models import Usuario
from mascotas.forms import MascotaForm
from mascotas.models import Mascota
from citas.models import Cita
from servicios.models import Servicio

logger = logging.getLogger(__name__)

# Helpers y configuraciones
def is_admin(user):
    return user.is_authenticated and user.is_staff

# Vistas públicas
def inicio(request):
    return render(request, 'inicio.html')

def registro(request):
    valid_samples = 0  # Evita errores de variable no inicializada
    user = None        # Inicialización temprana para chequeos posteriores

    if request.method == 'POST':
        form = RegistroForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Inicializar el detector facial
                    face_cascade = cv2.CascadeClassifier(
                        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                    )

                    # Crear usuario pero aún no lo guardamos completamente
                    user = form.save(commit=False)
                    user.is_active = True
                    user.save()

                    images = request.FILES.getlist('facial_data')
                    if len(images) < 20:
                        messages.error(request, "Se requieren mínimo 20 capturas faciales")
                        raise ValidationError("Insuficientes imágenes")

                    for idx, img in enumerate(images):
                        try:
                            facial_data = FacialData(usuario=user)

                            img_bytes = img.read()
                            nparr = np.frombuffer(img_bytes, np.uint8)
                            img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                            if img_cv is None:
                                raise ValueError("Formato de imagen no soportado o archivo corrupto")

                            try:
                                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                            except cv2.error as e:
                                raise ValueError(f"Error en conversión de color: {str(e)}")

                            faces = face_cascade.detectMultiScale(
                                gray,
                                scaleFactor=1.1,
                                minNeighbors=5,
                                minSize=(80, 80)
                            )

                            if len(faces) != 1:
                                raise ValidationError(f"Detectados {len(faces)} rostros. Se requiere 1")

                            facial_data.imagen.save(
                                f"{user.username}_{idx}.jpg",
                                ContentFile(img_bytes)
                            )
                            valid_samples += 1

                        except Exception as e:
                            logger.warning(f"Imagen {idx} descartada: {str(e)}", exc_info=True)
                            continue

                    if valid_samples < 20:
                        user.delete()
                        messages.error(request, f"Solo {valid_samples}/20 imágenes válidas. Registro fallido")
                        return redirect('registro')
                    for data in FacialData.objects.filter(usuario=user):
                        embedding = np.random.rand(128)  # Esto deberías reemplazar con tu modelo real de embeddings
                        data.embedding = pickle.dumps(embedding)
                        data.save()
                    try:
                        embedding_promedio = user.calcular_embedding_promedio()
                        if not embedding_promedio:
                            raise ValidationError("Error generando datos biométricos")

                        login(request, user)
                        messages.success(request, "¡Registro exitoso!")
                        return redirect('perfil_usuario')

                    except Exception as e:
                        user.delete()
                        logger.error(f"Error finalizando registro: {str(e)}", exc_info=True)
                        messages.error(request, "Error en proceso biométrico. Intente nuevamente")
                        return redirect('registro')

            except Exception as e:
                logger.error(f"Error en registro: {str(e)}", exc_info=True)
                if user and user.pk:
                    user.delete()
                messages.error(request, f"Error en el registro: {str(e)}")
                return redirect('registro')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegistroForm()

    # Solo entra aquí si user fue creado y se tienen al menos 20 muestras válidas (por seguridad)
    if user and valid_samples >= 20:
        try:
            for data in FacialData.objects.filter(usuario=user):
                embedding = np.random.rand(128)  # Reemplazar con tu modelo real
                data.embedding = pickle.dumps(embedding)
                data.save()

            if user.actualizar_datos_faciales():
                login(request, user)
                messages.success(request, "¡Registro exitoso!")
                return redirect('perfil_usuario')
            else:
                raise Exception("Error generando embeddings finales")

        except Exception as e:
            user.delete()
            logger.error(f"Error finalizando registro: {str(e)}", exc_info=True)
            messages.error(request, "Error en proceso biométrico")
            return redirect('registro')

    return render(request, 'usuarios/registro.html', {
        'form': form,
        'min_imagenes': 20,
    })

@login_required
def perfil_usuario(request):
    # lógica para mostrar perfil
    return render(request, 'usuarios/perfil.html')

def facial_login(request):
    if request.method == 'POST':
        try:
            # Verificar existencia del modelo
            from django.core.files.storage import default_storage
            model_path = default_storage.path('modelo_lbph.yml')
            
            if not default_storage.exists(model_path):
                return JsonResponse({'error': 'Modelo no entrenado'}, status=503)
            
            # Procesar imagen
            image_data = request.POST.get('image').split(',')[1]
            rostro = procesar_imagen(base64.b64decode(image_data))
            
            if rostro is None:
                return JsonResponse({'error': 'Rostro no detectado'}, status=400)
            
            # Cargar modelo
            model = cv2.face.LBPHFaceRecognizer_create()
            model.read(model_path)
            
            # Predecir
            label, conf = model.predict(rostro)
            
            # Umbral dinámico
            UMBRAL = 70  # Puedes ajustar este valor
            if conf < UMBRAL:
                user = Usuario.objects.get(id=label)
                login(request, user)
                user.intentos_fallidos = 0  # Resetear intentos
                user.save()
                return JsonResponse({'redirect': reverse('perfil_usuario')})
            else:
                # Registrar intento fallido
                if Usuario.objects.filter(id=label).exists():
                    user = Usuario.objects.get(id=label)
                    user.intentos_fallidos += 1
                    user.save()
                return JsonResponse({'error': 'Usuario no reconocido'}, status=401)
                
        except Exception as e:
            logger.error(f"Error facial: {str(e)}")
            return JsonResponse({'error': 'Error de servidor'}, status=500)
            
    return render(request, 'usuarios/login_facial.html')


# Vistas de administración
@login_required
@user_passes_test(is_admin)
def panel_administracion(request):
    UsuarioModel = get_user_model()
    context = {
        'total_usuarios': UsuarioModel.objects.count(),
        'total_mascotas': Mascota.objects.count(),
        'total_servicios': Servicio.objects.count(),
        'citas_hoy': Cita.objects.filter(fecha=now().date()).count(),
        'citas_pendientes': Cita.objects.filter(estado='pendiente').count(),
        'usuarios': UsuarioModel.objects.all(),
        'mascotas': Mascota.objects.select_related('dueno').all(),
        'servicios': Servicio.objects.all(),
        'citas': Cita.objects.select_related('mascota','usuario').all(),
    }
    return render(request, 'admin/panel.html', context)

@login_required
@user_passes_test(is_admin)
def entrenar_modelo(request):
    try:
        # Obtener datos de la base de datos
        facial_data = FacialData.objects.all().select_related('usuario')
        
        if not facial_data.exists():
            messages.error(request, "No hay datos faciales para entrenar")
            return redirect('panel_administracion')
        
        faces = []
        labels = []
        
        for data in facial_data:
            try:
                # Cargar desde la base de datos
                nparr = np.frombuffer(data.imagen.read(), np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
                faces.append(img)
                labels.append(data.usuario.id)
            except Exception as e:
                logger.error(f"Error procesando {data.id}: {str(e)}")
                continue
        
        if len(faces) == 0:
            messages.error(request, "No se pudieron cargar imágenes válidas")
            return redirect('panel_administracion')
        
        # Entrenar modelo
        model = cv2.face.LBPHFaceRecognizer_create()
        model.train(faces, np.array(labels))
        
        # Guardar usando FileStorage
        from django.core.files.storage import default_storage
        model_path = default_storage.path('modelo_lbph.yml')
        model.save(model_path)
        
        messages.success(request, f"Modelo actualizado con {len(faces)} muestras")
        return redirect('panel_administracion')
        
    except Exception as e:
        logger.error(f"Error en entrenamiento: {str(e)}")
        messages.error(request, "Error crítico en el entrenamiento")
        return redirect('panel_administracion')
# Vistas de usuario
@login_required
def perfil_usuario(request):
    mascotas = Mascota.objects.filter(dueno=request.user)
    citas = Cita.objects.filter(usuario=request.user)
    
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
        'citas': citas,
        'mascota_form': mform,
    })

@login_required
def capturar_rostros(request):
    if request.method == 'POST':
        try:
            # Para captura desde admin
            user_id = request.POST.get('user_id', request.user.id)
            user = get_object_or_404(Usuario, id=user_id)
            
            # Procesar imagen
            image_data = request.FILES['imagen'].read()
            rostro = procesar_imagen(image_data)
            
            if rostro is not None:
                # Guardar muestra
                _, buffer = cv2.imencode('.jpg', rostro)
                FacialData.objects.create(
                    usuario=user,
                    imagen=ContentFile(buffer.tobytes(), name=f"captura_{user.username}_{datetime.now().timestamp()}.jpg"),
                    embedding=pickle.dumps(rostro)
                )
                messages.success(request, "Muestra facial agregada exitosamente")
                return redirect('editar_usuario', user_id=user.id)
            
            messages.error(request, "No se detectó un rostro válido")
            return redirect('editar_usuario', user_id=user.id)
            
        except Exception as e:
            logger.error(f"Error captura: {str(e)}")
            messages.error(request, "Error al procesar la imagen")
            return redirect('panel_administracion')
    
    return render(request, 'usuarios/captura_facial.html')

# Vistas de autenticación
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
def editar_perfil(request):
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('perfil_usuario')
    else:
        form = EditarPerfilForm(instance=request.user)
    return render(request, 'usuarios/editar_perfil.html', {'form': form})

# Vistas restantes
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

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm

@login_required
def detalle_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, usuario=request.user)
    return render(request, 'citas/detalle_cita.html', {'cita': cita})

def redirect_by_role(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('panel_administracion')
        return redirect('perfil_usuario')
    return redirect('inicio')

def lista_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/lista_usuarios.html', {'usuarios': usuarios})

def procesar_imagen(imagen_bytes):
    nparr = np.frombuffer(imagen_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    
    if img is None:
        return None

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=5)

    if len(faces) == 0:
        return None
    
    x, y, w, h = faces[0]
    rostro = img[y:y+h, x:x+w]
    rostro = cv2.resize(rostro, (200, 200))  # Tamaño estándar para LBPH
    return rostro


@csrf_exempt
def validate_face(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        # Obtener datos de la imagen
        image_data = request.body.split(b',')[1]
        img_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Detección facial
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(100, 100)
        )
        
        return JsonResponse({
            'valid': len(faces) == 1,
            'faces_count': len(faces),
            'face_size': faces[0].tolist() if len(faces) > 0 else []
        })
        
    except IndexError:
        return JsonResponse({'error': 'Formato de imagen incorrecto'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)