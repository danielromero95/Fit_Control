# Gym Performance Analyzer

Proyecto para experimentar con el análisis automático de ejercicios de fuerza combinando vídeo y datos procedentes de wearables. Incluye módulos de preprocesado, estimación de pose, cálculo de métricas y una pequeña aplicación gráfica.

El objetivo real de la aplicación es ofrecer una plataforma integral que permita:

* Generar planes de entrenamiento personalizados basados en IA.
* Analizar de forma técnica la ejecución de cada ejercicio.
* Registrar y visualizar el progreso del usuario a lo largo del tiempo.

## 🚀 Ejecución Rápida

Para ejecutar fácilmente cualquier aplicación:

```bash
./run_app.sh
```

O ejecuta aplicaciones individuales:

```bash
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
└── README.md
```
