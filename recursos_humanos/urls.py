from django.urls import path
from . import views

app_name = 'recursos_humanos'

urlpatterns = [
    path('empleados/', views.gestion_empleados, name='gestion_empleados'),
    path('empleados/nuevo/', views.crear_empleado, name='crear_empleado'),
    path('empleados/<int:empleado_id>/editar/', views.editar_empleado, name='editar_empleado'),
    path('empleados/<int:empleado_id>/eliminar/', views.eliminar_empleado, name='eliminar_empleado'),

    path('nominas/', views.gestion_nominas, name='gestion_nominas'),
    path('nominas/nueva/', views.nueva_nomina, name='nueva_nomina'),

    path('viajes/', views.gestion_viajes, name='gestion_viajes'),
    path('viajes/nuevo/', views.nuevo_viaje, name='nuevo_viaje'),
   

]
