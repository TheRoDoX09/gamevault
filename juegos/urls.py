from django.urls import path
from .views import agregar_favorito, detalle_juego, generos, lista_juegos, quitar_favorito

urlpatterns = [
    path('juegos', lista_juegos),
    path('juegos/<int:juego_id>', detalle_juego),
    path('generos', generos),
    path('favoritos', agregar_favorito),
    path('favoritos/<int:juego_id>', quitar_favorito),
]
