from django.db import models

class Medicamento(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    stock = models.IntegerField(default=0)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    lote = models.CharField(max_length=50)
    fecha_caducidad = models.DateField()
    proveedor = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.nombre} (Lote: {self.lote})"

class MovimientoInventario(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida')
    ]
    
    medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    responsable = models.CharField(max_length=100)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_tipo_display()} de {self.cantidad} unidades"