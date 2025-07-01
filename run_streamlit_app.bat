@echo off
echo ======================================
echo  Gym Performance Analyzer - Streamlit
echo ======================================

:: Verificar si conda está disponible
where conda >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Conda no encontrado. Instala Anaconda o Miniconda.
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

:: Verificar streamlit
python -c "import streamlit" 2>nul
if %ERRORLEVEL% neq 0 (
    echo Instalando Streamlit...
    pip install streamlit
)

:: Ejecutar aplicación
echo Iniciando servidor Streamlit...
echo La aplicación se abrirá en: http://localhost:8501
streamlit run src/enhanced_app.py --server.port=8501

pause