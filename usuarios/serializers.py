import re
from datetime import date

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from juegos.serializers import FavoritoSerializer
from .models import Perfil

# Mismas reglas que valida el navegador (public/js/registro.js).
# El servidor vuelve a validar todo: nunca se confía solo en el cliente.
REGEX_NOMBRE = re.compile(r'^[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]{3,50}$')
REGEX_USUARIO = re.compile(r'^[A-Za-z0-9_]{4,20}$')
# Mínimo 8 caracteres, una mayúscula, una minúscula, un número y un símbolo
REGEX_PASSWORD = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,64}$')


def calcular_edad(nacimiento):
    hoy = date.today()
    return hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))


class RegistroSerializer(serializers.Serializer):
    nombre = serializers.CharField(trim_whitespace=True)
    usuario = serializers.CharField()
    email = serializers.EmailField(max_length=100)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    confirmar = serializers.CharField(write_only=True, trim_whitespace=False)
    nacimiento = serializers.DateField()
    plataforma = serializers.ChoiceField(choices=Perfil.PLATAFORMAS)
    terminos = serializers.BooleanField()

    def validate_nombre(self, value):
        if not REGEX_NOMBRE.match(value):
            raise serializers.ValidationError('El nombre debe tener de 3 a 50 letras.')
        return value

    def validate_usuario(self, value):
        if not REGEX_USUARIO.match(value):
            raise serializers.ValidationError('Usuario de 4 a 20 caracteres: letras, números o guion bajo.')
        return value

    def validate_email(self, value):
        return value.lower().strip()

    def validate_password(self, value):
        if not REGEX_PASSWORD.match(value):
            raise serializers.ValidationError(
                'La contraseña necesita 8+ caracteres, mayúscula, minúscula, número y símbolo.')
        return value

    def validate_confirmar(self, value):
        if value != self.initial_data.get('password'):
            raise serializers.ValidationError('Las contraseñas no coinciden.')
        return value

    def validate_nacimiento(self, value):
        edad = calcular_edad(value)
        if edad < 13 or edad > 120:
            raise serializers.ValidationError('Debes tener al menos 13 años.')
        return value

    def validate_terminos(self, value):
        if value is not True:
            raise serializers.ValidationError('Debes aceptar los términos y condiciones.')
        return value

    def validate(self, data):
        # Validadores de contraseña de Django (contraseñas comunes, parecida al usuario, etc.)
        try:
            validate_password(data['password'], User(username=data['usuario'], email=data['email']))
        except DjangoValidationError as e:
            raise serializers.ValidationError({'password': e.messages[0]})
        return data

    def create(self, validated_data):
        return Perfil.crear_usuario(
            nombre=validated_data['nombre'],
            usuario=validated_data['usuario'],
            email=validated_data['email'],
            password=validated_data['password'],
            nacimiento=validated_data['nacimiento'],
            plataforma=validated_data['plataforma']
        ).usuario


class UsuarioSerializer(serializers.ModelSerializer):
    # Nunca se envía el hash de la contraseña al cliente
    # default: las cuentas creadas con createsuperuser no tienen Perfil
    nombre = serializers.CharField(source='perfil.nombre', default='')
    usuario = serializers.CharField(source='username')
    plataforma = serializers.CharField(source='perfil.plataforma', default='')
    creado = serializers.DateTimeField(source='date_joined')
    favoritos = FavoritoSerializer(many=True)

    class Meta:
        model = User
        fields = ['id', 'nombre', 'usuario', 'email', 'plataforma', 'creado', 'favoritos']
