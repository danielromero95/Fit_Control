#!/usr/bin/env python3
"""
🏋️ FitControl - Lanzador Principal
=====================================

Script maestro para ejecutar cualquier componente de FitControl de forma fácil.
Incluye menú interactivo y verificaciones automáticas.

Uso:
    python start_fitcontrol.py
    python start_fitcontrol.py desktop
    python start_fitcontrol.py mobile
    python start_fitcontrol.py web
"""

import sys
import os
import subprocess
import platform
from pathlib import Path

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_main_banner():
    """Imprime el banner principal de FitControl."""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
🏋️ ═══════════════════════════════════════════════════════════════════════════════════════
   ███████╗██╗████████╗     ██████╗ ██████╗ ███╗   ██╗████████╗██████╗  ██████╗ ██╗     
   ██╔════╝██║╚══██╔══╝    ██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝██╔══██╗██╔═══██╗██║     
   █████╗  ██║   ██║       ██║     ██║   ██║██╔██╗ ██║   ██║   ██████╔╝██║   ██║██║     
   ██╔══╝  ██║   ██║       ██║     ██║   ██║██║╚██╗██║   ██║   ██╔══██╗██║   ██║██║     
   ██║     ██║   ██║       ╚██████╗╚██████╔╝██║ ╚████║   ██║   ██║  ██║╚██████╔╝███████╗
   ╚═╝     ╚═╝   ╚═╝        ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
                                                                                          
                        🎯 Gym Performance Analyzer - Lanzador Principal
                              📱 Móvil  |  🖥️ Desktop  |  🌐 Web
