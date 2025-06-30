# Este es el contenido de workout_api/workout_api/urls.py

from django.contrib import admin
from django.urls import path, include  # ¡Asegúrate de que 'include' está aquí!

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),  # <-- Esta es la línea clave que tienes que añadir/modificar
]