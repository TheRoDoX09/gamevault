# Backend de MySQL que permite usar MySQL 8.0.
# Django 6.1 exige MySQL 8.4+ y se detiene al conectar con una versión anterior.
# Es lo mismo que comentar check_database_version_supported() en el Django del venv,
# pero sin modificar librerías: funciona igual al clonar el proyecto.
from django.db.backends.mysql.base import DatabaseWrapper as MySQLDatabaseWrapper


class DatabaseWrapper(MySQLDatabaseWrapper):
    def check_database_version_supported(self):
        pass
