from django.urls import path
from .views import agendar_cita
from .views import editar_cita, eliminar_cita
from . import views

app_name = 'citas'

urlpatterns = [
    path('agendar/', agendar_cita, name='agendar_cita'),
    path('editar/<int:cita_id>/', editar_cita, name='editar_cita'),
    path('eliminar/<int:cita_id>/', eliminar_cita, name='eliminar_cita'),
    path('cita/<int:cita_id>/completar/', views.marcar_completada, name='marcar_completada'),

]