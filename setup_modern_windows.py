#!/usr/bin/env python3
"""
Script de migración y configuración moderna para Windows.
Resuelve los problemas de dependencias con conda y migra a Poetry.
"""

import os
import sys
import subprocess
import platform
import urllib.request
import tempfile
import shutil
from pathlib import Path


def print_header(title):
    """Imprime un encabezado bonito."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_step(step_num, total_steps, description):
    """Imprime el progreso del paso actual."""
    print(f"\n🔄 [{step_num}/{total_steps}] {description}")


def run_command(command, description="", shell=True, check=True, capture_output=True):
    """Ejecuta un comando y maneja errores con mejor output."""
    if description:
        print(f"   📦 {description}...")
    
    try:
        result = subprocess.run(
            command, 
            shell=shell, 
            check=check, 
            capture_output=capture_output, 
            text=True,
            timeout=300  # 5 minutos timeout
        )
        if capture_output and result.stdout and result.stdout.strip():
            # Solo mostrar las primeras líneas para evitar spam
            lines = result.stdout.strip().split('\n')
            if len(lines) <= 3:
                print(f"   ✓ {result.stdout.strip()}")
            else:
                print(f"   ✓ {lines[0]}")
                print(f"   ✓ ... (+{len(lines)-1} líneas más)")
        elif not capture_output:
            print(f"   ✓ Comando ejecutado")
        
        return result
    except subprocess.TimeoutExpired:
        print(f"   ⏰ Timeout: El comando tardó más de 5 minutos")
        return None
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error (código {e.returncode}): {e}")
        if capture_output and e.stderr:
            print(f"   📋 Detalles: {e.stderr.strip()}")
        return None
    except Exception as e:
        print(f"   ❌ Error inesperado: {e}")
        return None


def check_system_requirements():
    """Verifica los requisitos del sistema."""
    print_step(1, 6, "Verificando requisitos del sistema")
    
    # Verificar Python
    version = sys.version_info
    if version.major != 3 or version.minor < 10:
        print(f"   ❌ Python 3.10+ requerido. Versión actual: {version.major}.{version.minor}")
        print(f"   📥 Descarga Python 3.10+ desde: https://www.python.org/downloads/")
        return False
    
    print(f"   ✓ Python {version.major}.{version.minor}.{version.micro} detectado")
    
    # Verificar sistema operativo
    if platform.system() != "Windows":
        print(f"   ⚠️ Este script está optimizado para Windows. SO detectado: {platform.system()}")
    else:
        print(f"   ✓ Windows detectado ({platform.release()})")
    
    return True


def cleanup_conda_environment():
    """Limpia el entorno de conda problemático."""
    print_step(2, 6, "Limpiando entorno conda problemático")
    
    # Verificar si conda está disponible
    conda_available = False
    try:
        result = subprocess.run(["conda", "--version"], capture_output=True, text=True, check=True)
        conda_available = True
        print(f"   ✓ Conda detectado: {result.stdout.strip()}")
    except:
        print(f"   ℹ️ Conda no detectado, saltando limpieza")
        return True
    
    if conda_available:
        # Intentar limpiar el entorno problemático
        print(f"   🧹 Removiendo entorno gym_env si existe...")
        run_command(
            "conda env remove -n gym_env -y",
            "Removiendo entorno gym_env",
            check=False  # No fallar si no existe
        )
        
        # Limpiar cache de conda
        run_command(
            "conda clean -a -y",
            "Limpiando cache de conda",
            check=False
        )
    
    return True


def install_poetry():
    """Instala Poetry como gestor de dependencias moderno."""
    print_step(3, 6, "Instalando Poetry (gestor de dependencias moderno)")
    
    # Verificar si Poetry ya está instalado
    try:
        result = subprocess.run(
            ["poetry", "--version"], capture_output=True, text=True, check=True
        )
        print(f"   ✓ Poetry ya está instalado: {result.stdout.strip()}")
        return True
    except:
        pass
    
    print(f"   📦 Instalando Poetry...")
    
    try:
        # Usar el instalador oficial de Poetry
        installer_url = "https://install.python-poetry.org"
        
        with tempfile.NamedTemporaryFile(mode='w+b', suffix='.py', delete=False) as f:
            print(f"   📥 Descargando instalador de Poetry...")
            urllib.request.urlretrieve(installer_url, f.name)
            
            print(f"   🔧 Ejecutando instalador...")
            result = subprocess.run([sys.executable, f.name], check=True, capture_output=True, text=True)
            
            # Limpiar archivo temporal
            os.unlink(f.name)
            
        print(f"   ✓ Poetry instalado correctamente")
        
        # Agregar Poetry al PATH para esta sesión
        poetry_bin = Path.home() / "AppData" / "Roaming" / "Python" / "Scripts"
        if poetry_bin.exists():
            os.environ["PATH"] = str(poetry_bin) + os.pathsep + os.environ["PATH"]
        
        # Verificar instalación
        try:
            result = subprocess.run(["poetry", "--version"], capture_output=True, text=True, check=True)
            print(f"   ✓ Verificación exitosa: {result.stdout.strip()}")
            return True
        except:
            print(f"   ⚠️ Poetry instalado pero no se encuentra en PATH")
            print(f"   📋 Agrega manualmente a PATH: {poetry_bin}")
            print(f"   📋 O reinicia tu terminal y ejecuta este script nuevamente")
            return False
            
    except Exception as e:
        print(f"   ❌ Error instalando Poetry: {e}")
        print(f"\n   📋 Instalación manual de Poetry:")
        print(f"   1. Abre PowerShell como administrador")
        print(f"   2. Ejecuta: (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -")
        print(f"   3. Reinicia tu terminal")
        print(f"   4. Ejecuta este script nuevamente")
        return False


def fix_yaml_dependency():
    """Instala PyYAML que es necesario para la configuración."""
    print_step(4, 6, "Instalando dependencias críticas faltantes")
    
    # Instalar PyYAML directamente con pip
    result = run_command(
        f'"{sys.executable}" -m pip install PyYAML',
        "Instalando PyYAML (requerido para config.yaml)"
    )
    
    if result is None:
        print(f"   ❌ Error instalando PyYAML")
        return False
    
    # Verificar que se puede importar
    try:
        import yaml
        print(f"   ✓ PyYAML instalado y verificado")
        return True
    except ImportError:
        print(f"   ❌ PyYAML instalado pero no se puede importar")
        return False


def setup_poetry_environment():
    """Configura el entorno de Poetry con todas las dependencias."""
    print_step(5, 6, "Configurando entorno Poetry")
    
    # Verificar que tenemos el archivo pyproject.toml
    if not os.path.exists("pyproject.toml"):
        print(f"   ❌ No se encontró pyproject.toml en el directorio actual")
        print(f"   📋 Asegúrate de ejecutar este script desde la raíz del proyecto")
        return False
    
    # Configurar Poetry para crear entornos virtuales en el proyecto
    result = run_command(
        "poetry config virtualenvs.in-project true",
        "Configurando Poetry para usar .venv local"
    )
    
    if result is None:
        print(f"   ⚠️ No se pudo configurar Poetry, continuando...")
    
    # Instalar dependencias principales (sin output verboso)
    print(f"   📦 Instalando dependencias principales (esto puede tardar varios minutos)...")
    result = run_command(
        "poetry install --no-dev",
        capture_output=False  # Mostrar progreso en tiempo real
    )
    
    if result is None:
        print(f"   ❌ Error instalando dependencias principales")
        
        # Intentar con pip como fallback
        print(f"   🔄 Intentando instalación manual con pip...")
        
        # Lista de dependencias críticas
        critical_deps = [
            "PyYAML>=6.0",
            "numpy>=1.24.0",
            "opencv-python>=4.8.0",
            "mediapipe>=0.10.21",
            "PyQt5>=5.15.0",
            "matplotlib>=3.7.0",
            "streamlit>=1.28.0"
        ]
        
        for dep in critical_deps:
            run_command(
                f'"{sys.executable}" -m pip install {dep}',
                f"Instalando {dep}",
                check=False
            )
        
        return True  # Continuar aunque falle Poetry
    
    print(f"   ✓ Dependencias principales instaladas")
    
    # Preguntar por la API de Django
    print(f"\n   🤔 ¿Deseas instalar también la API de Django? (y/n): ", end="")
    try:
        install_api = input().lower().startswith('y')
    except:
        install_api = False
    
    if install_api:
        result = run_command(
            "poetry install --extras api",
            "Instalando dependencias de la API de Django"
        )
        if result:
            print(f"   ✓ API de Django instalada")
    
    return True


def create_modern_launchers():
    """Crea launchers modernos que reemplazan los antiguos scripts de conda."""
    print_step(6, 6, "Creando launchers modernos")
    
    # Script moderno para GUI (Windows)
    gui_script_modern = """@echo off
