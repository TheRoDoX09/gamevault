from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient
from .models import Perfil

DATOS_REGISTRO = {
    'nombre': 'Juan Pérez',
    'usuario': 'jugador_64011',
    'email': 'Jugador_64011@Correo.com',
    'password': 'Gamer#2026x',
    'confirmar': 'Gamer#2026x',
    'nacimiento': '2003-04-15',
    'plataforma': 'PC',
    'terminos': True,
}


class RegistroAPITest(TestCase):
    def setUp(self):
        cache.clear()  # reinicia el rate limiting entre pruebas
        self.client = APIClient()

    def test_registro_crea_usuario_y_sesion(self):
        respuesta = self.client.post('/api/registro', DATOS_REGISTRO, format='json')
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.data['usuario']['usuario'], 'jugador_64011')
        self.assertEqual(respuesta.data['usuario']['email'], 'jugador_64011@correo.com')
        self.assertNotIn('password', respuesta.data['usuario'])
        self.assertTrue(respuesta.cookies['token']['httponly'])
        self.assertEqual(respuesta.cookies['token']['samesite'], 'Strict')
        self.assertEqual(Perfil.objects.get(usuario__username='jugador_64011').plataforma, 'PC')

    def test_password_se_guarda_cifrada(self):
        self.client.post('/api/registro', DATOS_REGISTRO, format='json')
        user = User.objects.get(username='jugador_64011')
        self.assertNotEqual(user.password, DATOS_REGISTRO['password'])
        self.assertTrue(user.check_password(DATOS_REGISTRO['password']))

    def test_registro_con_datos_invalidos(self):
        respuesta = self.client.post('/api/registro', {
            **DATOS_REGISTRO,
            'nombre': 'A1',
            'usuario': 'ab',
            'email': 'correo-malo',
            'password': 'abc',
            'confirmar': 'xyz',
            'nacimiento': '2020-01-01',
            'plataforma': 'Atari',
            'terminos': False,
        }, format='json')
        self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(
            set(respuesta.data['errores']),
            {'nombre', 'usuario', 'email', 'password', 'confirmar', 'nacimiento', 'plataforma', 'terminos'}
        )
        self.assertFalse(User.objects.exists())

    def test_usuario_o_correo_duplicado(self):
        self.client.post('/api/registro', DATOS_REGISTRO, format='json')
        respuesta = self.client.post('/api/registro', {**DATOS_REGISTRO, 'usuario': 'otro_jugador'}, format='json')
        self.assertEqual(respuesta.status_code, 409)
        self.assertIn('email', respuesta.data['errores'])
        respuesta = self.client.post('/api/registro', {**DATOS_REGISTRO, 'email': 'otro@correo.com', 'usuario': 'JUGADOR_64011'}, format='json')
        self.assertEqual(respuesta.status_code, 409)
        self.assertIn('usuario', respuesta.data['errores'])


class LoginAPITest(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        Perfil.crear_usuario(
            nombre='Juan Pérez', usuario='jugador_64011', email='jugador_64011@correo.com',
            password='Gamer#2026x', nacimiento='2003-04-15', plataforma='PC'
        )

    def test_login_con_usuario_o_correo(self):
        for identificador in ['jugador_64011', 'JUGADOR_64011@correo.com']:
            respuesta = self.client.post('/api/login', {'identificador': identificador, 'password': 'Gamer#2026x'}, format='json')
            self.assertEqual(respuesta.status_code, 200)
            self.assertIn('token', respuesta.cookies)

    def test_mensaje_generico_en_login_fallido(self):
        mala_password = self.client.post('/api/login', {'identificador': 'jugador_64011', 'password': 'Incorrecta#1'}, format='json')
        no_existe = self.client.post('/api/login', {'identificador': 'fantasma', 'password': 'Incorrecta#1'}, format='json')
        self.assertEqual(mala_password.status_code, 401)
        self.assertEqual(mala_password.data, no_existe.data)
        self.assertEqual(mala_password.data['error'], 'Usuario o contraseña incorrectos.')

    def test_me_requiere_sesion(self):
        respuesta = self.client.get('/api/me')
        self.assertEqual(respuesta.status_code, 401)
        self.assertEqual(respuesta.data['error'], 'Debes iniciar sesión.')

    def test_me_y_logout(self):
        self.client.post('/api/login', {'identificador': 'jugador_64011', 'password': 'Gamer#2026x'}, format='json')
        respuesta = self.client.get('/api/me')
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data['usuario']['nombre'], 'Juan Pérez')
        self.assertEqual(respuesta.data['usuario']['favoritos'], [])

        self.client.post('/api/logout')
        self.assertEqual(self.client.get('/api/me').status_code, 401)

    def test_token_alterado_no_da_acceso(self):
        self.client.cookies['token'] = 'eyJ0eXAiOiJKV1QifQ.falso.falso'
        self.assertEqual(self.client.get('/api/me').status_code, 401)

    def test_rate_limit_en_login(self):
        for _ in range(20):
            self.client.post('/api/login', {'identificador': 'jugador_64011', 'password': 'Incorrecta#1'}, format='json')
        respuesta = self.client.post('/api/login', {'identificador': 'jugador_64011', 'password': 'Gamer#2026x'}, format='json')
        self.assertEqual(respuesta.status_code, 429)
        self.assertIn('Demasiados intentos', respuesta.data['error'])
