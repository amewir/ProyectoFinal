from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from cryptography.fernet import Fernet, InvalidToken
from cryptography.exceptions import InvalidKey
import pickle
import logging
import cv2
import numpy as np
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import transaction
from mtcnn import MTCNN
from PIL import Image, ExifTags
from io import BytesIO

logger = logging.getLogger(__name__)

class Usuario(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    first_name = models.CharField(max_length=30, blank=False, null=False)
    last_name = models.CharField(max_length=150, blank=False, null=False)
    
    # Campos biométricos y de seguridad
    telefono = models.CharField(max_length=8, blank=True, null=True, verbose_name="Teléfono")
    dpi = models.CharField(max_length=13, blank=False, null=False, verbose_name="DPI")
    direccion = models.TextField(blank=True, null=True, verbose_name="Dirección")
    bloqueado = models.BooleanField(default=False, verbose_name="Cuenta bloqueada")
    intentos_fallidos = models.IntegerField(default=0, verbose_name="Intentos fallidos")
    facial_embedding = models.BinaryField(null=True, blank=True, verbose_name="Embedding facial encriptado")
    
    # Sistema de roles
    ROLES = (
        ('admin', 'Administrador'),
        ('vet', 'Veterinario'),
        ('cliente', 'Cliente')
    )
    rol = models.CharField(
        max_length=10,
        choices=ROLES,
        default='cliente',
        verbose_name="Tipo de usuario"
    )

    def calcular_embedding_promedio(self):
        """Genera y almacena el embedding facial automáticamente"""
        try:
            # Obtener todas las muestras faciales del usuario
            muestras = self.muestras_faciales.all()
            
            if not muestras.exists():
                raise ValueError("El usuario no tiene muestras faciales registradas")
            
            # Generar embeddings
            embeddings = []
            for muestra in muestras:
                if muestra.embedding:
                    embeddings.append(pickle.loads(muestra.embedding))
            
            if not embeddings:
                raise ValueError("No se pudieron cargar embeddings válidos")
            
            # Calcular embedding promedio
            embedding_promedio = np.mean(embeddings, axis=0)
            
            # Encriptar y guardar
            cipher_suite = Fernet(settings.ENCRYPTION_KEY)
            serialized_data = pickle.dumps(embedding_promedio, protocol=4)
            self.facial_embedding = cipher_suite.encrypt(serialized_data)
            self.save()
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando datos faciales: {str(e)}", exc_info=True)
            return False


    # Métodos biométricos
    def actualizar_datos_faciales(self, embedding):
        """Encripta y almacena el embedding facial con validación"""
        try:
            if not isinstance(embedding, np.ndarray):
                raise ValueError("El embedding debe ser un array de numpy")
            
            cipher_suite = Fernet(settings.ENCRYPTION_KEY)
            serialized_data = pickle.dumps(embedding, protocol=4)  # Protocolo compatible
            self.facial_embedding = cipher_suite.encrypt(serialized_data)
            self.save()
            return True
        except Exception as e:
            logger.error(f"Error actualizando datos faciales: {str(e)}", exc_info=True)
            return False

    def obtener_embedding(self):
        """Desencripta y devuelve el embedding facial con manejo de errores"""
        if self.facial_embedding:
            try:
                cipher_suite = Fernet(settings.ENCRYPTION_KEY)
                decrypted_data = cipher_suite.decrypt(self.facial_embedding)
                embedding = pickle.loads(decrypted_data)
                
                # Validar formato del embedding
                if not isinstance(embedding, np.ndarray):
                    raise ValueError("Formato de embedding inválido")
                
                return embedding
            except (InvalidToken, InvalidKey) as e:
                logger.error(f"Error de desencriptación: {str(e)}")
                self.facial_embedding = None
                self.save()
            except Exception as e:
                logger.error(f"Error decodificando embedding: {str(e)}", exc_info=True)
        return None

    def reset_intentos(self):
        """Reinicia el contador de intentos fallidos"""
        self.intentos_fallidos = 0
        self.save()

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['username'], name='username_idx'),
            models.Index(fields=['email'], name='email_idx'),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"

