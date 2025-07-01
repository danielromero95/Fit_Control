@echo off
echo ====================================
echo  Gym Performance Analyzer - Web App
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
python -c "import streamlit; import cv2; import mediapipe; import plotly; import requests" 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Dependencias faltantes. Instalando...
    pip install streamlit opencv-python mediapipe plotly requests
)

:: Cambiar al directorio del proyecto
cd /d "%~dp0"

:: Añadir el directorio actual al PYTHONPATH para imports relativos
set PYTHONPATH=%CD%;%PYTHONPATH%

:: Ejecutar aplicación web
echo Iniciando aplicación web en http://localhost:8501
streamlit run src/enhanced_app.py

pause