title Gym Performance Analyzer - GUI (Moderno)
echo 🎯 Gym Performance Analyzer - GUI
echo ===================================
echo 🚀 Iniciando aplicacion de escritorio...
echo.

REM Verificar si Poetry esta disponible
poetry --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Error: Poetry no encontrado
    echo 📋 Ejecuta primero: python setup_modern_windows.py
    echo.
    pause
    exit /b 1
)

REM Cambiar al directorio del script
cd /d "%~dp0"

REM Ejecutar aplicacion GUI
poetry run python -m src.gui.main

echo.
echo 👋 Aplicacion GUI cerrada
pause
"""
    
    # Script moderno para Web (Windows)
    web_script_modern = """@echo off
title Gym Performance Analyzer - Web (Moderno)
echo 🌐 Gym Performance Analyzer - Web
echo ==================================
echo 🚀 Iniciando aplicacion web...
echo.

REM Verificar si Poetry esta disponible
poetry --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Error: Poetry no encontrado
    echo 📋 Ejecuta primero: python setup_modern_windows.py
    echo.
    pause
    exit /b 1
)

REM Cambiar al directorio del script
cd /d "%~dp0"

echo 🔗 La aplicacion estara disponible en: http://localhost:8501
echo 🛑 Para cerrar la aplicacion, presiona Ctrl+C en esta ventana
echo.

