# 🏋️ Guía de Ejecución - Gym Performance Analyzer

Esta guía te ayudará a ejecutar fácilmente todas las aplicaciones del proyecto Gym Performance Analyzer para ver el progreso de tu trabajo.

## 🚀 Ejecución Rápida

### Opción 1: Script Maestro (Recomendado)
```bash
./run_app.sh
```

Este script te permitirá elegir qué aplicación ejecutar con un menú interactivo.

### Opción 2: Ejecutar aplicaciones individuales

#### 🖥️ Aplicación GUI (Interfaz de Escritorio)
```bash
./run_gui_app.sh
```
- **Descripción**: Interfaz completa de escritorio con PyQt
- **Características**: Análisis de vídeo, seguimiento de progreso, planes de entrenamiento
- **Requisitos**: Conda, entorno `gym_env`

#### 🌐 Demo Streamlit (Interfaz Web)
```bash
./run_streamlit_app.sh
```
- **Descripción**: Interfaz web simplificada para demostraciones
- **URL**: http://localhost:8501
- **Características**: Análisis rápido de vídeos de ejercicios
- **Requisitos**: Conda, entorno `gym_env`

#### 🔧 API Django (Backend)
```bash
./run_django_api.sh
```
- **Descripción**: API REST para gestión de entrenamientos
- **URL**: http://localhost:8000
- **Panel Admin**: http://localhost:8000/admin (admin/admin123)
- **Documentación**: http://localhost:8000/api/
- **Requisitos**: Python 3, entorno virtual

#### 📱 Aplicación Móvil (React Native)
```bash
./run_mobile_app.sh
```
- **Descripción**: App móvil FitControl para dispositivos Android/iOS
- **Características**: Registro de entrenamientos, seguimiento móvil
- **Requisitos**: Node.js, React Native CLI, Android SDK/Xcode

## 📋 Requisitos del Sistema

### Para todas las aplicaciones:
- **Sistema Operativo**: Linux (preferiblemente Ubuntu/Debian)
- **Python**: 3.10 o superior
- **Git**: Para clonar el repositorio

### Para la Aplicación GUI y Streamlit:
- **Conda**: Para gestión de entornos
- **OpenCV**: Para procesamiento de vídeo
- **PyQt5**: Para la interfaz gráfica

### Para la API Django:
- **Python 3**: Con pip
- **SQLite**: Base de datos (incluida en Python)

### Para la Aplicación Móvil:
- **Node.js**: 16 o superior
- **npm**: Gestor de paquetes de Node
- **Android SDK**: Para desarrollo Android
- **Xcode**: Para desarrollo iOS (solo macOS)

## 🔧 Configuración Inicial

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd gym-performance-analyzer
```

### 2. Hacer ejecutables los scripts
```bash
chmod +x *.sh
```

### 3. Instalar Conda (si no está instalado)
```bash
# En Ubuntu/Debian
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

### 4. Instalar Node.js (para la app móvil)
```bash
# En Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## 🚀 Ejecución paso a paso

### Opción A: Ejecución individual
1. Ejecuta el script maestro: `./run_app.sh`
2. Selecciona la aplicación que quieres probar (1-4)
3. Sigue las instrucciones en pantalla

### Opción B: Ejecución en paralelo
1. Ejecuta el script maestro: `./run_app.sh`
2. Selecciona la opción 5 "Ejecutar todas las aplicaciones"
3. Se abrirán múltiples terminales con cada aplicación

## 📱 URLs de Acceso

Una vez ejecutadas las aplicaciones, podrás acceder a:

| Aplicación | URL | Descripción |
|------------|-----|-------------|
| Streamlit Demo | http://localhost:8501 | Interfaz web de análisis |
| Django API | http://localhost:8000 | API REST principal |
| Admin Django | http://localhost:8000/admin | Panel de administración |
| Documentación API | http://localhost:8000/api/ | Documentación interactiva |

## 🎯 Funcionalidades por Aplicación

### 🖥️ Aplicación GUI
- ✅ Análisis de vídeos de ejercicios
- ✅ Estimación de pose con MediaPipe
- ✅ Conteo automático de repeticiones
- ✅ Seguimiento de progreso
- ✅ Generación de planes de entrenamiento
- ✅ Visualización de métricas

### 🌐 Demo Streamlit
- ✅ Carga y análisis de vídeos
- ✅ Visualización en tiempo real
- ✅ Exportación de resultados
- ✅ Interfaz web intuitiva

### 🔧 API Django
- ✅ Gestión de usuarios
- ✅ CRUD de entrenamientos
- ✅ Análisis de datos
- ✅ Autenticación JWT
- ✅ API REST completa

### 📱 Aplicación Móvil
- ✅ Registro de entrenamientos
- ✅ Seguimiento de progreso
- ✅ Interfaz nativa
- ✅ Sincronización con API

## 🐛 Solución de Problemas

### Error: "conda: command not found"
```bash
# Instalar Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
source ~/.bashrc
```

### Error: "node: command not found"
```bash
# Instalar Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### Error: "permission denied"
```bash
# Hacer ejecutables los scripts
chmod +x *.sh
```

### Error en aplicación móvil: "ADB not found"
```bash
# Instalar Android SDK o usar Android Studio
sudo apt install android-sdk-platform-tools
```

## 📞 Soporte

Si tienes problemas:
1. Verifica que todos los requisitos estén instalados
2. Revisa los logs de error en la terminal
3. Asegúrate de que los puertos no estén en uso
4. Consulta la documentación específica de cada tecnología

## 🎉 ¡Listo para usar!

Ahora puedes ejecutar cualquiera de las aplicaciones y ver el progreso de tu trabajo de forma fácil y rápida. ¡Disfruta explorando el Gym Performance Analyzer!

---

**Nota**: La primera ejecución puede tardar más tiempo debido a la instalación de dependencias. Las ejecuciones posteriores serán mucho más rápidas.