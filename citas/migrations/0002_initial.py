# Generated by Django 5.2 on 2025-05-06 16:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('citas', '0001_initial'),
        ('mascotas', '0001_initial'),
        ('servicios', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='cita',
            name='creado_por',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='citas_creadas', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cita',
            name='mascota',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mascotas.mascota'),
        ),
        migrations.AddField(
            model_name='cita',
            name='servicio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='servicios.servicio'),
        ),
    ]
