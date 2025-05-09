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
    path('factura/<int:id>/', views.ver_factura, name='ver_factura'),
    path('marcar-factura-pagada/<int:id>/', views.marcar_factura_pagada, name='marcar_factura_pagada'),
    path('factura/<int:id>/marcar_pagada/', views.marcar_factura_pagada, name='marcar_factura_pagada'),
    path('facturas/', views.gestion_facturas, name='gestion_facturas'),


]