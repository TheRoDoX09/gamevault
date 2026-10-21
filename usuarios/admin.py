from django.contrib import admin
from .models import Perfil

# Register your models here.

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'usuario', 'plataforma', 'nacimiento']
    list_filter = ['plataforma']
