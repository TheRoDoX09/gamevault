# GameVault

Los juegos se sacan de la API de [RAWG](https://rawg.io/apidocs). Puedes buscarlos, filtrarlos por género y ver su detalle. Si creas una cuenta, también puedes guardar tus favoritos.

![GameVault](docs/capturas/inicio.jpg)

## Tecnologías

- Django y Django REST Framework
- SimpleJWT para las sesiones
- MySQL
- HTML, CSS y JavaScript

## Cómo correrlo

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Crea la base de datos `gamevault` en MySQL, copia `.env.example` como `.env` y pon tus datos (la clave de RAWG, la contraseña de MySQL, etc.).

```bash
python manage.py migrate
python manage.py runserver
```

Abre http://localhost:8000

## Seguridad

- Las claves van en el archivo `.env`, que no se sube al repositorio.
- La clave de RAWG solo se usa en el servidor, así que el navegador nunca la ve.
- Las contraseñas se guardan cifradas.
- La sesión usa un token JWT guardado en una cookie httpOnly.
- Los formularios se validan en el navegador y otra vez en el servidor.
- Hay un límite de intentos de inicio de sesión.

## Capturas

| Catálogo | Detalle |
|---|---|
| ![](docs/capturas/catalogo.jpg) | ![](docs/capturas/detalle.jpg) |
| **Registro** | **Perfil** |
| ![](docs/capturas/registro.png) | ![](docs/capturas/perfil.jpg) |
