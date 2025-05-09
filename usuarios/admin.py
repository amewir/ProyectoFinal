from django.contrib import admin
from .models import Usuario, FacialData
from import_export import resources
from ventas.models import Factura
from django.http import HttpResponse

class FacturaResource(resources.ModelResource):
    class Meta:
        model = Factura
        fields = ('id', 'cita__mascota__nombre', 'total', 'pagado')

# En la vista de administración:
def exportar_facturas(request):
    dataset = FacturaResource().export()
    response = HttpResponse(dataset.xlsx, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="facturas.xlsx"'
    return response



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