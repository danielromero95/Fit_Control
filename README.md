# Gym Performance Analyzer

Proyecto para experimentar con el análisis automático de ejercicios de fuerza combinando vídeo y datos procedentes de wearables. Incluye módulos de preprocesado, estimación de pose, cálculo de métricas y una pequeña aplicación gráfica.

## Requisitos

Se recomienda crear el entorno Conda definido en `environment.yml`:

```bash
conda env create -f environment.yml
```

Luego activa el entorno:

```bash
conda activate gym_env
```

## Pruebas

Las pruebas unitarias se ejecutan con `pytest` desde la raíz del proyecto:

```bash
pytest tests
```

## Estructura

```text
├── config.yaml             # Configuración principal validada con Pydantic
├── environment.yml         # Dependencias para reproducir el entorno
├── docs/
│   └── anteproyecto/
│       └── Anteproyecto-Daniel_Romero_de_Miguel.pdf
├── notebooks/
│   └── inspect_real_angles.ipynb
├── src/
│   ├── A_preprocessing/         # Extracción y preprocesado de vídeo
│   │   ├── frame_extraction.py
│   │   └── video_metadata.py
│   ├── B_pose_estimation/       # Estimadores y utilidades de pose
│   │   ├── estimators.py
│   │   ├── metrics.py
│   │   └── processing.py
│   ├── D_modeling/              # Cálculo de métricas y conteo de repeticiones
│   │   ├── exercise_analyzer.py
│   │   ├── fault_detection.py
│   │   └── math_utils.py
│   ├── F_visualization/         # Renderizado de vídeo y utilidades de dibujo
│   │   ├── drawing_utils.py
│   │   └── video_renderer.py
│   ├── gui/                     # Aplicación PyQt
│   │   ├── main.py
│   │   ├── main_window.py
│   │   ├── worker.py
│   │   └── widgets/
│   │       ├── plot_widget.py
│   │       ├── results_panel.py
│   │       ├── video_display.py
│   │       └── video_player.py
│   ├── app.py                   # Demo en Streamlit
│   ├── config.py                # Carga y validación de config.yaml
│   ├── constants.py             # Constantes generales de la aplicación
│   └── pipeline.py              # Pipeline de análisis en memoria
├── tests/
│   ├── conftest.py
│   ├── test_count_reps.py
│   ├── test_metrics_output.py
│   ├── test_pose_utils.py
│   └── test_video_utils.py
├── themes/                     # Estilos QSS para la GUI
│   ├── dark.qss
│   └── light.qss
└── README.md
```
