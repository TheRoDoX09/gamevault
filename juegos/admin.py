from django.contrib import admin
from .models import Favorito

# Register your models here.

@admin.register(Favorito)
class FavoritoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'juego_id', 'usuario', 'creado']
    list_filter = ['usuario']
