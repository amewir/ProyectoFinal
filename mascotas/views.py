from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import MascotaForm
from .models import Mascota

def is_admin(user):
    return user.is_authenticated and user.is_staff

@login_required
def perfil_usuario(request):
    return render(request, 'mascotas/perfil_usuario.html')

@login_required
def agregar_mascota(request):
    if request.method == 'POST':
        form = MascotaForm(request.POST, request.FILES)
        if form.is_valid():
            m = form.save(commit=False)
            m.dueno = request.user
            m.save()
            # redirige según rol
            if request.user.is_staff:
                return redirect('panel_administracion')
            return redirect('perfil_usuario')
    else:
        form = MascotaForm()
    return render(request, 'mascotas/agregar_mascota.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def editar_mascota(request, mascota_id):
    mascota = get_object_or_404(Mascota, id=mascota_id)
    form = MascotaForm(request.POST or None, request.FILES or None, instance=mascota)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Mascota actualizada')
        if request.user.is_staff:
            return redirect('panel_administracion')
        return redirect('perfil_usuario')
    return render(request, 'mascotas/agregar_mascota.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def eliminar_mascota(request, mascota_id):
    mascota = get_object_or_404(Mascota, id=mascota_id)
    if request.method == 'POST':
        mascota.delete()
        messages.success(request, 'Mascota eliminada')
        if request.user.is_staff:
            return redirect('panel_administracion')
        return redirect('perfil_usuario')
    return render(request, 'mascotas/confirmar_eliminacion.html', {'mascota': mascota})
