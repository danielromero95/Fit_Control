@echo off
echo ====================================
echo  Gym Performance Analyzer - GUI App
echo ====================================

:: Verificar si conda está disponible
where conda >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Conda no encontrado. Instala Anaconda o Miniconda.
    echo Descarga desde: https://www.anaconda.com/products/distribution
    pause
    exit /b 1
)

:: Activar entorno
echo Activando entorno gym_env...
call conda activate gym_env
if %ERRORLEVEL% neq 0 (
    echo Error: No se pudo activar el entorno gym_env
    echo Ejecuta primero: conda env create -f environment.yml
    pause
    exit /b 1
)

:: Verificar dependencias críticas
python -c "import PyQt5; import cv2; import mediapipe" 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Dependencias faltantes. Instalando...
    pip install PyQt5 opencv-python mediapipe pyqtgraph qtawesome
)

:: Ejecutar aplicación GUI
echo Iniciando aplicación GUI...
python src/gui/main.py

if %ERRORLEVEL% neq 0 (
    echo Error al ejecutar la aplicación GUI
    pause
    exit /b 1
)

echo Aplicación cerrada correctamente.
pause