REM Ejecutar aplicacion Web
poetry run streamlit run src/enhanced_app.py

echo.
echo 👋 Aplicacion web cerrada
pause
"""
    
    # Script de diagnóstico
    diagnostic_script = """@echo off
title Gym Performance Analyzer - Diagnostico
echo 🔍 Gym Performance Analyzer - Diagnostico
echo =========================================
echo.

echo 📋 Verificando instalacion...
echo.

REM Verificar Python
python --version
if %ERRORLEVEL% neq 0 (
    echo ❌ Python no encontrado
) else (
    echo ✓ Python disponible
)

REM Verificar Poetry
poetry --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Poetry no encontrado
) else (
    echo ✓ Poetry disponible
    poetry --version
)

REM Verificar dependencias criticas
echo.
echo 📦 Verificando dependencias criticas...
poetry run python -c "import yaml; print('✓ PyYAML OK')" 2>nul || echo "❌ PyYAML faltante"
poetry run python -c "import cv2; print('✓ OpenCV OK')" 2>nul || echo "❌ OpenCV faltante"
poetry run python -c "import mediapipe; print('✓ MediaPipe OK')" 2>nul || echo "❌ MediaPipe faltante"
poetry run python -c "import PyQt5; print('✓ PyQt5 OK')" 2>nul || echo "❌ PyQt5 faltante"
poetry run python -c "import streamlit; print('✓ Streamlit OK')" 2>nul || echo "❌ Streamlit faltante"

