#!/usr/bin/env python3
"""
🏋️ FitControl Desktop - Ejecutor Rápido
===========================================

Ejecutor simplificado para la aplicación de escritorio FitControl.
Este script verifica dependencias, configura el entorno y lanza la aplicación.

Uso:
    python run_desktop.py

Requisitos:
    - Python 3.8+
    - Entorno virtual activado (conda o venv)
    - Dependencias instaladas (ver README.md)
"""

import sys
import os
import traceback
from pathlib import Path

# Configuración de colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_banner():
    """Imprime el banner de bienvenida."""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
🏋️ ═══════════════════════════════════════════════════════════════════
   ███████╗██╗████████╗     ██████╗ ██████╗ ███╗   ██╗████████╗██████╗  ██████╗ ██╗     
   ██╔════╝██║╚══██╔══╝    ██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝██╔══██╗██╔═══██╗██║     
   █████╗  ██║   ██║       ██║     ██║   ██║██╔██╗ ██║   ██║   ██████╔╝██║   ██║██║     
   ██╔══╝  ██║   ██║       ██║     ██║   ██║██║╚██╗██║   ██║   ██╔══██╗██║   ██║██║     
   ██║     ██║   ██║       ╚██████╗╚██████╔╝██║ ╚████║   ██║   ██║  ██║╚██████╔╝███████╗
   ╚═╝     ╚═╝   ╚═╝        ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
                                                                                          
               🎯 Gym Performance Analyzer - Aplicación de Escritorio
═══════════════════════════════════════════════════════════════════{Colors.END}
"""
    print(banner)

def check_python_version():
    """Verifica que la versión de Python sea compatible."""
    if sys.version_info < (3, 8):
        print(f"{Colors.RED}❌ Error: Se requiere Python 3.8 o superior.{Colors.END}")
        print(f"   Versión actual: {sys.version}")
        print(f"   Descarga Python desde: https://www.python.org/downloads/")
        return False
    
    print(f"{Colors.GREEN}✅ Python {sys.version.split()[0]} - Compatible{Colors.END}")
    return True

def setup_project_path():
    """Configura el path del proyecto y agrega src al sys.path."""
    project_root = Path(__file__).parent.absolute()
    src_path = project_root / "src"
    
    print(f"{Colors.BLUE}📁 Directorio del proyecto: {project_root}{Colors.END}")
    
    if not src_path.exists():
        print(f"{Colors.RED}❌ Error: No se encontró el directorio 'src' en {src_path}{Colors.END}")
        print(f"   Asegúrate de ejecutar este script desde la raíz del proyecto.")
        return None, None
    
    # Agregar src al path de Python
    sys.path.insert(0, str(src_path))
    print(f"{Colors.GREEN}✅ Directorio src agregado al path{Colors.END}")
    
    return project_root, src_path

def check_dependencies():
    """Verifica que todas las dependencias críticas estén instaladas."""
    dependencies = {
        'PyQt5': 'pip install PyQt5',
        'qtawesome': 'pip install qtawesome',
        'sqlite3': 'Incluido en Python estándar',
        'pathlib': 'Incluido en Python estándar'
    }
    
    print(f"\n{Colors.YELLOW}🔍 Verificando dependencias...{Colors.END}")
    
    missing_deps = []
    
    for dep_name, install_cmd in dependencies.items():
        try:
            if dep_name == 'PyQt5':
                import PyQt5.QtWidgets
                import PyQt5.QtCore
                import PyQt5.QtGui
            elif dep_name == 'qtawesome':
                import qtawesome
            elif dep_name == 'sqlite3':
                import sqlite3
            elif dep_name == 'pathlib':
                import pathlib
            
            print(f"{Colors.GREEN}✅ {dep_name}{Colors.END}")
            
        except ImportError:
            print(f"{Colors.RED}❌ {dep_name} - {install_cmd}{Colors.END}")
            missing_deps.append((dep_name, install_cmd))
    
    if missing_deps:
        print(f"\n{Colors.RED}💡 Dependencias faltantes detectadas:{Colors.END}")
        for dep, cmd in missing_deps:
            print(f"   {Colors.YELLOW}▶ {cmd}{Colors.END}")
        print(f"\n{Colors.BLUE}🔧 Solución rápida:{Colors.END}")
        print(f"   {Colors.WHITE}pip install PyQt5 qtawesome{Colors.END}")
        return False
    
    print(f"{Colors.GREEN}🎉 Todas las dependencias están instaladas{Colors.END}")
    return True

def check_data_directory(project_root):
    """Verifica y crea el directorio de datos si es necesario."""
    data_dir = project_root / "data"
    
    if not data_dir.exists():
        print(f"{Colors.YELLOW}📂 Creando directorio de datos...{Colors.END}")
        try:
            data_dir.mkdir(exist_ok=True)
            print(f"{Colors.GREEN}✅ Directorio 'data' creado en {data_dir}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}❌ Error creando directorio data: {e}{Colors.END}")
            return False
    else:
        print(f"{Colors.GREEN}✅ Directorio de datos existe{Colors.END}")
    
    return True

def check_assets(project_root):
    """Verifica que los assets críticos existan."""
    assets_dir = project_root / "assets"
    logo_file = assets_dir / "FitControl_logo.ico"
    
    if not assets_dir.exists():
        print(f"{Colors.YELLOW}⚠️ Directorio 'assets' no encontrado{Colors.END}")
        return False
    
    if not logo_file.exists():
        print(f"{Colors.YELLOW}⚠️ Logo de la aplicación no encontrado{Colors.END}")
        print(f"   Buscado en: {logo_file}")
    else:
        print(f"{Colors.GREEN}✅ Assets de la aplicación encontrados{Colors.END}")
    
    return True

def launch_application():
    """Importa y lanza la aplicación principal."""
    try:
        print(f"\n{Colors.CYAN}🚀 Importando módulos de la aplicación...{Colors.END}")
        
        # Importar el main de la GUI
        from gui.main import main as run_app
        
        print(f"{Colors.GREEN}✅ Módulos importados correctamente{Colors.END}")
        print(f"\n{Colors.BOLD}{Colors.CYAN}🎮 Lanzando FitControl Desktop...{Colors.END}")
        print(f"{Colors.WHITE}   Presiona Ctrl+C para cerrar la aplicación{Colors.END}")
        
        # Ejecutar la aplicación
        run_app()
        
    except ImportError as e:
        print(f"{Colors.RED}❌ Error de importación: {e}{Colors.END}")
        print(f"\n{Colors.YELLOW}🔧 Posibles soluciones:{Colors.END}")
        print(f"   1. Verifica que estés en el directorio raíz del proyecto")
        print(f"   2. Activa el entorno virtual: conda activate gym_env")
        print(f"   3. Instala las dependencias: pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"{Colors.RED}❌ Error inesperado: {e}{Colors.END}")
        print(f"\n{Colors.YELLOW}📋 Detalles del error:{Colors.END}")
        traceback.print_exc()
        return False
    
    return True

def print_help():
    """Imprime información de ayuda."""
    help_text = f"""
{Colors.CYAN}📖 Ayuda - FitControl Desktop{Colors.END}

