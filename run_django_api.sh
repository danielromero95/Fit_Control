#!/bin/bash

# Script para ejecutar la API Django del Workout API
echo "🔧 Iniciando Django Workout API..."

# Cambiar al directorio workout_api
cd workout_api

# Verificar si existe un entorno virtual
if [ ! -d "venv" ]; then
    echo "🔧 Creando entorno virtual Python..."
    python3 -m venv venv
fi

# Activar el entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

# Ejecutar migraciones
echo "🗄️ Ejecutando migraciones de base de datos..."
python manage.py makemigrations
python manage.py migrate

# Crear superusuario si no existe (opcional)
echo "👤 Verificando superusuario..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superusuario creado: admin/admin123')
else:
    print('Superusuario ya existe: admin/admin123')
"

# Ejecutar el servidor
echo "🚀 Iniciando servidor Django..."
echo "📱 La API estará disponible en: http://localhost:8000"
echo "🔧 Panel de administración: http://localhost:8000/admin"
echo "📖 Documentación API: http://localhost:8000/api/"
python manage.py runserver 0.0.0.0:8000

echo "✅ API Django finalizada"