class FacialData(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='muestras_faciales'
    )
    imagen = models.ImageField(
        upload_to='facial_data/%Y/%m/%d/',
        verbose_name="Imagen facial procesada"
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    embedding = models.BinaryField(null=True, blank=True, verbose_name="Embedding temporal")

def procesar_imagen(imagen_bytes):
    try:
        nparr = np.frombuffer(imagen_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            raise ValueError("Imagen no válida")
            
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(
            img, 
            scaleFactor=1.1, 
            minNeighbors=5,
            minSize=(80, 80),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        if len(faces) == 0:
            return None
        
        x, y, w, h = faces[0]
        rostro = img[y:y+h, x:x+w]
        return cv2.resize(rostro, (200, 200),  # Coma añadida para consistencia
        )
    except Exception as e:
        logger.error(f"Error procesando imagen: {str(e)}")
        return None
    
    
def corregir_orientacion(self):
        """Corrige la orientación EXIF de la imagen"""
        try:
            img_bytes = self.imagen.read()
            image = Image.open(BytesIO(img_bytes))
            
            # Obtener orientación EXIF
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = image._getexif()
            
            if exif and orientation in exif:
                exif_orientation = exif[orientation]
                
                # Rotar según orientación
                if exif_orientation == 3:
                    image = image.rotate(180, expand=True)
                elif exif_orientation == 6:
                    image = image.rotate(270, expand=True)
                elif exif_orientation == 8:
                    image = image.rotate(90, expand=True)
                
                # Convertir de vuelta a bytes
                img_byte_arr = BytesIO()
                image.save(img_byte_arr, format='JPEG')
                return img_byte_arr.getvalue()
                
            return img_bytes
        except Exception as e:
            logger.warning(f"Error corrigiendo orientación: {str(e)}")
            return img_bytes

def ajustar_cuadro(self, box, shape):
        """Asegura que el cuadro del rostro esté dentro de los límites de la imagen"""
        x, y, w, h = box
        height, width = shape[:2]
        
        x = max(0, x)
        y = max(0, y)
        w = min(width - x, w)
        h = min(height - y, h)
        
        return x, y, w, h

def save(self, *args, **kwargs):
        """Guardado seguro con manejo transaccional"""
        try:
            with transaction.atomic():
                # Guardar primero para obtener ID
                if not self.pk:
                    super().save(*args, **kwargs)
                
                # Procesar imagen
                self.procesar_imagen()
                
                # Actualizar registro
                super().save(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error guardando FacialData: {str(e)}")
            if self.pk:
                self.delete()
            raise
            
def generar_embedding(self, model):
        """Genera embedding facial usando un modelo específico"""
        try:
            img = cv2.imdecode(np.frombuffer(self.imagen.read(), np.uint8), cv2.IMREAD_GRAYSCALE)
            embedding = model.predict(img.reshape(1, 150, 150, 1))[0]
            self.embedding = pickle.dumps(embedding)
            self.save()
            return embedding
        except Exception as e:
            logger.error(f"Error generando embedding: {str(e)}")
            return None

def save(self, *args, **kwargs):
    """Guardado seguro con manejo de errores"""
    try:
        with transaction.atomic():
            if not self.pk:  # Solo si es nuevo registro
                super().save(*args, **kwargs)  # Guardar primero para obtener ID
            self.procesar_imagen()
            super().save(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error crítico al guardar: {str(e)}")
        if self.pk:  # Solo eliminar si ya existe en DB
            self.delete()
        raise

    class Meta:
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['usuario', 'fecha_registro'])
        ]
        verbose_name = "Dato Facial"
        verbose_name_plural = "Datos Faciales"

    def __str__(self):
        return f"Muestra facial de {self.usuario.username} ({self.fecha_registro})"