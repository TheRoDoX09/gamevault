from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from gamevault.throttling import LimiteAuth
from .authentication import cerrar_sesion, crear_sesion
from .serializers import RegistroSerializer, UsuarioSerializer


def primer_error(errores):
    # {'email': ['msg', ...]} -> {'email': 'msg'}, el formato que pinta el formulario
    return {campo: str(lista[0]) for campo, lista in errores.items()}


@api_view(['POST'])
@throttle_classes([LimiteAuth])
def registro(request):
    serializer = RegistroSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'errores': primer_error(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)

    datos = serializer.validated_data
    if User.objects.filter(email__iexact=datos['email']).exists():
        return Response({'errores': {'email': 'Este correo ya está registrado.'}}, status=status.HTTP_409_CONFLICT)
    if User.objects.filter(username__iexact=datos['usuario']).exists():
        return Response({'errores': {'usuario': 'Este nombre de usuario ya existe.'}}, status=status.HTTP_409_CONFLICT)

    try:
        user = serializer.save()
    except IntegrityError:
        return Response({'errores': {'usuario': 'Este nombre de usuario ya existe.'}}, status=status.HTTP_409_CONFLICT)

    response = Response({'mensaje': 'Cuenta creada correctamente.', 'usuario': UsuarioSerializer(user).data},
                        status=status.HTTP_201_CREATED)
    crear_sesion(response, user)
    return response


@api_view(['POST'])
@throttle_classes([LimiteAuth])
def login(request):
    datos = request.data if isinstance(request.data, dict) else {}
    identificador = datos.get('identificador')
    password = datos.get('password')
    if not isinstance(identificador, str) or not isinstance(password, str) or not identificador or not password:
        return Response({'error': 'Escribe tu usuario/correo y contraseña.'}, status=status.HTTP_400_BAD_REQUEST)

    # Se acepta usuario o correo. authenticate() cifra la contraseña aunque el
    # usuario no exista, así el tiempo de respuesta no revela qué cuentas existen.
    identificador = identificador.strip()
    encontrado = User.objects.filter(Q(username__iexact=identificador) | Q(email__iexact=identificador)).first()
    user = authenticate(request, username=encontrado.username if encontrado else identificador, password=password)

    # Mismo mensaje en ambos casos para no revelar qué usuarios existen
    if user is None:
        return Response({'error': 'Usuario o contraseña incorrectos.'}, status=status.HTTP_401_UNAUTHORIZED)

    response = Response({'mensaje': 'Bienvenido de nuevo.', 'usuario': UsuarioSerializer(user).data})
    crear_sesion(response, user)
    return response


@api_view(['POST'])
def logout(request):
    response = Response({'mensaje': 'Sesión cerrada.'})
    cerrar_sesion(response)
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    return Response({'usuario': UsuarioSerializer(request.user).data})
