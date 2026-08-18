from django.db import models
from servicios.models import Servicio
from citas.models import Cita
from usuarios.models import Usuario

class Factura(models.Model):
    cita = models.OneToOneField(Cita, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_emision = models.DateField(auto_now_add=True)
    pagado = models.BooleanField(default=False)

    def generar_factura(self):
        self.total = self.cita.servicio.costo
        self.save()

class ClienteCRM(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    total_compras = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ultima_visita = models.DateField(auto_now=True)