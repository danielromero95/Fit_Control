@echo off
echo ============================================
echo  Gym Performance Analyzer - Configuración Completa
echo ============================================

:: Verificar si conda está disponible
where conda >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Conda no encontrado. Instala Anaconda o Miniconda.
    echo Descarga desde: https://www.anaconda.com/products/distribution
    pause
    exit /b 1
)

echo [1/5] Limpiando entorno anterior (si existe)...
call conda env remove -n gym_env -y 2>nul

echo [2/5] Creando nuevo entorno conda...
call conda env create -f environment.yml
if %ERRORLEVEL% neq 0 (
    echo Error: No se pudo crear el entorno conda
    pause
    exit /b 1
)

echo [3/5] Activando entorno...
call conda activate gym_env
if %ERRORLEVEL% neq 0 (
    echo Error: No se pudo activar el entorno
    pause
    exit /b 1
)

echo [4/5] Instalando dependencias adicionales...
pip install --upgrade pip
pip install plotly>=5.0.0
pip install requests>=2.25.0
pip install pydantic<2
pip install streamlit
pip install PyQt5
pip install opencv-python
pip install mediapipe==0.10.21
pip install pyqtgraph
pip install qtawesome
pip install matplotlib
pip install moviepy==1.0.3

echo [5/5] Verificando instalación...
python -c "
try:
    import PyQt5
    print('✓ PyQt5 instalado')
except ImportError:
    print('✗ PyQt5 falta')

try:
    import cv2
    print('✓ OpenCV instalado')
except ImportError:
    print('✗ OpenCV falta')

try:
    import mediapipe
    print('✓ MediaPipe instalado')
except ImportError:
    print('✗ MediaPipe falta')

try:
    import plotly
    print('✓ Plotly instalado')
except ImportError:
    print('✗ Plotly falta')

try:
    import requests
    print('✓ Requests instalado')
except ImportError:
    print('✗ Requests falta')

try:
    import streamlit
    print('✓ Streamlit instalado')
except ImportError:
    print('✗ Streamlit falta')
"

echo.
echo ============================================
echo  Configuración completada exitosamente
echo ============================================
echo.
echo Para ejecutar las aplicaciones:
echo   - GUI de escritorio: run_gui_app.bat
echo   - Interfaz web: run_streamlit_app.bat
echo   - Launcher principal: launcher_windows.bat
echo.

pause