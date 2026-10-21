from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from .models import Favorito

JUEGO_RAWG = {
    'id': 3498,
    'name': 'Grand Theft Auto V',
    'background_image': 'https://media.rawg.io/media/games/gta5.jpg',
    'released': '2013-09-17',
    'rating': 4.47,
    'metacritic': 92,
    'genres': [{'name': 'Action'}],
    'parent_platforms': [{'platform': {'name': 'PC'}}],
}


def respuesta_rawg(data, status_code=200):
    return Mock(status_code=status_code, ok=status_code < 400, json=Mock(return_value=data))


@override_settings(RAWG_API_KEY='clave-de-prueba')
class JuegosAPITest(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()

    @patch('juegos.services.requests.get')
    def test_buscar_juegos_usa_la_clave_del_servidor(self, mock_get):
        mock_get.return_value = respuesta_rawg({'count': 1, 'next': None, 'results': [JUEGO_RAWG]})
        respuesta = self.client.get('/api/juegos', {'busqueda': 'gta', 'genero': 'action', 'pagina': 999})
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data['total'], 1)
        self.assertEqual(respuesta.data['juegos'][0]['nombre'], 'Grand Theft Auto V')
        self.assertNotIn('clave-de-prueba', str(respuesta.data))

        params = mock_get.call_args.kwargs['params']
        self.assertEqual(params['key'], 'clave-de-prueba')
        self.assertEqual(params['page'], 50)  # la página se limita a 50
        self.assertNotIn('ordering', params)  # con búsqueda RAWG ordena por relevancia

    @patch('juegos.services.requests.get')
    def test_parametros_invalidos_se_descartan(self, mock_get):
        mock_get.return_value = respuesta_rawg({'count': 0, 'next': None, 'results': []})
        self.client.get('/api/juegos', {'genero': '<script>', 'orden': 'DROP TABLE'})
        params = mock_get.call_args.kwargs['params']
        self.assertNotIn('genres', params)
        self.assertEqual(params['ordering'], '-added')

    @patch('juegos.services.requests.get')
    def test_juego_no_encontrado(self, mock_get):
        mock_get.return_value = respuesta_rawg({}, status_code=404)
        respuesta = self.client.get('/api/juegos/999999999')
        self.assertEqual(respuesta.status_code, 404)
        self.assertEqual(respuesta.data['error'], 'Juego no encontrado.')

    @override_settings(RAWG_API_KEY='')
    def test_sin_clave_configurada(self):
        respuesta = self.client.get('/api/generos')
        self.assertEqual(respuesta.status_code, 503)


class FavoritoAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.usuario = User.objects.create_user(username='jugador_64011', password='Gamer#2026x')
        self.client.force_authenticate(user=self.usuario)
        self.favorito = {'id': 3498, 'nombre': 'Grand Theft Auto V', 'imagen': 'https://media.rawg.io/media/games/gta5.jpg'}

    def test_agregar_favorito(self):
        respuesta = self.client.post('/api/favoritos', self.favorito, format='json')
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data['favoritos'], [self.favorito])

    def test_favorito_repetido_no_se_duplica(self):
        self.client.post('/api/favoritos', self.favorito, format='json')
        self.client.post('/api/favoritos', self.favorito, format='json')
        self.assertEqual(Favorito.objects.filter(usuario=self.usuario).count(), 1)

    def test_imagen_externa_rechazada(self):
        respuesta = self.client.post('/api/favoritos', {**self.favorito, 'imagen': 'https://malicioso.com/x.png'}, format='json')
        self.assertEqual(respuesta.status_code, 400)
        self.assertFalse(Favorito.objects.exists())

    def test_quitar_favorito(self):
        self.client.post('/api/favoritos', self.favorito, format='json')
        respuesta = self.client.delete('/api/favoritos/3498')
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data['favoritos'], [])

    def test_favoritos_sin_autenticar(self):
        self.client.force_authenticate(user=None)
        respuesta = self.client.post('/api/favoritos', self.favorito, format='json')
        self.assertEqual(respuesta.status_code, 401)


class FrontendTest(TestCase):
    def test_paginas_y_404(self):
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertEqual(self.client.get('/registro').status_code, 200)
        self.assertEqual(self.client.get('/css/styles.css').status_code, 200)
        self.assertEqual(self.client.get('/no-existe').status_code, 404)
        respuesta = self.client.get('/api/no-existe')
        self.assertEqual(respuesta.status_code, 404)
        self.assertEqual(respuesta.json()['error'], 'Ruta no encontrada.')

    def test_cabeceras_de_seguridad(self):
        respuesta = self.client.get('/')
        self.assertIn("script-src 'self'", respuesta['Content-Security-Policy'])
        self.assertEqual(respuesta['X-Frame-Options'], 'DENY')
        self.assertEqual(respuesta['X-Content-Type-Options'], 'nosniff')
