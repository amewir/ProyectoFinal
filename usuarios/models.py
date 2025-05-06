from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from cryptography.fernet import Fernet, InvalidToken
from cryptography.exceptions import InvalidSignature
import logging
import pickle

logger = logging.getLogger(__name__)

class Usuario(AbstractUser):
    facial_data = models.BinaryField(null=True, blank=True)
    bloqueado = models.BooleanField(default=False)
    intentos_fallidos = models.IntegerField(default=0)

    ROLES = (
        ('admin', 'Administrador'),
        ('vet', 'Veterinario'),
        ('cliente', 'Cliente')
    )
    rol = models.CharField(max_length=10, choices=ROLES, default='cliente')

    def set_facial_data(self, facial_encoding):
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
        if not self.facial_data:
            return None
        try:
            cipher_suite = Fernet(settings.ENCRYPTION_KEY)
            decrypted_data = cipher_suite.decrypt(self.facial_data)
            return pickle.loads(decrypted_data)
        except (InvalidToken, InvalidSignature) as e:
            logger.error(f"Error de desencriptación: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error recuperando datos faciales: {str(e)}")
            return None

    def reset_intentos(self):
        self.intentos_fallidos = 0
        self.save()

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
