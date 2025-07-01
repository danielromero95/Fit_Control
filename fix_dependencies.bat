@echo off
echo ============================================
echo  Reparación Rápida de Dependencias
echo ============================================

:: Activar entorno gym_env
call conda activate gym_env

:: Instalar dependencias faltantes
echo Instalando plotly...
pip install plotly>=5.0.0

echo Instalando requests...
pip install requests>=2.25.0

echo Reparando protobuf...
pip install --force-reinstall protobuf<5,>=4.25.3

echo Instalando otras dependencias críticas...
pip install pydantic<2
pip install PyQt5

:: Verificar instalación
echo.
echo Verificando dependencias...
python -c "
import sys
missing = []

try:
    import plotly
    print('✓ plotly disponible')
except ImportError:
    missing.append('plotly')
    print('✗ plotly falta')

try:
    import requests
    print('✓ requests disponible')
except ImportError:
    missing.append('requests')
    print('✗ requests falta')

try:
    from src.i18n.translator import Translator
    print('✓ src.i18n.translator disponible')
except ImportError as e:
    missing.append('src modules')
    print('✗ src.i18n.translator falta:', e)

if missing:
    print('\nDependencias faltantes:', ', '.join(missing))
    sys.exit(1)
else:
    print('\n✓ Todas las dependencias están disponibles')
"

if %ERRORLEVEL% equ 0 (
    echo.
    echo ============================================
    echo  Reparación completada exitosamente
    echo ============================================
    echo.
    echo Ahora puedes ejecutar:
    echo   run_gui_app.bat - Para la aplicación de escritorio
    echo   run_streamlit_app.bat - Para la interfaz web
    echo.
) else (
    echo.
    echo ============================================
    echo  Algunas dependencias aún faltan
    echo ============================================
    echo.
    echo Ejecuta setup_windows_fixed.bat para una instalación completa
    echo.
)

pause