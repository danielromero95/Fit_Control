@echo off
echo =============================================
echo  Gym Performance Analyzer - Launcher Windows
echo =============================================

:: Verificar si conda está disponible
where conda >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Conda no encontrado.
    echo.
    echo Ejecuta setup_windows.bat primero para configurar el entorno.
    pause
    exit /b 1
)

:: Activar entorno
echo Activando entorno gym_env...
call conda activate gym_env
if %ERRORLEVEL% neq 0 (
    echo Error: No se pudo activar el entorno gym_env
    echo Ejecuta setup_windows.bat primero.
    pause
    exit /b 1
)

:: Ejecutar launcher específico para Windows
echo Iniciando Launcher...
python launcher_windows.py

if %ERRORLEVEL% neq 0 (
    echo Error al ejecutar el launcher
    pause
    exit /b 1
)

echo Launcher cerrado.
pause