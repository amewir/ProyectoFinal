from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from usuarios.views import inicio, custom_login  # Importación única y ordenada
from django.urls import path
from usuarios.views import inicio, custom_login, registro, redirect_by_role
from usuarios.views import inicio, panel_administracion, perfil_usuario, cerrar_sesion
from servicios.views import agendar_cita


from django.urls import include
from django.contrib.auth.views import LoginView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', inicio, name='inicio'),
    path('login/', custom_login, name='login'),
    path('registro/', registro, name='registro'),
    path('redirect/', redirect_by_role, name='redirect_by_role'),
    path('admin-panel/', panel_administracion, name='panel_administracion'),
    path('perfil/', perfil_usuario, name='perfil_usuario'),
    path('logout/', cerrar_sesion, name='cerrar_sesion'),
    path('cuenta/', include('django.contrib.auth.urls')),
    path('cuenta/login/', LoginView.as_view(template_name='usuarios/login.html')),  # Ruta personalizada
    path('cuenta/', include('django.contrib.auth.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('mascotas/', include('mascotas.urls')),
    path('citas/', include('servicios.urls')),
    path('citas/agendar/', agendar_cita, name='agendar_cita'),
    path('servicios/', include('servicios.urls')),

]

# Configuración para archivos multimedia (solo desarrollo)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)