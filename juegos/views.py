import re

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from gamevault.throttling import LimiteRAWG
from .models import Favorito
from .serializers import FavoritoSerializer
from .services import ClienteRAWG

ORDENES = ['-rating', '-released', '-added', '-metacritic', 'name']
REGEX_GENERO = re.compile(r'^[a-z0-9-]{1,40}$')
MAX_FAVORITOS = 100


# ---------- Consumo de la API externa (RAWG) ----------

@api_view(['GET'])
@throttle_classes([LimiteRAWG])
def lista_juegos(request):
    # Los parámetros se validan antes de enviarlos a la API externa
    busqueda = request.query_params.get('busqueda', '')[:80]
    genero = request.query_params.get('genero', '')
    orden = request.query_params.get('orden')
    try:
        pagina = int(request.query_params.get('pagina', 1))
    except ValueError:
        pagina = 1

    return Response(ClienteRAWG().buscar_juegos(
        busqueda=busqueda,
        genero=genero if REGEX_GENERO.match(genero) else None,
        orden=orden if orden in ORDENES else '-added',
        pagina=min(max(pagina, 1), 50)
    ))


@api_view(['GET'])
@throttle_classes([LimiteRAWG])
def detalle_juego(request, juego_id):
    return Response(ClienteRAWG().detalle_juego(juego_id))


@api_view(['GET'])
@throttle_classes([LimiteRAWG])
def generos(request):
    return Response(ClienteRAWG().generos())


# ---------- Favoritos (rutas protegidas) ----------

def favoritos_de(user):
    return FavoritoSerializer(user.favoritos.all(), many=True).data


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def agregar_favorito(request):
    serializer = FavoritoSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'error': 'Datos de juego no válidos.'}, status=status.HTTP_400_BAD_REQUEST)

    juego_id = serializer.validated_data['juego_id']
    if not request.user.favoritos.filter(juego_id=juego_id).exists():
        if request.user.favoritos.count() >= MAX_FAVORITOS:
            return Response({'error': f'Máximo {MAX_FAVORITOS} favoritos.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(usuario=request.user)
    return Response({'favoritos': favoritos_de(request.user)})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def quitar_favorito(request, juego_id):
    Favorito.objects.filter(usuario=request.user, juego_id=juego_id).delete()
    return Response({'favoritos': favoritos_de(request.user)})
