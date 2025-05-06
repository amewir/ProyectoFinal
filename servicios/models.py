from django.db import models
from django.urls import reverse

class Servicio(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Servicio")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL Amigable")
    descripcion = models.TextField(verbose_name="Descripción Completa")
    descripcion_corta = models.CharField(max_length=200, verbose_name="Descripción Corta")
    costo = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        verbose_name="Costo (Q)"
    )
    imagen = models.ImageField(
        upload_to='servicios/',
        verbose_name="Imagen Representativa"
    )
    duracion = models.PositiveIntegerField(
        verbose_name="Duración en Minutos",
        default=60
    )
    disponible = models.BooleanField(default=True, verbose_name="Disponible")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        ordering = ['nombre']
        permissions = [
            ("gestion_servicios", "Puede gestionar servicios"),
        ]

    def __str__(self):
        return f"{self.nombre} - Q{self.costo}"
    
    def get_absolute_url(self):
        return reverse('detalle_servicio', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        from django.utils.text import slugify
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)