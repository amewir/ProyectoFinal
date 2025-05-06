from django.urls import path
from .views import agendar_cita , nuevo_servicio

urlpatterns = [
    path('agendar/', agendar_cita, name='agendar_cita'),
    path('nuevo/', nuevo_servicio, name='nuevo_servicio'),

]