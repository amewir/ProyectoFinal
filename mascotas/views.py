from django.shortcuts import render, redirect
from .forms import MascotaForm
from django.contrib.auth.decorators import login_required

@login_required
def agregar_mascota(request):
    if request.method == 'POST':
        form = MascotaForm(request.POST, request.FILES)
        if form.is_valid():
            nueva_mascota = form.save(commit=False)
            nueva_mascota.dueno = request.user  # Asignar dueño automáticamente
            nueva_mascota.save()
            return redirect('lista_mascotas')  # Redirigir a la lista de mascotas
    else:
        form = MascotaForm()
    
    return render(request, 'mascotas/agregar_mascota.html', {
        'form': form,
        'titulo_pagina': 'Registrar nueva mascota'
    })