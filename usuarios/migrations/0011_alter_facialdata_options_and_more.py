# Generated by Django 5.2 on 2025-05-08 23:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0010_alter_facialdata_options_remove_usuario_facial_data_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='facialdata',
            options={},
        ),
        migrations.RemoveIndex(
            model_name='facialdata',
            name='usuarios_fa_usuario_7b64bf_idx',
        ),
    ]
