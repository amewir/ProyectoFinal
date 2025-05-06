from django.db import models
from django.conf import settings  # usa AUTH_USER_MODEL

class Mascota(models.Model):
    ESPECIES = (
      ('perro','Perro'),
      ('gato','Gato'),
      ('ave', 'Ave'),
      ('otro','Otro'),
    )
    nombre           = models.CharField(max_length=100)
    especie          = models.CharField(max_length=20, choices=ESPECIES)
    raza             = models.CharField(max_length=50)
    edad             = models.PositiveIntegerField()
    peso             = models.FloatField()
    foto             = models.ImageField(upload_to='mascotas/', blank=True, null=True)
    dueno            = models.ForeignKey(
                           settings.AUTH_USER_MODEL,
                           on_delete=models.CASCADE,
                           related_name='mascotas'
                       )
    historial_medico = models.TextField(blank=True)
    fecha_registro   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.get_especie_display()})"
