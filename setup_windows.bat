@echo off
echo ============================================
echo  Gym Performance Analyzer - Configuración
echo ============================================

:: Verificar si conda está disponible
where conda >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Conda no encontrado.
    echo.
    echo Por favor instala Anaconda o Miniconda:
    echo https://www.anaconda.com/products/distribution
    echo.
    echo Después de instalar, reinicia PowerShell y ejecuta este script nuevamente.
    pause
    exit /b 1
)

echo Conda encontrado. Procediendo con la configuración...

:: Crear entorno conda
echo.
echo [1/4] Creando entorno conda 'gym_env'...
call conda env create -f environment.yml
if %ERRORLEVEL% neq 0 (
    echo Actualizando entorno existente...
    call conda env update -f environment.yml --prune
)

:: Activar entorno
echo.
echo [2/4] Activando entorno...
call conda activate gym_env

:: Instalar dependencias adicionales de pip
echo.
echo [3/4] Instalando dependencias adicionales...
pip install --upgrade pip
pip install PyQt5 opencv-python mediapipe streamlit django djangorestframework

:: Verificar instalación
echo.
echo [4/4] Verificando instalación...
python -c "
import sys
print(f'Python {sys.version}')

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
    import streamlit
    print('✓ Streamlit instalado')
except ImportError:
    print('✗ Streamlit falta')
"

echo.
echo ============================================
echo  Configuración completada
echo ============================================
echo.
echo Para ejecutar las aplicaciones:
echo   - GUI de escritorio: run_gui_app.bat
echo   - Interfaz web: run_streamlit_app.bat
echo   - Launcher: launcher_windows.bat
echo.
pause