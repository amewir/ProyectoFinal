from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from ventas.models import Factura
from import_export import resources
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Sum, Count
from django.contrib.auth.decorators import login_required, user_passes_test
from ventas.models import Factura
from servicios.models import Servicio
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404, redirect
from ventas.models import Factura


@login_required
@user_passes_test(lambda u: u.is_staff)
def reporte_ventas(request):
    # Estadísticas generales
    total_ventas = Factura.objects.aggregate(total=Sum('total'))['total'] or 0
    facturas_pendientes = Factura.objects.filter(pagado=False).count()
    
    # Ventas por servicio
    ventas_por_servicio = (
        Servicio.objects
        .annotate(total_ventas=Sum('cita__factura__total'))
        .order_by('-total_ventas')
    )
    
    # Ventas últimos 6 meses
    fecha_limite = datetime.now() - timedelta(days=180)
    ventas_mensuales = (
        Factura.objects
        .filter(fecha_emision__gte=fecha_limite)
        .extra({'month': "date_trunc('month', fecha_emision)"} )
        .values('month')
        .annotate(total=Sum('total'))
        .order_by('month')
    )
    
    # Preparar datos para gráficos
    meses = [v['month'].strftime("%b %Y") for v in ventas_mensuales]
    montos = [float(v['total'] or 0) for v in ventas_mensuales]  # Solucionado
    
    servicios_labels = [s.nombre for s in ventas_por_servicio]
    servicios_data = [float(s.total_ventas or 0) for s in ventas_por_servicio]
    
    context = {
        'total_ventas': total_ventas,
        'facturas_pendientes': facturas_pendientes,
        'ventas_mensuales': ventas_mensuales,
        'meses': meses,
        'montos': montos,
        'servicios_labels': servicios_labels,
        'servicios_data': servicios_data,
    }
    
    return render(request, 'admin/reporte_ventas.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def gestion_facturas(request):
    facturas = Factura.objects.select_related('cita__usuario').all()
    return render(request, 'admin/gestion_facturas.html', {
        'facturas': facturas,
        'facturas_pendientes': Factura.objects.filter(pagado=False).count()
    })
class FacturaResource(resources.ModelResource):
    class Meta:
        model = Factura
        fields = ('id', 'cita__mascota__nombre', 'total', 'pagado', 'fecha_emision')
        export_order = fields

@login_required
@user_passes_test(lambda u: u.is_staff)
def exportar_facturas(request):
    # Configurar el recurso de exportación
    dataset = FacturaResource().export()
    
    # Crear la respuesta HTTP
    response = HttpResponse(
        dataset.xlsx,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="facturas_veterinaria.xlsx"'
    
    return response

from django.shortcuts import get_object_or_404
from .models import Factura

def detalle_factura(request, factura_id):
    factura = get_object_or_404(Factura, pk=factura_id)
    return render(request, 'ventas/detalle_factura.html', {'factura': factura})

@login_required
@user_passes_test(lambda u: u.is_staff)
def ver_factura(request, id):
    factura = get_object_or_404(Factura, pk=id)
    return render(request, 'ventas/ver_factura.html', {'factura': factura})

@login_required
@user_passes_test(lambda u: u.is_staff)
def marcar_factura_pagada(request, id):
    factura = get_object_or_404(Factura, pk=id)
    factura.pagado = True
    factura.save()
    return redirect('ventas:gestion_facturas') 