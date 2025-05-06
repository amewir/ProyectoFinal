from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from cryptography.fernet import Fernet, InvalidToken
from cryptography.exceptions import InvalidKey
import pickle
import logging

logger = logging.getLogger(__name__)

class Usuario(AbstractUser):
    # Campos heredados de AbstractUser con modificaciones
    email = models.EmailField(unique=True, blank=False, null=False)
    first_name = models.CharField(max_length=30, blank=False, null=False)
    last_name = models.CharField(max_length=150, blank=False, null=False)
    
    # Nuevos campos personalizados
    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Teléfono"
    )
    dpi = models.CharField(
        max_length=13,
        blank=True,
        null=True,
        verbose_name="DPI"
    )
    direccion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Dirección"
    )
    bloqueado = models.BooleanField(
        default=False,
        verbose_name="Cuenta bloqueada"
    )
    intentos_fallidos = models.IntegerField(
        default=0,
        verbose_name="Intentos fallidos"
    )
    facial_data = models.BinaryField(
        null=True,
        blank=True,
        verbose_name="Datos faciales encriptados"
    )
    
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

    # Métodos de seguridad
    def set_facial_data(self, facial_encoding):
        """Encripta y almacena los datos biométricos"""
        try:
            cipher_suite = Fernet(settings.ENCRYPTION_KEY)
            serialized_data = pickle.dumps(facial_encoding)
            encrypted_data = cipher_suite.encrypt(serialized_data)
            self.facial_data = encrypted_data
            self.save()
        except Exception as e:
            logger.error(f"Error guardando datos faciales: {str(e)}")
            raise ValueError("Error al procesar datos biométricos")

    def get_facial_data(self):
        """Desencripta y recupera los datos biométricos"""
        if not self.facial_data:
            return None
            
        try:
            cipher_suite = Fernet(settings.ENCRYPTION_KEY)
            decrypted_data = cipher_suite.decrypt(self.facial_data)
            return pickle.loads(decrypted_data)
        except (InvalidToken, InvalidKey) as e:
            logger.error(f"Error de desencriptación: {str(e)}")
            self.reset_facial_data()
            return None
        except Exception as e:
            logger.error(f"Error recuperando datos faciales: {str(e)}")
            return None

    def reset_facial_data(self):
        """Elimina los datos biométricos almacenados"""
        self.facial_data = None
        self.save()

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