{Colors.BOLD}Uso:{Colors.END}
    python run_desktop.py

{Colors.BOLD}Requisitos previos:{Colors.END}
    1. Python 3.8 o superior
    2. Entorno virtual activado
    3. Dependencias instaladas

{Colors.BOLD}Instalación rápida:{Colors.END}
    # Crear entorno con conda
    conda env create -f environment.yml
    conda activate gym_env
    
    # O con pip
    pip install PyQt5 qtawesome opencv-python

{Colors.BOLD}Problemas comunes:{Colors.END}
    • ModuleNotFoundError → pip install <módulo>
    • Entorno no activado → conda activate gym_env
    • Directorio incorrecto → cd <ruta-del-proyecto>

{Colors.BOLD}Más información:{Colors.END}
    README.md - Guía completa de instalación
    MEJORAS_IMPLEMENTADAS.md - Changelog
"""
    print(help_text)

def main():
    """Función principal del ejecutor."""
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
        print_help()
        return
    
    print_banner()
    
    # Verificaciones previas
    print(f"{Colors.BOLD}🔍 Realizando verificaciones iniciales...{Colors.END}")
    
    if not check_python_version():
        sys.exit(1)
    
    project_root, src_path = setup_project_path()
    if not project_root:
        sys.exit(1)
    
    if not check_dependencies():
        print(f"\n{Colors.RED}💀 No se puede continuar sin las dependencias requeridas.{Colors.END}")
        print(f"   Instala las dependencias y vuelve a intentar.")
        sys.exit(1)
    
    if not check_data_directory(project_root):
        print(f"{Colors.YELLOW}⚠️ Problemas con el directorio de datos, pero continuando...{Colors.END}")
    
    check_assets(project_root)
    
    # Lanzar aplicación
    print(f"\n{Colors.GREEN}🎯 Todo listo para el lanzamiento{Colors.END}")
    
    success = launch_application()
    
    if success:
        print(f"\n{Colors.GREEN}👋 ¡Gracias por usar FitControl!{Colors.END}")
    else:
        print(f"\n{Colors.RED}💥 La aplicación se cerró con errores.{Colors.END}")
        print(f"   Revisa los mensajes anteriores para más información.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⏹️ Aplicación interrumpida por el usuario{Colors.END}")
        print(f"{Colors.WHITE}👋 ¡Hasta luego!{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}💥 Error crítico no manejado: {e}{Colors.END}")
        traceback.print_exc()
        sys.exit(1)