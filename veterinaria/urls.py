from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from usuarios.views import editar_usuario
from django.contrib.auth import views as auth_views
from usuarios.forms import CustomPasswordResetForm
from usuarios.forms import CustomSetPasswordForm
from django.contrib import admin
from django.urls import path, include
from usuarios.views import CustomPasswordResetConfirmView

from citas.views import (
    agendar_cita,
    historial_citas,
    editar_cita,
    eliminar_cita,
    marcar_completada,   # <- aquí
)


from usuarios.views import (
    inicio, custom_login, registro, redirect_by_role,
    panel_administracion, perfil_usuario, cerrar_sesion,
    editar_perfil, eliminar_usuario, detalle_cita,
    gestion_citas, cambiar_estado_cita
)
from mascotas.views import (
    agregar_mascota, editar_mascota, eliminar_mascota
)
from citas.views import (
    agendar_cita, historial_citas, editar_cita, eliminar_cita
)
from servicios.views import (
    gestion_servicios, crear_servicio, editar_servicio, eliminar_servicio
)

urlpatterns = [
    # Admin Django
    path('admin/', admin.site.urls),
    
    # URLs de usuarios    
    path('usuarios/', include('usuarios.urls')), 
    # Auth y páginas públicas
    path('', inicio, name='inicio'),
    path('login/', custom_login, name='login'),
    path('logout/', cerrar_sesion, name='logout'),
    path('registro/', registro, name='registro'),
    path('redirect/', redirect_by_role, name='redirect_by_role'),
    
    # Password reset
    path('password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='password_reset/password_reset_form.html',
            email_template_name='password_reset/password_reset_email.html',
            subject_template_name='password_reset/password_reset_subject.txt'
        ),
        name='password_reset'),
    
    path('password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='password_reset/password_reset_done.html'
        ),
        name='password_reset_done'),
    
    path(
    'reset/<uidb64>/<token>/',
    CustomPasswordResetConfirmView.as_view(
        template_name='password_reset/password_reset_confirm.html',
        form_class=CustomSetPasswordForm
    ),
    name='password_reset_confirm'
),
    
    
    
    path('reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='password_reset/password_reset_complete.html'
        ),
        name='password_reset_complete'),
    
    # Panel de administración
    path('admin-panel/', panel_administracion, name='panel_administracion'),
    path('admin-panel/usuarios/eliminar/<int:user_id>/', eliminar_usuario, name='eliminar_usuario'),
    path('admin-panel/usuarios/editar/<int:user_id>/', editar_usuario, name='editar_usuario'),
    
    # Gestión de citas
    path('admin-panel/citas/', gestion_citas, name='gestion_citas'),
    path('admin-panel/citas/estado/<int:cita_id>/', cambiar_estado_cita, name='cambiar_estado_cita'),
    
    # Perfil de usuario
    path('perfil/', perfil_usuario, name='perfil_usuario'),
    path('perfil/editar/', editar_perfil, name='editar_perfil'),
    
    # Mascotas
    path('mascotas/agregar/', agregar_mascota, name='agregar_mascota'),
    path('mascotas/editar/<int:mascota_id>/', editar_mascota, name='editar_mascota'),
    path('mascotas/eliminar/<int:mascota_id>/', eliminar_mascota, name='eliminar_mascota'),
    
    # Servicios
    path('servicios/', gestion_servicios, name='gestion_servicios'),
    path('servicios/crear/', crear_servicio, name='crear_servicio'),
    path('servicios/editar/<slug:slug>/', editar_servicio, name='editar_servicio'),
    path('servicios/eliminar/<slug:slug>/', eliminar_servicio, name='eliminar_servicio'),
    
    # Citas
    path('citas/agendar/', agendar_cita, name='agendar_cita'),
    path('citas/historial/', historial_citas, name='historial_citas'),
    path('citas/<int:cita_id>/', detalle_cita, name='detalle_cita'),
    path('citas/editar/<int:cita_id>/', editar_cita, name='editar_cita'),
    path('citas/eliminar/<int:cita_id>/', eliminar_cita, name='eliminar_cita'),
    path('citas/completar/<int:cita_id>/', marcar_completada, name='marcar_completada'),
    
    #modulos
    path('rh/', include('recursos_humanos.urls')),
    path('rh/', include(('recursos_humanos.urls', 'recursos_humanos'), namespace='recursos_humanos')),
    path('ventas/', include(('ventas.urls', 'ventas'), namespace='ventas')),
    path('mascotas/', include(('mascotas.urls', 'mascotas'), namespace='mascotas')),
    path('servicios/', include(('servicios.urls', 'servicios'), namespace='servicios')),
    path('citas/', include(('citas.urls', 'citas'), namespace='citas')),
    path('inventarios/', include(('inventarios.urls', 'inventarios'), namespace='inventarios')),



    
    
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