═══════════════════════════════════════════════════════════════════════════════════════{Colors.END}
"""
    print(banner)

def get_platform_info():
    """Obtiene información de la plataforma actual."""
    system = platform.system()
    machine = platform.machine()
    python_version = platform.python_version()
    
    print(f"{Colors.BLUE}📍 Información del Sistema:{Colors.END}")
    print(f"   🖥️  Sistema: {system} ({machine})")
    print(f"   🐍 Python: {python_version}")
    print(f"   📁 Directorio: {Path.cwd()}")
    print()

def check_python_compatibility():
    """Verifica que la versión de Python sea compatible."""
    if sys.version_info < (3, 8):
        print(f"{Colors.RED}❌ Python 3.8+ requerido. Versión actual: {sys.version}{Colors.END}")
        return False
    print(f"{Colors.GREEN}✅ Python {sys.version.split()[0]} - Compatible{Colors.END}")
    return True

def check_project_structure():
    """Verifica que la estructura del proyecto sea correcta."""
    required_dirs = ['src', 'MobileApp']
    required_files = ['environment.yml', 'README.md']
    
    print(f"{Colors.YELLOW}🔍 Verificando estructura del proyecto...{Colors.END}")
    
    all_good = True
    
    for directory in required_dirs:
        if Path(directory).exists():
            print(f"{Colors.GREEN}✅ {directory}/ encontrado{Colors.END}")
        else:
            print(f"{Colors.RED}❌ {directory}/ faltante{Colors.END}")
            all_good = False
    
    for file in required_files:
        if Path(file).exists():
            print(f"{Colors.GREEN}✅ {file} encontrado{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️ {file} faltante (no crítico){Colors.END}")
    
    return all_good

def show_applications_menu():
    """Muestra el menú de aplicaciones disponibles."""
    print(f"\n{Colors.CYAN}{Colors.BOLD}🚀 Aplicaciones Disponibles:{Colors.END}")
    print()
    
    apps = [
        {
            'number': '1',
            'name': '🖥️ Aplicación de Escritorio',
            'description': 'Interfaz completa con PyQt - Análisis de vídeo y dashboard',
            'command': 'desktop',
            'status': '✅ Listo'
        },
        {
            'number': '2', 
            'name': '📱 Aplicación Móvil',
            'description': 'App React Native - Dashboard y biblioteca de ejercicios',
            'command': 'mobile',
            'status': '✅ Listo'
        },
        {
            'number': '3',
            'name': '🌐 Aplicación Web',
            'description': 'Interfaz Streamlit - Análisis de vídeo básico',
            'command': 'web',
            'status': '✅ Listo'
        },
        {
            'number': '4',
            'name': '🔧 Verificar Dependencias',
            'description': 'Comprobar estado de instalación y dependencias',
            'command': 'check',
            'status': '🔍 Verificar'
        }
    ]
    
    for app in apps:
        print(f"  {Colors.WHITE}{app['number']}.{Colors.END} {Colors.BOLD}{app['name']}{Colors.END}")
        print(f"     {app['description']}")
        print(f"     Estado: {app['status']}")
        print()
    
    print(f"  {Colors.WHITE}q.{Colors.END} {Colors.BOLD}Salir{Colors.END}")
    print()

def run_desktop_app():
    """Ejecuta la aplicación de escritorio."""
    print(f"{Colors.CYAN}🖥️ Iniciando aplicación de escritorio...{Colors.END}")
    
    script_path = Path("run_desktop.py")
    
    if script_path.exists():
        print(f"   Ejecutando: python {script_path}")
        try:
            subprocess.run([sys.executable, str(script_path)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}❌ Error ejecutando aplicación desktop: {e}{Colors.END}")
            return False
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⏹️ Aplicación desktop interrumpida{Colors.END}")
    else:
        print(f"{Colors.YELLOW}⚠️ run_desktop.py no encontrado, ejecutando directamente...{Colors.END}")
        try:
            # Agregar src al path
            src_path = Path("src")
            if src_path.exists():
                sys.path.insert(0, str(src_path))
                from gui.main import main as run_app
                run_app()
            else:
                print(f"{Colors.RED}❌ Directorio src/ no encontrado{Colors.END}")
                return False
        except ImportError as e:
            print(f"{Colors.RED}❌ Error importando aplicación: {e}{Colors.END}")
            print(f"   Instala dependencias: pip install PyQt5 qtawesome")
            return False
        except Exception as e:
            print(f"{Colors.RED}❌ Error inesperado: {e}{Colors.END}")
            return False
    
    return True

def run_mobile_app():
    """Ejecuta la aplicación móvil."""
    print(f"{Colors.CYAN}📱 Iniciando aplicación móvil...{Colors.END}")
    
    mobile_dir = Path("MobileApp")
    
    if not mobile_dir.exists():
        print(f"{Colors.RED}❌ Directorio MobileApp no encontrado{Colors.END}")
        return False
    
    # Verificar si existe el script bash
    bash_script = Path("run_mobile.sh")
    if bash_script.exists() and platform.system() != "Windows":
        print("   Ejecutando con script bash...")
        try:
            subprocess.run(["bash", str(bash_script)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}❌ Error ejecutando script bash: {e}{Colors.END}")
            return False
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⏹️ Aplicación móvil interrumpida{Colors.END}")
    else:
        # Ejecutar directamente con npm/expo
        print("   Verificando Node.js...")
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                node_version = result.stdout.strip()
                print(f"   ✅ Node.js {node_version}")
            else:
                print(f"{Colors.RED}❌ Node.js no encontrado{Colors.END}")
                print("   Instala Node.js desde: https://nodejs.org/")
                return False
        except FileNotFoundError:
            print(f"{Colors.RED}❌ Node.js no encontrado{Colors.END}")
            print("   Instala Node.js desde: https://nodejs.org/")
            return False
        
        print(f"   Cambiando a directorio: {mobile_dir}")
        try:
            os.chdir(mobile_dir)
            
            # Verificar si node_modules existe
            if not Path("node_modules").exists():
                print("   📦 Instalando dependencias...")
                subprocess.run(["npm", "install"], check=True)
            
            print("   🚀 Iniciando Expo...")
            print(f"\n{Colors.WHITE}📋 Instrucciones:{Colors.END}")
            print("   1. Instala 'Expo Go' en tu móvil")
            print("   2. Escanea el código QR que aparecerá")
            print("   3. Presiona Ctrl+C para detener")
            print()
            
            subprocess.run(["npx", "expo", "start"], check=True)
            
        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}❌ Error ejecutando aplicación móvil: {e}{Colors.END}")
            return False
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⏹️ Aplicación móvil interrumpida{Colors.END}")
        finally:
            # Volver al directorio raíz
            os.chdir("..")
    
    return True

def run_web_app():
    """Ejecuta la aplicación web."""
    print(f"{Colors.CYAN}🌐 Iniciando aplicación web...{Colors.END}")
    
    # Verificar que src existe
    src_dir = Path("src")
    if not src_dir.exists():
        print(f"{Colors.RED}❌ Directorio src/ no encontrado{Colors.END}")
        return False
    
    # Buscar archivos de Streamlit
    streamlit_files = [
        src_dir / "enhanced_app.py",
        src_dir / "app.py"
    ]
    
    target_file = None
    for file in streamlit_files:
        if file.exists():
            target_file = file
            break
    
    if not target_file:
        print(f"{Colors.RED}❌ No se encontraron archivos de Streamlit{Colors.END}")
        return False
    
    print(f"   Ejecutando: streamlit run {target_file}")
    print(f"\n{Colors.WHITE}📋 La aplicación se abrirá automáticamente en tu navegador{Colors.END}")
    print(f"   URL: http://localhost:8501")
    print(f"   Presiona Ctrl+C para detener")
    print()
    
    try:
        subprocess.run(["streamlit", "run", str(target_file)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}❌ Error ejecutando Streamlit: {e}{Colors.END}")
        print("   Instala Streamlit: pip install streamlit")
        return False
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⏹️ Aplicación web interrumpida{Colors.END}")
    except FileNotFoundError:
        print(f"{Colors.RED}❌ Streamlit no encontrado{Colors.END}")
        print("   Instala Streamlit: pip install streamlit")
        return False
    
    return True

def run_dependency_check():
    """Ejecuta verificación de dependencias."""
    print(f"{Colors.CYAN}🔧 Verificando dependencias...{Colors.END}")
    print()
    
    # Verificar Python
    if not check_python_compatibility():
        return False
    
    # Verificar estructura
    if not check_project_structure():
        print(f"{Colors.RED}⚠️ Problemas con la estructura del proyecto{Colors.END}")
    
    # Verificar dependencias Python
    print(f"\n{Colors.YELLOW}🐍 Verificando dependencias Python...{Colors.END}")
    python_deps = ['PyQt5', 'qtawesome', 'streamlit', 'opencv-python', 'sqlite3']
    
    for dep in python_deps:
        try:
            if dep == 'opencv-python':
                import cv2
                print(f"{Colors.GREEN}✅ {dep} (OpenCV){Colors.END}")
            else:
                __import__(dep.replace('-', '_'))
                print(f"{Colors.GREEN}✅ {dep}{Colors.END}")
        except ImportError:
            print(f"{Colors.RED}❌ {dep} - pip install {dep}{Colors.END}")
    
    # Verificar Node.js para móvil
    print(f"\n{Colors.YELLOW}📱 Verificando entorno móvil...{Colors.END}")
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"{Colors.GREEN}✅ Node.js {result.stdout.strip()}{Colors.END}")
        else:
            print(f"{Colors.RED}❌ Node.js no encontrado{Colors.END}")
    except FileNotFoundError:
        print(f"{Colors.RED}❌ Node.js no encontrado{Colors.END}")
    
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"{Colors.GREEN}✅ npm {result.stdout.strip()}{Colors.END}")
        else:
            print(f"{Colors.RED}❌ npm no encontrado{Colors.END}")
    except FileNotFoundError:
        print(f"{Colors.RED}❌ npm no encontrado{Colors.END}")
    
    print(f"\n{Colors.GREEN}🎉 Verificación completada{Colors.END}")
    return True

def interactive_menu():
    """Muestra el menú interactivo principal."""
    while True:
        print_main_banner()
        get_platform_info()
        show_applications_menu()
        
        try:
            choice = input(f"{Colors.CYAN}👉 Selecciona una opción (1-4, q para salir): {Colors.END}").strip().lower()
            
            if choice == 'q' or choice == 'quit' or choice == 'exit':
                print(f"{Colors.WHITE}👋 ¡Hasta luego!{Colors.END}")
                break
            elif choice == '1' or choice == 'desktop':
                run_desktop_app()
            elif choice == '2' or choice == 'mobile':
                run_mobile_app()
            elif choice == '3' or choice == 'web':
                run_web_app()
            elif choice == '4' or choice == 'check':
                run_dependency_check()
            else:
                print(f"{Colors.RED}❌ Opción no válida: {choice}{Colors.END}")
            
            if choice in ['1', '2', '3', '4', 'desktop', 'mobile', 'web', 'check']:
                input(f"\n{Colors.CYAN}Presiona Enter para volver al menú principal...{Colors.END}")
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}👋 ¡Hasta luego!{Colors.END}")
            break
        except EOFError:
            print(f"\n{Colors.YELLOW}👋 ¡Hasta luego!{Colors.END}")
            break

def main():
    """Función principal."""
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        print_main_banner()
        get_platform_info()
        
        if command == 'desktop':
            run_desktop_app()
        elif command == 'mobile':
            run_mobile_app()
        elif command == 'web':
            run_web_app()
        elif command == 'check':
            run_dependency_check()
        elif command in ['help', '-h', '--help']:
            print(f"{Colors.CYAN}📖 Ayuda - FitControl Lanzador{Colors.END}")
            print()
            print(f"{Colors.BOLD}Uso:{Colors.END}")
            print("    python start_fitcontrol.py [comando]")
            print()
            print(f"{Colors.BOLD}Comandos disponibles:{Colors.END}")
            print("    desktop  - Ejecutar aplicación de escritorio")
            print("    mobile   - Ejecutar aplicación móvil")
            print("    web      - Ejecutar aplicación web")
            print("    check    - Verificar dependencias")
            print("    help     - Mostrar esta ayuda")
            print()
            print(f"{Colors.BOLD}Sin argumentos:{Colors.END}")
            print("    Ejecuta el menú interactivo")
        else:
            print(f"{Colors.RED}❌ Comando no reconocido: {command}{Colors.END}")
            print("   Usa 'python start_fitcontrol.py help' para ver comandos disponibles")
    else:
        # Menú interactivo
        interactive_menu()

if __name__ == "__main__":
    main()