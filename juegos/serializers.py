from rest_framework import serializers
from .models import Favorito


class FavoritoSerializer(serializers.ModelSerializer):
    # El frontend envía/recibe {id, nombre, imagen}; "id" es el id del juego en RAWG
    id = serializers.IntegerField(source='juego_id', min_value=1)

    class Meta:
        model = Favorito
        fields = ['id', 'nombre', 'imagen']

    def validate_imagen(self, value):
        # Solo imágenes del CDN de RAWG (la CSP tampoco permite otras)
        if value and not value.startswith('https://media.rawg.io/'):
            raise serializers.ValidationError('Imagen no válida.')
        return value or None
