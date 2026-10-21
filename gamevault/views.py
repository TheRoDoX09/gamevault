# Sirve las páginas del frontend (carpeta /public).
from django.conf import settings
from django.http import FileResponse, JsonResponse

PAGINAS = ['index', 'registro', 'login', 'juegos', 'juego', 'perfil']


def _html(nombre, status=200):
    return FileResponse(open(settings.PUBLIC_DIR / f'{nombre}.html', 'rb'),
                        content_type='text/html; charset=utf-8', status=status)


def pagina(request, nombre='index'):
    if nombre not in PAGINAS:
        return pagina_no_encontrada(request)
    return _html(nombre)


def pagina_no_encontrada(request):
    return _html('404', status=404)


def api_no_encontrada(request):
    return JsonResponse({'error': 'Ruta no encontrada.'}, status=404)
