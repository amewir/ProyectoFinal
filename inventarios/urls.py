from django.urls import path
from .views import gestion_medicamentos, movimientos_inventario, alertas_inventario
from .views import gestion_medicamentos, crear_medicamento, actualizar_stock

app_name = 'inventarios'

urlpatterns = [
    path('medicamentos/', gestion_medicamentos, name='gestion_medicamentos'),
    path('movimientos/', movimientos_inventario, name='movimientos_inventario'),
    path('alertas/', alertas_inventario, name='alertas_inventario'),
    path('medicamentos/nuevo/', crear_medicamento, name='crear_medicamento'),
    path('medicamentos/stock/<int:medicamento_id>/', actualizar_stock, name='actualizar_stock'),
    
]