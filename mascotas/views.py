from django.shortcuts import render

def agregar_mascota(request):
    return render(request, 'mascotas/agregar_mascota.html')