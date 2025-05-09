from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from ventas.models import Factura

from .forms import CitaForm, SimulacionPagoForm
from .models import Cita


def send_confirmation_email(user, cita):
    asunto = f"Confirmación de cita para {cita.mascota.nombre}"
    cuerpo = f"""
    Detalles de la Cita:
    - Mascota: {cita.mascota.nombre}
    - Servicio: {cita.servicio.nombre}
    - Fecha: {cita.fecha} {cita.hora}
    - Costo: Q{cita.servicio.costo}

    Detalles de Facturación:
    - Nombre: {cita.nombre_facturacion} {cita.apellido_facturacion}
    - DPI: {cita.dpi}
    - NIT/C/F: {cita.nit}
    - Dirección: {cita.direccion_facturacion}
    - Departamento/Municipio: {cita.departamento}/{cita.municipio}
    """
    email = EmailMessage(asunto, cuerpo, to=[user.email])
    email.send()

@login_required
def agendar_cita(request):
    if request.method == 'POST':
        form_cita = CitaForm(request.user, request.POST)
        form_pago = SimulacionPagoForm(request.POST)
        if form_cita.is_valid() and form_pago.is_valid():
            cita = form_cita.save(commit=False)
            cita.usuario = request.user
            # Datos de facturación
            cita.nombre_facturacion = form_pago.cleaned_data['nombre']
            cita.apellido_facturacion = form_pago.cleaned_data['apellido']
            cita.direccion_facturacion = form_pago.cleaned_data['direccion']
            cita.departamento = form_pago.cleaned_data['departamento']
            cita.municipio = form_pago.cleaned_data['municipio']
            cita.dpi = form_pago.cleaned_data['dpi']
            cita.nit = 'CF' if form_pago.cleaned_data['es_consumidor_final'] else form_pago.cleaned_data['nit']
            cita.save()

            # Crear la factura
            Factura.objects.create(cita=cita, total=cita.servicio.costo)

            send_confirmation_email(request.user, cita)
            messages.success(request, '¡Cita agendada y pago simulado exitosamente!')
            return redirect('perfil_usuario')
    else:
        form_cita = CitaForm(request.user)
        form_pago = SimulacionPagoForm()

    return render(request, 'citas/agendar_cita.html', {
        'form_cita': form_cita,
        'form_pago': form_pago
    })

@login_required
def historial_citas(request):
    estado = request.GET.get('estado')
    citas = Cita.objects.filter(usuario=request.user)
    if estado:
        citas = citas.filter(estado=estado)
    return render(request, 'citas/historial.html', {
        'citas': citas,
        'estados': ['pendiente', 'completada', 'cancelada']
    })

@login_required
def editar_cita(request, cita_id):
    # Admin puede editar cualquier cita; usuario solo la suya
    cita = (get_object_or_404(Cita, id=cita_id)
            if request.user.is_staff
            else get_object_or_404(Cita, id=cita_id, usuario=request.user))
    if request.method == 'POST':
        form = CitaForm(request.user, request.POST, instance=cita)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Cita actualizada correctamente!')
            return redirect('panel_administracion' if request.user.is_staff else 'perfil_usuario')
    else:
        form = CitaForm(request.user, instance=cita)
    return render(request, 'citas/editar_cita.html', {
        'form_cita': form,
        'cita': cita
    })

@login_required
def eliminar_cita(request, cita_id):
    # Admin puede eliminar cualquier cita; usuario solo la suya
    cita = (get_object_or_404(Cita, id=cita_id)
            if request.user.is_staff
            else get_object_or_404(Cita, id=cita_id, usuario=request.user))
    if request.method == 'POST':
        cita.delete()
        messages.success(request, '¡Cita eliminada correctamente!')
        return redirect('panel_administracion' if request.user.is_staff else 'perfil_usuario')
    return render(request, 'citas/confirmar_eliminacion.html', {'cita': cita})

@login_required
def marcar_completada(request, cita_id):
    # Permite marcar la cita como completada
    cita = (get_object_or_404(Cita, id=cita_id)
            if request.user.is_staff
            else get_object_or_404(Cita, id=cita_id, usuario=request.user))
    cita.estado = 'completada'
    cita.save()
    messages.success(request, '¡Cita marcada como completada!')
    return redirect('panel_administracion' if request.user.is_staff else 'historial_citas')