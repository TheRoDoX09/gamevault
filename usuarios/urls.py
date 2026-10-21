from django.urls import path
from .views import login, logout, me, registro

urlpatterns = [
    path('registro', registro),
    path('login', login),
    path('logout', logout),
    path('me', me),
]
