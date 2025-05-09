from django.contrib import admin
from .models import Usuario, FacialData

class FacialDataInline(admin.TabularInline):
    model = FacialData
    extra = 0
    readonly_fields = ['fecha_registro']
    fields = ['imagen', 'embedding', 'fecha_registro']

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'rol', 'bloqueado', 'tiene_datos_faciales')
    list_filter = ('rol', 'bloqueado')
    search_fields = ('username', 'email')
    inlines = [FacialDataInline]
    
    def tiene_datos_faciales(self, obj):
        return bool(obj.facial_embedding)
    tiene_datos_faciales.boolean = True
    tiene_datos_faciales.short_description = 'Datos Faciales'