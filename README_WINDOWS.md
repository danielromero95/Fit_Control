# 🏋️ Gym Performance Analyzer - Guía para Windows 11

## 🚀 Inicio Rápido

### ⚡ Opción 1: Script PowerShell (Recomendado)
```powershell
# Abrir PowerShell como administrador y ejecutar:
.\run_gym_analyzer.ps1
```

### ⚡ Opción 2: Scripts Batch
```batch
# 1. Configuración inicial (solo la primera vez)
setup_windows.bat

# 2. Ejecutar launcher
launcher_windows.bat
```

## 📋 Requisitos Previos

### 1. Anaconda o Miniconda
- **Descarga**: https://www.anaconda.com/products/distribution
- **Instalación**: Ejecutar como administrador
- **Verificación**: Abrir PowerShell y ejecutar `conda --version`

### 2. Python 3.10+
- Se instala automáticamente con Anaconda
- Verificar con: `python --version`

## 🎯 Aplicaciones Disponibles

### 🖥️ Aplicación de Escritorio (Principal)
- **Descripción**: Interfaz completa PyQt para análisis de movimientos
- **Comando**: `.\run_gui_app.bat`
- **Características**:
  - Análisis de videos de ejercicios
  - Detección de posturas
  - Contador de repeticiones
  - Gráficos de rendimiento
  - Base de datos local

### 🌐 Interfaz Web (Demo)
- **Descripción**: Versión web simplificada con Streamlit
- **Comando**: `.\run_streamlit_app.bat`
- **URL**: http://localhost:8501
- **Características**:
  - Análisis rápido de videos
  - Interfaz web moderna
  - Ideal para demostraciones

### 📱 Aplicación Móvil (En desarrollo)
- **Estado**: Código completo pero requiere configuración adicional
- **Tecnología**: React Native
- **Plataformas**: Android e iOS
- **Requisitos adicionales**:
  - Node.js v16+
  - Android Studio (para Android)
  - Xcode (para iOS, solo en macOS)

## 🔧 Configuración Detallada

### Primera Instalación

1. **Descargar e instalar Anaconda**
   ```
   https://www.anaconda.com/products/distribution
   ```

2. **Abrir PowerShell como administrador**
   - Presionar `Win + X`
   - Seleccionar "Windows PowerShell (Admin)"

3. **Navegar al directorio del proyecto**
   ```powershell
   cd "C:\ruta\a\gym-performance-analyzer"
   ```

4. **Ejecutar configuración automática**
   ```powershell
   .\setup_windows.bat
   ```

### Ejecución Diaria

```powershell
# Opción A: Script PowerShell interactivo
.\run_gym_analyzer.ps1

# Opción B: Launcher gráfico
.\launcher_windows.bat

# Opción C: Aplicación específica
.\run_gui_app.bat
.\run_streamlit_app.bat
```

## 🎮 Arquitectura de Aplicaciones

```
🏋️ Gym Performance Analyzer
├── 🖥️ Aplicación de Escritorio (PyQt)
│   ├── Análisis completo de videos
│   ├── Interfaz nativa de Windows
│   └── Base de datos SQLite local
│
├── 🌐 Interfaz Web (Streamlit)
│   ├── Demo rápido y ligero
│   ├── Acceso vía navegador
│   └── Ideal para presentaciones
│
└── 📱 App Móvil (React Native)
    ├── Android (requiere Android Studio)
    ├── iOS (requiere Xcode en macOS)
    └── Funcionalidad completa móvil
```

## ❓ Preguntas Frecuentes

### ¿Realmente son solo 2 aplicaciones principales?
**Respuesta**: Para uso diario en Windows, sí:
1. **Aplicación de Escritorio** (PyQt) - La principal y más completa
2. **Interfaz Web** (Streamlit) - Para demos y análisis rápidos

La aplicación móvil existe pero requiere configuración de desarrollo adicional.

### ¿Necesito emulador para la app móvil?
**Respuesta**: Sí, para ejecutar la app móvil necesitas:
- **Android**: Android Studio con AVD Manager o dispositivo físico
- **iOS**: Xcode con simulador (solo en macOS) o dispositivo físico

**Recomendación**: Usa la aplicación de escritorio que tiene todas las funcionalidades.

### ¿Qué aplicación debo usar?
**Para uso normal**: Aplicación de escritorio (`run_gui_app.bat`)
**Para demos**: Interfaz web (`run_streamlit_app.bat`)
**Para desarrollo móvil**: Configurar React Native por separado

## 🐛 Solución de Problemas

### Error: "conda no encontrado"
```powershell
# 1. Instalar Anaconda
# 2. Reiniciar PowerShell
# 3. Verificar instalación
conda --version
```

### Error: "El sistema no puede encontrar el archivo especificado"
```powershell
# 1. Verificar que estás en el directorio correcto
pwd
ls *.bat

# 2. Ejecutar configuración inicial
.\setup_windows.bat
```

### Error: "Entorno gym_env no encontrado"
```powershell
# Crear entorno manualmente
conda env create -f environment.yml
conda activate gym_env
```

### La aplicación GUI no abre
```powershell
# Verificar dependencias
conda activate gym_env
python -c "import PyQt5; import cv2; import mediapipe; print('OK')"

# Si falla, reinstalar
pip install PyQt5 opencv-python mediapipe
```

## 🆘 Soporte

Si tienes problemas:

1. **Ejecuta el diagnóstico**:
   ```powershell
   .\setup_windows.bat
   ```

2. **Verifica la documentación**: `README.md`, `GUIA_EJECUCION.md`

3. **Logs de error**: Los scripts muestran errores detallados

## 🎯 Resumen para Windows 11

| Aplicación | Comando | Uso Recomendado |
|------------|---------|-----------------|
| 🖥️ Escritorio | `.\run_gui_app.bat` | **Uso principal** |
| 🌐 Web | `.\run_streamlit_app.bat` | Demos y pruebas |
| 🚀 Launcher | `.\launcher_windows.bat` | **Punto de entrada** |
| 🔧 Setup | `.\setup_windows.bat` | **Primera vez** |

**¡Listo para analizar tu rendimiento deportivo en Windows 11! 🏋️‍♀️**