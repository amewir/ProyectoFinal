from django.urls import path
from .views import gestion_empleados, gestion_nominas, gestion_viajes
from .views import gestion_empleados, crear_empleado, editar_empleado, eliminar_empleado


app_name = 'recursos_humanos'

urlpatterns = [
    path('empleados/', gestion_empleados, name='gestion_empleados'),
    path('nominas/', gestion_nominas, name='gestion_nominas'),
    path('viajes/', gestion_viajes, name='gestion_viajes'),
    path('empleados/', gestion_empleados, name='gestion_empleados'),
    path('empleados/nuevo/', crear_empleado, name='crear_empleado'),
    path('empleados/editar/<int:empleado_id>/', editar_empleado, name='editar_empleado'),
    path('empleados/eliminar/<int:empleado_id>/', eliminar_empleado, name='eliminar_empleado'),
    
]