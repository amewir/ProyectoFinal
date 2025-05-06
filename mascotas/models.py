from django.db import models
from usuarios.models import Usuario

class Mascota(models.Model):
    nombre = models.CharField(max_length=50)
    id_chip = models.CharField(max_length=20, unique=True)
    especie = models.CharField(max_length=20)
    sexo = models.CharField(max_length=10)
    raza = models.CharField(max_length=30)
    edad = models.IntegerField()
    peso = models.FloatField()
    dueno = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    historial_medico = models.TextField()
    notas_adicionales = models.TextField(blank=True, null=True)