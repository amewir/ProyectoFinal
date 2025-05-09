from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Medicamento, MovimientoInventario
from .forms import MedicamentoForm

from recursos_humanos.models import Nomina




def is_admin(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_admin)
def gestion_medicamentos(request):
    medicamentos = Medicamento.objects.all().order_by('nombre')
    stock_bajo = Medicamento.objects.filter(stock__lt=10)
    
    return render(request, 'inventarios/gestion_medicamentos.html', {
        'medicamentos': medicamentos,
        'stock_bajo': stock_bajo,
        'total_medicamentos': medicamentos.count()
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def lista_medicamentos(request):
    medicamentos = Medicamento.objects.all()
    return render(request, 'inventarios/lista_medicamentos.html', {'medicamentos': medicamentos})

from django.core.paginator import Paginator

@login_required
@user_passes_test(is_admin)
def movimientos_inventario(request):
    # Obtener todos los movimientos ordenados por fecha
    movimientos = MovimientoInventario.objects.all().order_by('-fecha')
    
    # Paginación (10 elementos por página)
    paginator = Paginator(movimientos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas
    total_entradas = MovimientoInventario.objects.filter(tipo='entrada').count()
    total_salidas = MovimientoInventario.objects.filter(tipo='salida').count()
    
    return render(request, 'admin/movimientos_inventario.html', {
        'page_obj': page_obj,
        'total_entradas': total_entradas,
        'total_salidas': total_salidas
    })

from django.utils import timezone
from datetime import timedelta

@login_required
@user_passes_test(is_admin)
def alertas_inventario(request):
    # Medicamentos con stock bajo (<10 unidades)
    stock_bajo = Medicamento.objects.filter(stock__lt=10).order_by('stock')
    
    # Medicamentos próximos a caducar (30 días o menos)
    fecha_alerta = timezone.now().date() + timedelta(days=30)
    caducidad_proxima = Medicamento.objects.filter(
        fecha_caducidad__lte=fecha_alerta
    ).order_by('fecha_caducidad')
    
    return render(request, 'admin/alertas_inventario.html', {
        'stock_bajo': stock_bajo,
        'caducidad_proxima': caducidad_proxima,
        'fecha_alerta': fecha_alerta
    })

@login_required
@user_passes_test(is_admin)
def crear_medicamento(request):
    if request.method == 'POST':
        form = MedicamentoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventarios:gestion_medicamentos')
    else:
        form = MedicamentoForm()
    
    return render(request, 'admin/form_medicamento.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def actualizar_stock(request, medicamento_id):
    medicamento = Medicamento.objects.get(id=medicamento_id)
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad'))
        tipo = request.POST.get('tipo')
        
        if tipo == 'entrada':
            medicamento.stock += cantidad
        elif tipo == 'salida':
            medicamento.stock -= cantidad
        
        medicamento.save()
        
        # Registrar movimiento
        MovimientoInventario.objects.create(
            medicamento=medicamento,
            tipo=tipo,
            cantidad=cantidad,
            responsable=request.user.username
        )
        
        return redirect('inventarios:gestion_medicamentos')
    
    return render(request, 'admin/actualizar_stock.html', {
        'medicamento': medicamento
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def gestion_nominas(request):
    nominas = Nomina.objects.all()
    return render(request, 'admin/gestion_nominas.html', {'nominas': nominas})