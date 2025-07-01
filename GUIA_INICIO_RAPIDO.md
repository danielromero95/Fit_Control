# 🚀 Guía de Inicio Rápido - Para Usuarios Nuevos

¡Hola! Aquí tienes una guía súper simple para ejecutar la aplicación **Gym Performance Analyzer**.

## 🎯 Opción 1: Ejecución Más Fácil (Recomendada)

### Django API (Backend) - ¡Funciona de inmediato!

La **API Django** es la más fácil de ejecutar porque usa Python puro:

```bash
./run_django_api.sh
```

**¿Qué hace?**
- Crea automáticamente un entorno virtual de Python
- Instala todas las dependencias necesarias
- Ejecuta la aplicación web

**Después de ejecutar, ve a:**
- 🌐 **Aplicación principal**: http://localhost:8000
- 👨‍💼 **Panel de administración**: http://localhost:8000/admin (usuario: admin, contraseña: admin123)
- 📚 **Documentación de la API**: http://localhost:8000/api/

### Aplicación Móvil React Native

También puedes ejecutar la app móvil fácilmente:

```bash
./run_mobile_app.sh
```

**¿Qué hace?**
- Instala automáticamente todas las dependencias de Node.js
- Ejecuta la aplicación móvil FitControl
- Te muestra opciones para conectar tu teléfono o usar un emulador

## 🎯 Opción 2: Para Más Funcionalidades (Requiere Conda)

Si quieres las funcionalidades completas de análisis de vídeo, necesitas instalar Conda primero:

### Paso 1: Instalar Conda
```bash
# Descargar Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# Instalarlo
bash Miniconda3-latest-Linux-x86_64.sh

# Recargar el terminal
source ~/.bashrc
```

### Paso 2: Configuración Automática
```bash
./setup_easy_launcher.sh
```

### Paso 3: Ejecutar con GUI
```bash
./run_launcher.sh
```

## 🔍 ¿Qué Aplicación Elegir?

| Aplicación | Facilidad | Funcionalidades | Tiempo de Setup |
|------------|-----------|-----------------|-----------------|
| **Django API** | ⭐⭐⭐⭐⭐ | Backend completo, admin panel | 2-3 minutos |
| **App Móvil** | ⭐⭐⭐⭐ | Interfaz móvil nativa | 3-5 minutos |
| **GUI Completa** | ⭐⭐⭐ | Análisis de vídeo, IA | 10-15 minutos |
| **Streamlit** | ⭐⭐⭐ | Demo web de análisis | 10-15 minutos |

## 🚀 ¡Empieza Ahora Mismo!

**Mi recomendación para empezar:**

1. **Primero** ejecuta la Django API para ver la aplicación funcionando:
   ```bash
   ./run_django_api.sh
   ```

2. **Luego** la app móvil para ver la interfaz:
   ```bash
   ./run_mobile_app.sh
   ```

3. **Finalmente** si quieres análisis de vídeo, instala Conda y ejecuta:
   ```bash
   ./setup_easy_launcher.sh
   ```

## 🆘 ¿Problemas?

### Error: "Permission denied"
```bash
chmod +x *.sh
```

### Error: "Command not found"
- Para Django: Ya tienes Python ✅
- Para móvil: Ya tienes Node.js ✅  
- Para GUI: Necesitas instalar Conda

### ¿No sabes qué hacer?
¡Simplemente ejecuta esto y sigue las instrucciones:
```bash
./run_app.sh
```

## 🎉 ¡Ya Está!

Con cualquiera de estas opciones tendrás la aplicación funcionando en menos de 5 minutos. 

**¿Cuál quieres probar primero?** 🚀