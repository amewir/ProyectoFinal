from django.contrib import admin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'rol', 'bloqueado')
    list_filter = ('rol', 'bloqueado')
    search_fields = ('username', 'email')