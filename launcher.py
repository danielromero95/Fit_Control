#!/usr/bin/env python3
"""
Launcher GUI para Gym Performance Analyzer
Script principal para ejecutar el launcher gráfico
"""

import sys
import os
from pathlib import Path

# Añadir el directorio src al path para importar módulos
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

try:
    from gui.app_launcher import main
    main()
except ImportError as e:
    print(f"Error importando módulos: {e}")
    print("Asegúrate de que el entorno esté configurado correctamente.")
    print("Ejecuta: conda env create -f environment.yml && conda activate gym_env")
    sys.exit(1)
except Exception as e:
    print(f"Error ejecutando launcher: {e}")
    sys.exit(1)