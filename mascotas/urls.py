from django.urls import path
from . import views

urlpatterns = [
    path('agregar/', views.agregar_mascota, name='agregar_mascota'),
]