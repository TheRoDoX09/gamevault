"""
URL configuration for gamevault project.

- /api/...  Web service REST propio (apps usuarios y juegos)
- /admin/   Panel de administración de Django
- resto     Páginas del frontend (carpeta /public)
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

from .views import api_no_encontrada, pagina, pagina_no_encontrada

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('usuarios.urls')),
    path('api/', include('juegos.urls')),
    re_path(r'^api/', api_no_encontrada),

    # Frontend: /registro y /registro.html muestran la misma página
    path('', pagina),
    re_path(r'^(?P<nombre>[a-z]+)(?:\.html)?$', pagina),
    re_path(r'^(?P<path>(?:css|js)/[\w.-]+|favicon\.svg)$', serve, {'document_root': settings.PUBLIC_DIR}),
    re_path(r'', pagina_no_encontrada),
]
