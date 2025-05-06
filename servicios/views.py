from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ServicioForm
from .models import Servicio

@permission_required('servicios.gestion_servicios')
def gestion_servicios(request):
    servicios = Servicio.objects.all()
    return render(request, 'servicios/gestion_servicios.html', {
        'servicios': servicios
    })

@permission_required('servicios.gestion_servicios')
def crear_servicio(request):
    if request.method == 'POST':
        form = ServicioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Servicio creado exitosamente!')
            return redirect('gestion_servicios')
    else:
        form = ServicioForm()
    
    return render(request, 'servicios/form_servicio.html', {
        'form': form,
        'titulo': 'Nuevo Servicio'
    })

@permission_required('servicios.gestion_servicios')
def editar_servicio(request, slug):
    servicio = get_object_or_404(Servicio, slug=slug)
    if request.method == 'POST':
        form = ServicioForm(request.POST, request.FILES, instance=servicio)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Servicio actualizado correctamente!')
            return redirect('gestion_servicios')
    else:
        form = ServicioForm(instance=servicio)
    
    return render(request, 'servicios/form_servicio.html', {
        'form': form,
        'titulo': f'Editar {servicio.nombre}'
    })