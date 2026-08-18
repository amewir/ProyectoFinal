# recursos_humanos/models.py
from django.db import models
from usuarios.models import Usuario




class Empleado(models.Model):
    PUESTOS_CHOICES = [
        ('veterinario', 'Veterinario'),
        ('asistente', 'Asistente'),
        ('admin', 'Administrador'),
        ('gerente', 'Gerente')
    ]
    
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='empleado'
    )
    puesto = models.CharField(
        max_length=20,
        choices=PUESTOS_CHOICES,
        default='asistente'
    )
    fecha_contratacion = models.DateField()
    salario_base = models.DecimalField(max_digits=10, decimal_places=2)
    departamento = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.get_puesto_display()}"

class SolicitudViaje(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    destino = models.CharField(max_length=200)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    motivo = models.TextField()
    presupuesto = models.DecimalField(max_digits=10, decimal_places=2)
    aprobado = models.BooleanField(default=False)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.empleado} - {self.destino}"
    
class Nomina(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)
    horas_extras = models.PositiveIntegerField(default=0)
    bonos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deducciones = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    salario_neto = models.DecimalField(max_digits=10, decimal_places=2)

    def calcular_salario_neto(self):
        return (
            self.empleado.salario_base +
            (self.horas_extras * 100) +
            self.bonos -
            self.deducciones
        )

    def save(self, *args, **kwargs):
        self.salario_neto = self.calcular_salario_neto()
        super().save(*args, **kwargs)