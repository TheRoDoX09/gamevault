from django.contrib.auth.models import User
from django.db import models, transaction


class Perfil(models.Model):
    PLATAFORMAS = [
        ('PC', 'PC'),
        ('PlayStation', 'PlayStation'),
        ('Xbox', 'Xbox'),
        ('Nintendo', 'Nintendo'),
        ('Móvil', 'Móvil'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil', verbose_name='Usuario')
    nombre = models.CharField(max_length=50, verbose_name='Nombre completo')
    nacimiento = models.DateField(verbose_name='Fecha de nacimiento')
    plataforma = models.CharField(max_length=20, choices=PLATAFORMAS, verbose_name='Plataforma favorita')

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    @classmethod
    def crear_usuario(cls, nombre, usuario, email, password, nacimiento, plataforma):
        # Factory Method: encapsula cómo se construye una cuenta. Crea el User de Django
        # (que cifra la contraseña) y su Perfil en una sola transacción.
        with transaction.atomic():
            user = User.objects.create_user(username=usuario, email=email, password=password)
            return cls.objects.create(
                usuario=user,
                nombre=nombre,
                nacimiento=nacimiento,
                plataforma=plataforma
            )
