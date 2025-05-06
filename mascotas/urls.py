from django.urls import path
from .views import agregar_mascota

urlpatterns = [
    path('agregar-mascota/', agregar_mascota, name='agregar_mascota'),
]