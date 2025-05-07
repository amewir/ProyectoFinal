# citas/models.py
from django.db import models
from django.conf import settings
from mascotas.models import Mascota
from servicios.models import Servicio

class Cita(models.Model):
     # Nuevos campos de facturación
    nombre_facturacion = models.CharField(max_length=100, verbose_name="Nombre")
    apellido_facturacion = models.CharField(max_length=100, verbose_name="Apellido")
    direccion_facturacion = models.TextField(verbose_name="Dirección")
    departamento = models.CharField(max_length=50, verbose_name="Departamento")
    municipio = models.CharField(max_length=50, verbose_name="Municipio")
    dpi = models.CharField(max_length=13, verbose_name="DPI (13 dígitos)")
    nit = models.CharField(max_length=10, verbose_name="NIT (9 dígitos o CF)")
    es_consumidor_final = models.BooleanField(default=False, verbose_name="Consumidor Final (C/F)")

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
    def estado_color(self):
        return {
            'pendiente': 'warning',
            'completada': 'success',
            'cancelada': 'danger'
        }.get(self.estado, 'secondary')
        
    def puede_editar(self, user):
        return user == self.usuario or user.is_staff