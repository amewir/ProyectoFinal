# recursos_humanos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from usuarios.models import Usuario
from .models import Empleado, Nomina, SolicitudViaje
from .forms import EmpleadoForm, NominaForm, SolicitudViajeForm
from .forms import EmpleadoForm, NominaForm , EmpleadoCreacionForm
# Función de verificación de administrador
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model

from .models import Empleado
from .forms import UsuarioForm, EmpleadoForm

User = get_user_model()

def is_admin(user):
    return user.is_authenticated and user.is_staff
# ---------------------------------------------------
# Gestión de Empleados
# ---------------------------------------------------
@login_required
@user_passes_test(is_admin)
def gestion_empleados(request):
    empleados = Empleado.objects.select_related('usuario').all()
    return render(request, 'admin/gestion_empleados.html', {
        'empleados': empleados,
        'roles': Empleado.PUESTOS_CHOICES
    })
@login_required
@user_passes_test(is_admin)
def crear_empleado(request):
    if request.method == 'POST':
        form = EmpleadoCreacionForm(request.POST)
        usuario_form = UsuarioForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('recursos_humanos:gestion_empleados')
    else:
        form = EmpleadoCreacionForm()
        usuario_form = UsuarioForm()

    return render(request, 'recursos_humanos/crear_empleado.html', {
        'form_empleado': form,
    })
@login_required
@user_passes_test(is_admin)
def editar_empleado(request, empleado_id):
    empleado = get_object_or_404(Empleado, id=empleado_id)
    usuario_form = UsuarioForm(request.POST or None, instance=empleado.usuario)
    empleado_form = EmpleadoForm(request.POST or None, instance=empleado)

    if request.method == 'POST':
        if usuario_form.is_valid() and empleado_form.is_valid():
            usuario_form.save()
            empleado_form.save()
            return redirect('recursos_humanos:gestion_empleados')  # Redirige a la lista de empleados después de guardar

    return render(request, 'recursos_humanos/editar_empleado.html', {
        'empleado': empleado,
        'form_usuario': usuario_form,
        'form_empleado': empleado_form,
    })
    
        
@login_required
@user_passes_test(is_admin)
def eliminar_empleado(request, empleado_id):
    empleado = get_object_or_404(Empleado, id=empleado_id)
    if request.method == 'POST':
        empleado.delete()
        messages.success(request, 'Empleado eliminado')
    return redirect('recursos_humanos:gestion_empleados')

# ---------------------------------------------------
# Gestión de Nóminas
# ---------------------------------------------------
@login_required
@user_passes_test(is_admin)
def gestion_nominas(request):
    nominas = Nomina.objects.all().select_related('empleado')
    return render(request, 'admin/gestion_nominas.html', {
        'nominas': nominas,
        'total_nominas': nominas.count()
    })

@login_required
@user_passes_test(is_admin)
def generar_nomina(request, empleado_id):
    empleado = get_object_or_404(Empleado, id=empleado_id)
    if request.method == 'POST':
        form = NominaForm(request.POST)
        if form.is_valid():
            nomina = form.save(commit=False)
            nomina.empleado = empleado
            nomina.salario_neto = nomina.calcular_salario_neto()
            nomina.save()
            messages.success(request, 'Nómina generada exitosamente')
            return redirect('recursos_humanos:gestion_nominas')
    else:
        form = NominaForm(initial={'empleado': empleado})
    
    return render(request, 'admin/form_nomina.html', {'form': form})

# ---------------------------------------------------
# Gestión de Viajes
# ---------------------------------------------------
@login_required
@user_passes_test(is_admin)
def gestion_viajes(request):
    viajes = SolicitudViaje.objects.select_related('empleado').all()
    return render(request, 'admin/gestion_viajes.html', {
        'viajes': viajes,
        'empleados': Empleado.objects.all()
    })

@login_required
@user_passes_test(is_admin)
def aprobar_viaje(request, viaje_id):
    viaje = get_object_or_404(SolicitudViaje, id=viaje_id)
    viaje.aprobado = True
    viaje.save()
    messages.success(request, 'Viaje aprobado exitosamente')
    return redirect('recursos_humanos:gestion_viajes')

@login_required
@user_passes_test(is_admin)
def nuevo_viaje(request):
    if request.method == 'POST':
        form = SolicitudViajeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('recursos_humanos:gestion_viajes')
    else:
        form = SolicitudViajeForm()
    return render(request, 'recursos_humanos/form_viaje.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def nueva_nomina(request):
    if request.method == 'POST':
        form = NominaForm(request.POST)
        if form.is_valid():
            nomina = form.save(commit=False)
            nomina.salario_neto = nomina.calcular_salario_neto()
            nomina.save()
            return redirect('recursos_humanos:gestion_nominas')
    else:
        form = NominaForm()
    return render(request, 'recursos_humanos/form_nomina.html', {'form': form})