#!/usr/bin/env python3
"""
Script de emergencia para resolver problemas críticos de dependencias.
Usa solo pip y Python estándar. Úsalo cuando Poetry y conda fallen.
"""

import os
import sys
import subprocess
import platform

def print_banner():
    print("🚨" + "="*50 + "🚨")
    print("   SCRIPT DE EMERGENCIA - GYM ANALYZER")
    print("🚨" + "="*50 + "🚨")
    print("\nEste script resuelve problemas críticos cuando:")
    print("❌ Conda está corrupto")
    print("❌ Poetry no funciona") 
    print("❌ Hay conflictos de dependencias")
    print("\n⚠️  Solo usa pip y Python estándar")


def run_pip_command(package, description=""):
    """Instala un paquete con pip de forma segura."""
    if description:
        print(f"📦 {description}...")
    
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade", package]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"   ✅ {package} instalado correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error instalando {package}: {e}")
        if e.stderr:
            print(f"      Detalles: {e.stderr.strip()}")
        return False


def fix_critical_dependencies():
    """Instala las dependencias más críticas una por una."""
    print("\n🔧 Instalando dependencias críticas...")
    
    # Lista de paquetes críticos en orden de prioridad
    critical_packages = [
        ("pip", "Actualizando pip"),
        ("setuptools", "Actualizando setuptools"),
        ("wheel", "Instalando wheel"),
        ("PyYAML", "YAML parser (CRÍTICO para config.yaml)"),
        ("numpy", "Librería matemática base"),
        ("opencv-python", "Computer Vision"),
        ("PyQt5", "Interfaz gráfica"),
        ("matplotlib", "Gráficos"),
        ("streamlit", "Interfaz web"),
        ("mediapipe", "IA para pose estimation"),
        ("pandas", "Manipulación de datos"),
        ("requests", "HTTP requests"),
        ("scipy", "Algoritmos científicos"),
        ("pydantic<2", "Validación de datos"),
        ("plotly", "Gráficos interactivos"),
        ("pyqtgraph", "Gráficos Qt"),
        ("qtawesome", "Iconos Qt"),
        ("moviepy", "Procesamiento de video"),
    ]
    
    success_count = 0
    total_packages = len(critical_packages)
    
    for package, description in critical_packages:
        if run_pip_command(package, description):
            success_count += 1
        else:
            print(f"   ⚠️  Continuando sin {package}...")
    
    print(f"\n📊 Resultado: {success_count}/{total_packages} paquetes instalados correctamente")
    
    if success_count >= total_packages - 2:  # Permitir 2 fallos
        print("✅ Suficientes dependencias instaladas para funcionar")
        return True
    else:
        print("❌ Demasiados fallos. Puede que el entorno necesite reinstalación")
        return False


def test_imports():
    """Prueba importar las dependencias críticas."""
    print("\n🧪 Probando imports críticos...")
    
    tests = [
        ("yaml", "PyYAML"),
        ("cv2", "OpenCV"),
        ("numpy", "NumPy"),
        ("PyQt5", "PyQt5"),
        ("matplotlib", "Matplotlib"),
        ("streamlit", "Streamlit"),
    ]
    
    working = []
    failing = []
    
    for module_name, display_name in tests:
        try:
            __import__(module_name)
            print(f"   ✅ {display_name} OK")
            working.append(display_name)
        except ImportError as e:
            print(f"   ❌ {display_name} FALLA: {e}")
            failing.append(display_name)
    
    print(f"\n📊 Resultado de imports:")
    print(f"   ✅ Funcionando: {len(working)}/{len(tests)}")
    print(f"   ❌ Fallando: {len(failing)}/{len(tests)}")
    
    if len(working) >= 4:  # Necesitamos al menos yaml, cv2, numpy, PyQt5
        print("✅ Suficientes dependencias funcionando")
        return True
    else:
        print("❌ Faltan dependencias críticas")
        return False


