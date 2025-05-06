from django.shortcuts import render

def agendar_cita(request):
    return render(request, 'citas/agendar_cita.html')
def nuevo_servicio(request):
    return render(request, 'servicios/nuevo_servicio.html')