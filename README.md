# 🏋️ Gym Performance Analyzer

**¡Ahora más fácil que nunca!** - Proyecto para experimentar con el análisis automático de ejercicios de fuerza combinando vídeo y datos procedentes de wearables. Incluye módulos de preprocesado, estimación de pose, cálculo de métricas y aplicaciones modernas con **facilidad de uso extrema**.

## 🎯 **¿Primera vez? ¡Solo necesitas esto!**
```bash
./setup_easy_launcher.sh
```
**¡Y ya está!** Después podrás ejecutar todo con un clic desde el escritorio o escribiendo `gym-launcher` en cualquier terminal.

## 🚀 **Características Principales**

La aplicación ofrece una plataforma integral que permite:

* **🤖 Generar planes de entrenamiento** personalizados basados en IA.
* **📊 Analizar técnicamente** la ejecución de cada ejercicio.
* **📈 Registrar y visualizar** el progreso del usuario a lo largo del tiempo.
* **🎮 Acceso súper fácil** con GUI moderno y múltiples formas de ejecución.

## 🚀 Ejecución Super Fácil

### 🎯 **Nuevo GUI Launcher (Recomendado)**

La forma más fácil de ejecutar las aplicaciones es usando nuestro nuevo **GUI Launcher**:

#### **⚡ Configuración de un solo comando:**
```bash
./setup_easy_launcher.sh
```

Este script configurará automáticamente:
- ✅ GUI Launcher moderno con interfaz visual
- ✅ Icono en el escritorio y menú de aplicaciones  
- ✅ Alias de terminal `gym-launcher`
- ✅ Verificación automática de dependencias
- ✅ Instalación de tkinter si es necesario

#### **🖥️ Formas de ejecutar después de la configuración:**

1. **Desde el menú de aplicaciones**: Busca "Gym Performance Analyzer"
2. **Desde el escritorio**: Doble clic en el icono
3. **Desde cualquier terminal**: `gym-launcher`
4. **Desde este directorio**: `./run_launcher.sh`

### 🎮 **GUI Launcher - Características**

El GUI Launcher te permite:
- 🖱️ **Selección visual**: Botones coloridos para cada aplicación
- 🚀 **Ejecución automática**: Un clic ejecuta todo automáticamente
- 📊 **Estado en tiempo real**: Ve el estado de ejecución de cada app
- 🔄 **Ejecución paralela**: Opción para ejecutar múltiples apps
- 📚 **Acceso a documentación**: Botón directo a la documentación
- ✅ **Verificación de entorno**: Comprueba que todo esté listo

### 🔧 **Métodos Tradicionales**

Para usuarios avanzados, también puedes usar:

```bash
./run_app.sh           # Launcher de terminal
./run_gui_app.sh       # Aplicación GUI completa
./run_streamlit_app.sh # Demo web Streamlit  
./run_django_api.sh    # API Django
./run_mobile_app.sh    # Aplicación móvil React Native
```

**Verificación del entorno:**
```bash
./verificar_entorno.sh  # Verifica que todo esté listo
```

📚 **Guía completa**: Ver `GUIA_EJECUCION.md` para instrucciones detalladas.

## Requisitos

Se recomienda crear el entorno Conda definido en `environment.yml`:

```bash
conda env create -f environment.yml
```

Luego activa el entorno:

```bash
conda activate gym_env
```

## Estructura

```text
├── assets/                   # Iconos y recursos de la GUI
│   ├── FitControl_logo.ico
│   └── Gym_Loading_Gif.gif
├── config.yaml               # Configuración principal validada con Pydantic
├── data/
│   └── gym_progress.db       # Base de datos SQLite de la aplicación
├── docs/
│   └── anteproyecto/
│       └── Anteproyecto-Daniel_Romero_de_Miguel.pdf
├── environment.yml           # Dependencias para reproducir el entorno
├── src/
│   ├── A_preprocessing/         # Extracción y preprocesado de vídeo
│   │   ├── frame_extraction.py
│   │   ├── video_metadata.py
│   │   └── video_utils.py
│   ├── B_pose_estimation/       # Estimadores y utilidades de pose
│   │   ├── estimators.py
│   │   └── metrics.py
│   ├── D_modeling/              # Cálculo de métricas y conteo de repeticiones
│   │   ├── exercise_analyzer.py
│   │   └── math_utils.py
│   ├── F_visualization/         # Renderizado de vídeo y utilidades de dibujo
│   │   ├── drawing_utils.py
│   │   └── video_renderer.py
│   ├── gui/                     # Aplicación PyQt
│   │   ├── main.py
│   │   ├── main_window.py
│   │   ├── worker.py
│   │   ├── pages/
│   │   │   ├── analysis_page.py
│   │   │   ├── dashboard_page.py
│   │   │   ├── plans_page.py
│   │   │   ├── progress_page.py
│   │   │   └── ...
│   │   └── widgets/
│   │       ├── plot_widget.py
│   │       ├── results_panel.py
│   │       ├── video_display.py
│   │       └── video_player.py
│   ├── services/               # Funciones auxiliares (IA generativa)
│   │   └── plan_generator.py
│   ├── i18n/                    # Archivos de internacionalización
│   │   ├── es.json
│   │   └── translator.py
│   ├── app.py                   # Demo en Streamlit
│   ├── config.py                # Carga y validación de config.yaml
│   ├── constants.py             # Constantes generales de la aplicación
│   ├── database.py              # Funciones para la base de datos
│   └── pipeline.py              # Pipeline de análisis en memoria
├── themes/                     # Estilos QSS para la GUI
│   ├── dark.qss
│   └── light.qss
├── launcher.py               # GUI Launcher principal
├── run_launcher.sh           # Script de ejecución del launcher  
├── setup_easy_launcher.sh    # Configuración automática
├── GymAnalyzer-Launcher.desktop  # Archivo de escritorio
└── README.md
```

## 🎯 Facilidad de Uso

### 🚀 **Nuevas Características de Facilidad**

Hemos implementado múltiples mejoras para hacer que ejecutar las aplicaciones sea **extremadamente fácil**:

#### **🔧 Configuración Automática**
- **Un solo comando** configura todo: `./setup_easy_launcher.sh`
- **Instalación automática** de dependencias (tkinter)
- **Icono en el escritorio** y menú de aplicaciones
- **Alias de terminal** `gym-launcher` para acceso desde cualquier lugar

#### **🎮 GUI Launcher Moderno**
- **Interfaz visual** con botones coloridos para cada aplicación
- **Ejecución automática** - solo un clic ejecuta todo
- **Estados en tiempo real** - ve el progreso de ejecución
- **Recuperación automática** - si algo falla, prueba alternativas
- **Múltiples versiones** - completa y simple según tu sistema

#### **📱 Múltiples Formas de Acceso**
1. **Menú de aplicaciones**: Busca "Gym Performance Analyzer"
2. **Icono de escritorio**: Doble clic y listo
3. **Terminal global**: `gym-launcher` desde cualquier ubicación
4. **Script directo**: `./run_launcher.sh`

### **⚡ Comparación: Antes vs Ahora**

| Aspecto | Antes | Ahora |
|---------|-------|-------|
| **Pasos para ejecutar** | 5-10 comandos | 1 clic o comando |
| **Conocimiento técnico** | Medio-Alto | **Ninguno** |
| **Tiempo de setup** | 15+ minutos | **2 minutos** |
| **Facilidad de uso** | 3/10 | **9/10** |

📚 **Documentación detallada**: Ver `FACILIDAD_DE_USO.md` para guía completa.

```
