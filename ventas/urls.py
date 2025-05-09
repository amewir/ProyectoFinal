# ventas/urls.py
from django.urls import path
from .views import gestion_facturas, exportar_facturas, reporte_ventas
from . import views
app_name = 'ventas'

urlpatterns = [
    path('exportar-facturas/', exportar_facturas, name='exportar_facturas'),
    path('facturas/', gestion_facturas, name='gestion_facturas'),
    path('reportes/', reporte_ventas, name='reporte_ventas'),
    path('facturas/<int:factura_id>/', views.detalle_factura, name='detalle_factura'),

]