def create_emergency_launchers():
    """Crea launchers de emergencia que usan Python directamente."""
    print("\n🚀 Creando launchers de emergencia...")
    
    # Launcher GUI emergencia
    gui_emergency = f"""@echo off
title Gym Analyzer - GUI (EMERGENCIA)
echo 🚨 Gym Performance Analyzer - GUI (Modo Emergencia)
echo ====================================================
echo.

echo 🔍 Verificando Python...
python --version
if %ERRORLEVEL% neq 0 (
    echo ❌ Python no encontrado
    pause
    exit /b 1
)

echo 🔍 Verificando dependencias criticas...
python -c "import yaml, cv2, numpy, PyQt5" 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ Dependencias criticas faltantes
    echo 📋 Ejecuta: python fix_emergencia.py
    pause
    exit /b 1
)

echo ✅ Dependencias verificadas
echo 🚀 Iniciando aplicacion GUI...

cd /d "%~dp0"
set PYTHONPATH=%CD%;%PYTHONPATH%
python -m src.gui.main

echo.
echo 👋 Aplicacion cerrada
pause
"""

    # Launcher Web emergencia  
    web_emergency = f"""@echo off
title Gym Analyzer - Web (EMERGENCIA)
echo 🚨 Gym Performance Analyzer - Web (Modo Emergencia)
echo ===================================================
echo.

echo 🔍 Verificando Python...
python --version
if %ERRORLEVEL% neq 0 (
    echo ❌ Python no encontrado
    pause
    exit /b 1
)

echo 🔍 Verificando dependencias criticas...
python -c "import yaml, cv2, numpy, streamlit" 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ Dependencias criticas faltantes
    echo 📋 Ejecuta: python fix_emergencia.py
    pause
    exit /b 1
)

echo ✅ Dependencias verificadas
echo 🌐 Iniciando aplicacion web...
echo 🔗 Disponible en: http://localhost:8501

cd /d "%~dp0"
set PYTHONPATH=%CD%;%PYTHONPATH%
streamlit run src/enhanced_app.py

echo.
echo 👋 Aplicacion cerrada
pause
"""

    # Crear archivos
    try:
        with open("run_gui_emergencia.bat", "w", encoding="utf-8") as f:
            f.write(gui_emergency)
        print("   ✅ run_gui_emergencia.bat creado")
        
        with open("run_web_emergencia.bat", "w", encoding="utf-8") as f:
            f.write(web_emergency)
        print("   ✅ run_web_emergencia.bat creado")
        
        return True
    except Exception as e:
        print(f"   ❌ Error creando launchers: {e}")
        return False


def create_simple_requirements():
    """Crea un requirements.txt super simple para emergencias."""
    simple_reqs = """# Requirements mínimos para emergencias
PyYAML
numpy
opencv-python  
PyQt5
matplotlib
streamlit
mediapipe
pandas
requests
"""
    
    try:
        with open("requirements_emergencia.txt", "w", encoding="utf-8") as f:
            f.write(simple_reqs)
        print("   ✅ requirements_emergencia.txt creado")
        return True
    except Exception as e:
        print(f"   ❌ Error creando requirements: {e}")
        return False


def main():
    """Función principal del script de emergencia."""
    print_banner()
    
    print("\n❓ ¿Qué quieres hacer?")
    print("1. 🔧 Arreglar dependencias (recomendado)")
    print("2. 🧪 Solo probar imports actuales")
    print("3. 🚀 Solo crear launchers de emergencia")
    print("4. 📋 Todo lo anterior")
    
    try:
        choice = input("\nSelecciona opción (1-4): ").strip()
    except KeyboardInterrupt:
        print("\n👋 Cancelado por el usuario")
        return
    
    success = True
    
    if choice in ["1", "4"]:
        success &= fix_critical_dependencies()
        create_simple_requirements()
    
    if choice in ["2", "4"]:
        success &= test_imports()
    
    if choice in ["3", "4"]:
        success &= create_emergency_launchers()
    
    print("\n" + "="*60)
    if success:
        print("🎉 ¡Script de emergencia completado!")
        print("\n📋 Próximos pasos:")
        print("   1. Prueba run_gui_emergencia.bat para la GUI")
        print("   2. Prueba run_web_emergencia.bat para la web")
        print("   3. Si sigues teniendo problemas, considera reinstalar Python")
    else:
        print("⚠️ El script terminó con algunos errores")
        print("\n📋 Opciones:")
        print("   1. Ejecuta este script nuevamente")
        print("   2. Reinstala Python desde python.org")
        print("   3. Usa un entorno virtual limpio")
    
    input("\nPresiona Enter para salir...")


if __name__ == "__main__":
    main()