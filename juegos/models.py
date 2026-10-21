from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Favorito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favoritos', verbose_name='Usuario')
    juego_id = models.PositiveIntegerField(verbose_name='ID del juego en RAWG')
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    imagen = models.URLField(max_length=500, null=True, blank=True, verbose_name='Imagen')
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Favorito'
        verbose_name_plural = 'Favoritos'
        ordering = ['creado']
        constraints = [
            models.UniqueConstraint(fields=['usuario', 'juego_id'], name='favorito_unico_por_usuario'),
        ]

    def __str__(self):
        return self.nombre
