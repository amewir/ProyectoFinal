from django.urls import path
from .views import agregar_mascota, perfil_usuario
from . import views


app_name = 'mascotas'

urlpatterns = [
    path('agregar-mascota/', agregar_mascota, name='agregar_mascota'),
    path('panel/', views.perfil_usuario, name='perfil_usuario'),
    path('editar-mascota/<int:mascota_id>/', views.editar_mascota, name='editar_mascota'),
    path('eliminar-mascota/<int:mascota_id>/', views.eliminar_mascota, name='eliminar_mascota'),  

]