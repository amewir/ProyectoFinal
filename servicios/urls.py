from django.urls import path
from . import views
from .views import gestion_servicios, crear_servicio, editar_servicio

urlpatterns = [
    path('gestion/', gestion_servicios, name='gestion_servicios'),
   path('nuevo/', crear_servicio, name='crear_servicio'),
    path('editar/<slug:slug>/', editar_servicio, name='editar_servicio'),
]