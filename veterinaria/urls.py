from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from usuarios.views import editar_usuario
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

    # Público y Auth
    path('', inicio, name='inicio'),
    path('login/', custom_login, name='login'),
    path('logout/', cerrar_sesion, name='logout'),
    path('registro/', registro, name='registro'),
    path('redirect/', redirect_by_role, name='redirect_by_role'),
    path('cuenta/', include('django.contrib.auth.urls')),

    # Panel de administración (staff)
    path('admin-panel/', panel_administracion, name='panel_administracion'),
    path('admin-panel/usuarios/eliminar/<int:user_id>/', eliminar_usuario, name='eliminar_usuario'),

    # Gestión de citas en admin
    path('admin-panel/citas/', gestion_citas, name='gestion_citas'),
    path('admin-panel/citas/estado/<int:cita_id>/', cambiar_estado_cita, name='cambiar_estado_cita'),

    # Perfil de usuario
    path('perfil/', perfil_usuario, name='perfil_usuario'),
    path('perfil/editar/', editar_perfil, name='editar_perfil'),

    # CRUD Mascotas
    path('mascotas/agregar/', agregar_mascota, name='agregar_mascota'),
    path('mascotas/editar/<int:mascota_id>/', editar_mascota, name='editar_mascota'),
    path('mascotas/eliminar/<int:mascota_id>/', eliminar_mascota, name='eliminar_mascota'),

    # CRUD Servicios
    path('servicios/', gestion_servicios, name='gestion_servicios'),
    path('servicios/crear/', crear_servicio, name='crear_servicio'),
    path('servicios/editar/<slug:slug>/', editar_servicio, name='editar_servicio'),
    path('servicios/eliminar/<slug:slug>/', eliminar_servicio, name='eliminar_servicio'),

    # CRUD Citas usuario
    path('citas/agendar/', agendar_cita, name='agendar_cita'),
    path('citas/historial/', historial_citas, name='historial_citas'),
    path('citas/<int:cita_id>/', detalle_cita, name='detalle_cita'),
    path('citas/editar/<int:cita_id>/', editar_cita, name='editar_cita'),
    path('citas/eliminar/<int:cita_id>/', eliminar_cita, name='eliminar_cita'),
    #ADMINISTRACION
    path('admin-panel/usuarios/editar/<int:user_id>/',
         editar_usuario,
         name='editar_usuario'),
    path('citas/completar/<int:cita_id>/', marcar_completada, name='marcar_completada'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
