#!/usr/bin/env python3
"""
Script de configuración moderna para Gym Performance Analyzer.
Este script instala Poetry y configura el entorno de desarrollo automáticamente.
"""

import os
import sys
import subprocess
import platform
import urllib.request
import tempfile
from pathlib import Path


def run_command(command, description="", shell=True, check=True):
    """Ejecuta un comando y maneja errores."""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(
            command, shell=shell, check=check, capture_output=True, text=True
        )
        if result.stdout:
            print(f"   ✓ {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e}")
        if e.stderr:
            print(f"   Error details: {e.stderr.strip()}")
        return None


def check_python_version():
    """Verifica que la versión de Python sea compatible."""
    version = sys.version_info
    if version.major != 3 or version.minor < 10:
        print(f"❌ Python 3.10+ requerido. Versión actual: {version.major}.{version.minor}")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} detectado")
    return True


def install_poetry():
    """Instala Poetry si no está disponible."""
    try:
        result = subprocess.run(
            ["poetry", "--version"], capture_output=True, text=True, check=True
        )
        print(f"✓ Poetry ya está instalado: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("📦 Instalando Poetry...")
        
        # URL del instalador de Poetry
        poetry_installer_url = "https://install.python-poetry.org"
        
        try:
            # Descargar e instalar Poetry
            with tempfile.NamedTemporaryFile(mode='w+b', suffix='.py', delete=False) as f:
                urllib.request.urlretrieve(poetry_installer_url, f.name)
                
                # Ejecutar el instalador
                result = subprocess.run([sys.executable, f.name], check=True, capture_output=True, text=True)
                
                # Limpiar archivo temporal
                os.unlink(f.name)
                
            print("✓ Poetry instalado correctamente")
            
            # Agregar Poetry al PATH para esta sesión
            poetry_bin = Path.home() / ".local" / "bin"
            if platform.system() == "Windows":
                poetry_bin = Path.home() / "AppData" / "Roaming" / "Python" / "Scripts"
            
            os.environ["PATH"] = str(poetry_bin) + os.pathsep + os.environ["PATH"]
            
            return True
            
        except Exception as e:
            print(f"❌ Error instalando Poetry: {e}")
            print("\n📋 Instalación manual de Poetry:")
            if platform.system() == "Windows":
                print("   1. Abre PowerShell como administrador")
                print("   2. Ejecuta: (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -")
            else:
                print("   1. Ejecuta: curl -sSL https://install.python-poetry.org | python3 -")
            print("   3. Reinicia tu terminal")
            print("   4. Ejecuta este script nuevamente")
            return False


def setup_poetry_environment():
    """Configura Poetry y instala dependencias."""
    
    # Configurar Poetry para crear entornos virtuales en el proyecto
    run_command(
        "poetry config virtualenvs.in-project true",
        "Configurando Poetry para usar .venv local"
    )
    
    # Instalar dependencias principales
    result = run_command(
        "poetry install",
        "Instalando dependencias principales"
    )
    
    if result is None:
        print("❌ Error instalando dependencias principales")
        return False
    
    # Instalar dependencias opcionales de la API si se desea
    print("\n🤔 ¿Deseas instalar también la API de Django? (y/n): ", end="")
    install_api = input().lower().startswith('y')
    
    if install_api:
        run_command(
            "poetry install --extras api",
            "Instalando dependencias de la API de Django"
        )
    
    return True


def create_launcher_scripts():
    """Crea scripts de lanzamiento modernos."""
    
    # Script para GUI
    gui_script = """#!/bin/bash
# Launcher moderno para la aplicación GUI
echo "🚀 Iniciando Gym Performance Analyzer - GUI"
echo "======================================"

# Activar entorno Poetry y ejecutar aplicación
poetry run python -m src.gui.main

echo "👋 Aplicación GUI cerrada"
read -p "Presiona Enter para continuar..."
"""
    
    # Script para Web
    web_script = """#!/bin/bash
# Launcher moderno para la aplicación Web
echo "🌐 Iniciando Gym Performance Analyzer - Web"
echo "======================================="

# Activar entorno Poetry y ejecutar Streamlit
echo "🔗 La aplicación estará disponible en: http://localhost:8501"
poetry run streamlit run src/web/main.py

echo "👋 Aplicación Web cerrada"
read -p "Presiona Enter para continuar..."
"""
    
    # Script para Windows (GUI)
    gui_script_win = """@echo off
REM Launcher moderno para la aplicación GUI (Windows)
title Gym Performance Analyzer - GUI
echo 🚀 Iniciando Gym Performance Analyzer - GUI
echo ======================================

REM Activar entorno Poetry y ejecutar aplicación
poetry run python -m src.gui.main

echo 👋 Aplicación GUI cerrada
pause
"""
    
    # Script para Windows (Web)
    web_script_win = """@echo off
REM Launcher moderno para la aplicación Web (Windows)
title Gym Performance Analyzer - Web
echo 🌐 Iniciando Gym Performance Analyzer - Web
echo =======================================

echo 🔗 La aplicación estará disponible en: http://localhost:8501
poetry run streamlit run src/web/main.py

echo 👋 Aplicación Web cerrada
pause
"""
    
    # Escribir scripts
    scripts = [
        ("run_gui_modern.sh", gui_script),
        ("run_web_modern.sh", web_script),
        ("run_gui_modern.bat", gui_script_win),
        ("run_web_modern.bat", web_script_win),
    ]
    
    for filename, content in scripts:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Hacer ejecutables en sistemas Unix
        if not filename.endswith('.bat'):
            os.chmod(filename, 0o755)
    
    print("✓ Scripts de lanzamiento modernos creados")


def main():
    """Función principal del script de configuración."""
    print("🎯 Gym Performance Analyzer - Configuración Moderna")
    print("=====================================================")
    
    # Verificar Python
    if not check_python_version():
        sys.exit(1)
    
    # Instalar Poetry
    if not install_poetry():
        sys.exit(1)
    
    # Configurar entorno
    if not setup_poetry_environment():
        sys.exit(1)
    
    # Crear launchers
    create_launcher_scripts()
    
    print("\n🎉 ¡Configuración completada exitosamente!")
    print("\n📋 Para usar la aplicación:")
    print("   🖥️  GUI: ./run_gui_modern.sh (Linux/Mac) o run_gui_modern.bat (Windows)")
    print("   🌐 Web: ./run_web_modern.sh (Linux/Mac) o run_web_modern.bat (Windows)")
    print("\n🔧 Comandos útiles:")
    print("   poetry run python -m src.gui.main  # Ejecutar GUI directamente")
    print("   poetry run streamlit run src/web/main.py  # Ejecutar web directamente")
    print("   poetry shell  # Activar entorno virtual")
    print("   poetry add <paquete>  # Agregar nueva dependencia")
    print("   poetry update  # Actualizar dependencias")


if __name__ == "__main__":
    main()