# citas/models.py
from django.db import models
from django.conf import settings
from mascotas.models import Mascota
from servicios.models import Servicio

class Cita(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Usuario"
    )
    mascota = models.ForeignKey(
        Mascota,
        on_delete=models.CASCADE,
        verbose_name="Mascota"
    )
    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.CASCADE,
        verbose_name="Servicio"
    )
    fecha = models.DateField("Fecha de la cita")
    hora = models.TimeField("Hora de la cita")
    notas = models.TextField("Notas adicionales", blank=True)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('completada', 'Completada'),
            ('cancelada', 'Cancelada')
        ],
        default='pendiente'
    )

    def __str__(self):
        return f"{self.mascota.nombre} - {self.fecha} {self.hora}"