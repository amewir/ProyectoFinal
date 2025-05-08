from django.urls import path
from .views import agregar_mascota, perfi_usuario
from . import views

urlpatterns = [
    path('agregar-mascota/', agregar_mascota, name='agregar_mascota'),
    path('panel/', views.perfil_usuario, name='perfil_usuario'),

]