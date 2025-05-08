from django.urls import path
from .views import registro, cerrar_sesion, custom_login
from usuarios.views import cerrar_sesion, editar_perfil
from usuarios.views import agregar_mascota, editar_usuario
from citas.views import agendar_cita
from .views import editar_usuario, lista_usuarios


from . import views
urlpatterns = [
    path('registro/', registro, name='registro'),
    path('login/', custom_login, name='login'),
    path('logout/', cerrar_sesion, name='logout'),
    path('perfil/editar/', editar_perfil, name='editar_perfil'),
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('agregar-mascota/', agregar_mascota, name='agregar_mascota'),
    path('agendar-cita/', agendar_cita, name='agendar_cita'),
    path('admin-panel/usuarios/editar/<int:user_id>/', editar_usuario, name='editar_usuario'),
    path('usuarios/', lista_usuarios, name='lista_usuarios'),
]
