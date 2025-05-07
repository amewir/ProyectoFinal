from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .forms import ServicioForm
from .models import Servicio

@permission_required('servicios.gestion_servicios')
def gestion_servicios(request):
    return render(request, 'servicios/gestion_servicios.html', {
        'servicios': Servicio.objects.all()
    })

@permission_required('servicios.gestion_servicios')
def crear_servicio(request):
    if request.method == 'POST':
        form = ServicioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Servicio creado')
            return redirect('gestion_servicios')
    else:
        form = ServicioForm()
    return render(request, 'servicios/form_servicio.html', {'form': form})

@permission_required('servicios.gestion_servicios')
def editar_servicio(request, slug):
    servicio = get_object_or_404(Servicio, slug=slug)
    form = ServicioForm(request.POST or None, request.FILES or None, instance=servicio)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Servicio actualizado')
        return redirect('gestion_servicios')
    return render(request, 'servicios/form_servicio.html', {'form': form})

@permission_required('servicios.gestion_servicios')
def eliminar_servicio(request, slug):
    servicio = get_object_or_404(Servicio, slug=slug)
    if request.method == 'POST':
        servicio.delete()
        messages.success(request, 'Servicio eliminado')
        return redirect('gestion_servicios')
    return render(request, 'servicios/confirmar_eliminacion.html', {'servicio': servicio})
