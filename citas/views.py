from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CitaForm
from .models import Cita

@login_required
def agendar_cita(request):
    if request.method == 'POST':
        # Pasa el usuario al formulario
        form = CitaForm(request.user, request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            # Asigna el usuario correctamente (depende de tu modelo)
            cita.usuario = request.user # O cita.creado_por según tu modelo
            cita.save()
            messages.success(request, '¡Cita agendada exitosamente!')
            return redirect('perfil_usuario')
    else:
        form = CitaForm(request.user)  # Pasa el usuario aquí también
    
    return render(request, 'citas/agendar_cita.html', {
        'form': form,
        'titulo_pagina': 'Agendar Nueva Cita'
    })