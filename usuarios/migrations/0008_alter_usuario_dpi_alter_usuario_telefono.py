# Generated by Django 5.1.4 on 2025-05-08 06:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0007_usuario_dpi'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='dpi',
            field=models.CharField(default='', max_length=13, verbose_name='DPI'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='usuario',
            name='telefono',
            field=models.CharField(blank=True, max_length=8, null=True, verbose_name='Teléfono'),
        ),
    ]