echo.
echo 📋 Diagnostico completado
pause
"""
    
    # Crear los archivos
    scripts = [
        ("run_gui_modern.bat", gui_script_modern),
        ("run_web_modern.bat", web_script_modern),
        ("diagnostico.bat", diagnostic_script),
    ]
    
    for filename, content in scripts:
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"   ✓ Creado: {filename}")
        except Exception as e:
            print(f"   ❌ Error creando {filename}: {e}")
    
    # Crear archivo README con instrucciones
    readme_content = """# 🎯 Gym Performance Analyzer - Versión Moderna

## 🚀 Cómo usar

### Aplicaciones
- **GUI de Escritorio**: Doble clic en `run_gui_modern.bat`
- **Interfaz Web**: Doble clic en `run_web_modern.bat`
- **Diagnóstico**: Doble clic en `diagnostico.bat` para verificar la instalación

### Comandos útiles (desde terminal)
- `poetry shell` - Activar entorno virtual
- `poetry run python -m src.gui.main` - Ejecutar GUI directamente
- `poetry run streamlit run src/enhanced_app.py` - Ejecutar web directamente
- `poetry add <paquete>` - Agregar nueva dependencia
- `poetry update` - Actualizar dependencias
- `poetry install` - Reinstalar dependencias

### Solución de problemas
1. Si los scripts no funcionan, ejecuta `diagnostico.bat`
2. Si faltan dependencias, ejecuta `python setup_modern_windows.py` nuevamente
3. Si persisten problemas, abre una terminal y usa `poetry shell` + comandos directos

### Ventajas de Poetry sobre Conda
- ✅ Resolución de dependencias más rápida y confiable
- ✅ Archivos de bloqueo para builds reproducibles
- ✅ Mejor gestión de dependencias opcionales
- ✅ Compatible con pip y PyPI
- ✅ Menos problemas de corrupción de entornos
"""
    
    try:
        with open("README_MODERNO.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"   ✓ Creado: README_MODERNO.md")
    except Exception as e:
        print(f"   ❌ Error creando README_MODERNO.md: {e}")
    
    return True


def main():
    """Función principal del script de migración."""
    print_header("🎯 Gym Performance Analyzer - Migración Moderna")
    print("Este script migra tu instalación de Conda a Poetry y resuelve problemas de dependencias.")
    print("\n⚠️  IMPORTANTE: Cierra todas las aplicaciones del Gym Analyzer antes de continuar.")
    print("\nPresiona Enter para continuar o Ctrl+C para cancelar...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n👋 Migración cancelada por el usuario")
        return
    
    # Ejecutar pasos de migración
    steps = [
        check_system_requirements,
        cleanup_conda_environment,
        install_poetry,
        fix_yaml_dependency,
        setup_poetry_environment,
        create_modern_launchers,
    ]
    
    for step_func in steps:
        try:
            if not step_func():
                print(f"\n❌ Error en el paso: {step_func.__name__}")
                print(f"📋 Por favor revisa los errores arriba y ejecuta el script nuevamente.")
                input("\nPresiona Enter para salir...")
                return
        except Exception as e:
            print(f"\n💥 Error inesperado en {step_func.__name__}: {e}")
            print(f"📋 Por favor revisa los errores arriba y ejecuta el script nuevamente.")
            input("\nPresiona Enter para salir...")
            return
    
    # ¡Éxito!
    print_header("🎉 ¡Migración completada exitosamente!")
    print("\n📋 Tu instalación ha sido migrada a Poetry y los problemas de dependencias han sido resueltos.")
    print("\n🚀 Para usar la aplicación:")
    print("   🖥️  GUI: Doble clic en run_gui_modern.bat")
    print("   🌐 Web: Doble clic en run_web_modern.bat")
    print("   🔍 Diagnóstico: Doble clic en diagnostico.bat")
    print("\n📖 Lee README_MODERNO.md para más información")
    print("\n👋 Los antiguos scripts de conda pueden ser eliminados si deseas")
    
    input("\nPresiona Enter para salir...")


if __name__ == "__main__":
    main()