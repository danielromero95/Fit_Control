#!/usr/bin/env python3
"""
Script de Inicio Rápido - Fit_Control
=====================================

Este script facilita el inicio y demostración de la aplicación Fit_Control.
Automatiza el proceso de configuración y proporciona acceso fácil a todas 
las funcionalidades.

Características:
- Configuración automática del entorno
- Instalación de dependencias
- Inicialización de la base de datos
- Creación de datos de demostración
- Inicio del servidor backend
- Instrucciones para React Native

Uso:
    python start_fitcontrol.py

Opciones:
    --demo      : Crear datos de demostración
    --reset     : Resetear base de datos
    --mobile    : Mostrar instrucciones para React Native
    --test      : Ejecutar tests de integración
"""

import os
import sys
import subprocess
import time
import json
import webbrowser
from datetime import datetime
from typing import Dict, List, Optional

class Colors:
    """Colores para output en terminal."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_success(message: str):
    """Imprime mensaje de éxito."""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message: str):
    """Imprime mensaje de error."""
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message: str):
    """Imprime mensaje de advertencia."""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_info(message: str):
    """Imprime mensaje informativo."""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def print_header(message: str):
    """Imprime encabezado."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'═'*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{message.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'═'*80}{Colors.END}\n")

def print_section(message: str):
    """Imprime sección."""
    print(f"\n{Colors.BOLD}{Colors.PURPLE}▶ {message}{Colors.END}")
    print(f"{Colors.PURPLE}{'─'*60}{Colors.END}")

class FitControlSetup:
    """Clase para configurar y demostrar Fit_Control."""
    
    def __init__(self):
        """Inicializa el setup."""
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.backend_dir = os.path.join(self.project_root, 'workout_api')
        self.mobile_dir = os.path.join(self.project_root, 'MobileApp')
        self.venv_dir = os.path.join(self.project_root, 'fit_control_env')
        
    def check_prerequisites(self) -> bool:
        """Verifica prerrequisitos del sistema."""
        print_section("Verificando Prerrequisitos")
        
        # Verificar Python
        try:
            python_version = sys.version_info
            if python_version.major >= 3 and python_version.minor >= 8:
                print_success(f"Python {python_version.major}.{python_version.minor}.{python_version.micro} ✓")
            else:
                print_error("Se requiere Python 3.8 o superior")
                return False
        except Exception as e:
            print_error(f"Error verificando Python: {e}")
            return False
        
        # Verificar directorios del proyecto
        if os.path.exists(self.backend_dir):
            print_success("Directorio backend encontrado ✓")
        else:
            print_error("No se encontró el directorio 'workout_api'")
            return False
            
        if os.path.exists(self.mobile_dir):
            print_success("Directorio mobile encontrado ✓")
        else:
            print_warning("No se encontró el directorio 'MobileApp'")
        
        # Verificar Node.js para React Native
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print_success(f"Node.js {result.stdout.strip()} ✓")
            else:
                print_warning("Node.js no encontrado (requerido para React Native)")
        except FileNotFoundError:
            print_warning("Node.js no encontrado (requerido para React Native)")
        
        return True
    
    def setup_virtual_environment(self) -> bool:
        """Configura el entorno virtual."""
        print_section("Configurando Entorno Virtual")
        
        try:
            if not os.path.exists(self.venv_dir):
                print_info("Creando entorno virtual...")
                subprocess.run([sys.executable, '-m', 'venv', self.venv_dir], check=True)
                print_success("Entorno virtual creado")
            else:
                print_success("Entorno virtual ya existe")
            
            return True
        except Exception as e:
            print_error(f"Error configurando entorno virtual: {e}")
            return False
    
    def install_dependencies(self) -> bool:
        """Instala dependencias de Python."""
        print_section("Instalando Dependencias")
        
        try:
            # Determinar el ejecutable de pip en el venv
            if sys.platform == "win32":
                pip_exe = os.path.join(self.venv_dir, 'Scripts', 'pip')
                python_exe = os.path.join(self.venv_dir, 'Scripts', 'python')
            else:
                pip_exe = os.path.join(self.venv_dir, 'bin', 'pip')
                python_exe = os.path.join(self.venv_dir, 'bin', 'python')
            
            requirements_file = os.path.join(self.backend_dir, 'requirements.txt')
            
            if os.path.exists(requirements_file):
                print_info("Instalando dependencias de Python...")
                subprocess.run([pip_exe, 'install', '-r', requirements_file], 
                             check=True, cwd=self.backend_dir)
                print_success("Dependencias de Python instaladas")
            else:
                print_warning("No se encontró requirements.txt")
            
            return True
        except Exception as e:
            print_error(f"Error instalando dependencias: {e}")
            return False
    
    def setup_database(self, reset: bool = False) -> bool:
        """Configura la base de datos."""
        print_section("Configurando Base de Datos")
        
        try:
            # Determinar el ejecutable de python en el venv
            if sys.platform == "win32":
                python_exe = os.path.join(self.venv_dir, 'Scripts', 'python')
            else:
                python_exe = os.path.join(self.venv_dir, 'bin', 'python')
            
            if reset:
                print_info("Reseteando base de datos...")
                db_file = os.path.join(self.backend_dir, 'db.sqlite3')
                if os.path.exists(db_file):
                    os.remove(db_file)
                    print_success("Base de datos eliminada")
            
            # Ejecutar migraciones
            print_info("Ejecutando migraciones...")
            subprocess.run([python_exe, 'manage.py', 'migrate'], 
                         check=True, cwd=self.backend_dir)
            print_success("Migraciones aplicadas")
            
            # Verificar si existe superusuario
            try:
                result = subprocess.run([python_exe, 'manage.py', 'shell', '-c', 
                                       "from django.contrib.auth import get_user_model; "
                                       "User = get_user_model(); "
                                       "print('exists' if User.objects.filter(is_superuser=True).exists() else 'none')"],
                                      capture_output=True, text=True, cwd=self.backend_dir)
                
                if 'none' in result.stdout:
                    print_info("Creando superusuario...")
                    subprocess.run([python_exe, 'manage.py', 'shell', '-c',
                                  "from django.contrib.auth import get_user_model; "
                                  "User = get_user_model(); "
                                  "User.objects.create_superuser('admin', 'admin@fitcontrol.com', 'admin123')"],
                                 check=True, cwd=self.backend_dir)
                    print_success("Superusuario creado (admin/admin123)")
                else:
                    print_success("Superusuario ya existe")
            except Exception as e:
                print_warning(f"No se pudo verificar/crear superusuario: {e}")
            
            return True
        except Exception as e:
            print_error(f"Error configurando base de datos: {e}")
            return False
    
    def create_demo_data(self) -> bool:
        """Crea datos de demostración."""
        print_section("Creando Datos de Demostración")
        
        try:
            # Determinar el ejecutable de python en el venv
            if sys.platform == "win32":
                python_exe = os.path.join(self.venv_dir, 'Scripts', 'python')
            else:
                python_exe = os.path.join(self.venv_dir, 'bin', 'python')
            
            # Script para crear datos de ejemplo
            demo_script = """
from workouts.models import Exercise, WorkoutPlan, WorkoutDay, WorkoutExercise
from authentication.models import UserProfile
from django.contrib.auth import get_user_model
import json

User = get_user_model()

# Crear ejercicios de ejemplo
exercises_data = [
    {
        'name': 'Push-ups',
        'description': 'Flexiones de brazos clásicas',
        'muscle_groups': ['chest', 'shoulders', 'triceps'],
        'equipment_needed': ['bodyweight'],
        'difficulty_level': 'beginner',
        'instructions': ['Colócate en posición de plancha', 'Baja el pecho hacia el suelo', 'Empuja hacia arriba'],
        'tips': ['Mantén el core contraído', 'No arquees la espalda']
    },
    {
        'name': 'Squats',
        'description': 'Sentadillas básicas',
        'muscle_groups': ['legs', 'glutes'],
        'equipment_needed': ['bodyweight'],
        'difficulty_level': 'beginner',
        'instructions': ['Párate con pies separados', 'Baja como si te sentaras', 'Vuelve a la posición inicial'],
        'tips': ['Mantén la espalda recta', 'No dejes que las rodillas se junten']
    },
    {
        'name': 'Plank',
        'description': 'Plancha abdominal',
        'muscle_groups': ['abs', 'core'],
        'equipment_needed': ['bodyweight'],
        'difficulty_level': 'intermediate',
        'instructions': ['Posición de flexión con antebrazos', 'Mantén el cuerpo recto', 'Aguanta la posición'],
        'tips': ['Respira normalmente', 'No levantes las caderas']
    }
]

print("Creando ejercicios...")
exercises = []
for ex_data in exercises_data:
    exercise, created = Exercise.objects.get_or_create(
        name=ex_data['name'],
        defaults=ex_data
    )
    exercises.append(exercise)
    if created:
        print(f"  ✓ {exercise.name}")

# Crear plan de entrenamiento
print("Creando plan de entrenamiento...")
plan, created = WorkoutPlan.objects.get_or_create(
    name="Plan Principiante",
    defaults={
        'description': 'Plan perfecto para comenzar tu journey fitness',
        'difficulty_level': 'beginner',
        'duration_weeks': 4,
        'days_per_week': 3,
        'estimated_duration_minutes': 30,
        'tags': ['beginner', 'bodyweight', 'home'],
        'is_public': True,
        'created_by_id': 1 if User.objects.filter(id=1).exists() else User.objects.first().id
    }
)

if created:
    print(f"  ✓ {plan.name}")
    
    # Crear días de entrenamiento
    day_configs = [
        {'day_number': 1, 'name': 'Día 1 - Pecho y Core', 'exercises': [
            {'exercise': exercises[0], 'sets': 3, 'reps': 10, 'rest': 60},
            {'exercise': exercises[2], 'sets': 3, 'reps': 30, 'rest': 45}
        ]},
        {'day_number': 2, 'name': 'Día 2 - Piernas', 'exercises': [
            {'exercise': exercises[1], 'sets': 3, 'reps': 15, 'rest': 60}
        ]},
        {'day_number': 3, 'name': 'Día 3 - Full Body', 'exercises': [
            {'exercise': exercises[0], 'sets': 2, 'reps': 8, 'rest': 45},
            {'exercise': exercises[1], 'sets': 2, 'reps': 12, 'rest': 45},
            {'exercise': exercises[2], 'sets': 2, 'reps': 20, 'rest': 30}
        ]}
    ]
    
    for day_config in day_configs:
        day = WorkoutDay.objects.create(
            plan=plan,
            day_number=day_config['day_number'],
            name=day_config['name']
        )
        
        for i, ex_config in enumerate(day_config['exercises']):
            WorkoutExercise.objects.create(
                day=day,
                exercise=ex_config['exercise'],
                sets=ex_config['sets'],
                reps=ex_config['reps'],
                rest_seconds=ex_config['rest'],
                order=i + 1
            )
        
        print(f"    ✓ {day.name}")

print("\\n¡Datos de demostración creados exitosamente!")
"""
            
            print_info("Ejecutando script de datos de demostración...")
            subprocess.run([python_exe, 'manage.py', 'shell', '-c', demo_script],
                         check=True, cwd=self.backend_dir)
            print_success("Datos de demostración creados")
            
            return True
        except Exception as e:
            print_error(f"Error creando datos de demostración: {e}")
            return False
    
    def start_backend_server(self) -> bool:
        """Inicia el servidor backend."""
        print_section("Iniciando Servidor Backend")
        
        try:
            # Determinar el ejecutable de python en el venv
            if sys.platform == "win32":
                python_exe = os.path.join(self.venv_dir, 'Scripts', 'python')
            else:
                python_exe = os.path.join(self.venv_dir, 'bin', 'python')
            
            print_info("Iniciando servidor Django en puerto 8000...")
            print_info("Presiona Ctrl+C para detener el servidor")
            print_info("El admin estará disponible en: http://localhost:8000/admin/")
            print_info("Usuario: admin, Contraseña: admin123")
            print("")
            
            # Iniciar servidor
            subprocess.run([python_exe, 'manage.py', 'runserver'], cwd=self.backend_dir)
            
            return True
        except KeyboardInterrupt:
            print_success("\nServidor detenido")
            return True
        except Exception as e:
            print_error(f"Error iniciando servidor: {e}")
            return False
    
    def show_mobile_instructions(self):
        """Muestra instrucciones para React Native."""
        print_header("INSTRUCCIONES PARA REACT NATIVE")
        
        print(f"{Colors.CYAN}Para iniciar la aplicación React Native:{Colors.END}")
        print("")
        print("1. Abrir una nueva terminal")
        print("2. Navegar al directorio mobile:")
        print(f"   cd {self.mobile_dir}")
        print("")
        print("3. Instalar dependencias (primera vez):")
        print("   npm install")
        print("")
        print("4. Para Android:")
        print("   npx react-native run-android")
        print("")
        print("5. Para iOS (solo en macOS):")
        print("   npx react-native run-ios")
        print("")
        print(f"{Colors.YELLOW}Nota: Asegúrate de que el backend esté corriendo en puerto 8000{Colors.END}")
        print("")
        print(f"{Colors.GREEN}URLs importantes:{Colors.END}")
        print("  - Backend API: http://localhost:8000/api/")
        print("  - Admin Django: http://localhost:8000/admin/")
        print("  - Documentación API: http://localhost:8000/api/docs/")
        print("")
    
    def show_demo_guide(self):
        """Muestra guía de demostración."""
        print_header("GUÍA DE DEMOSTRACIÓN - FIT_CONTROL")
        
        print(f"{Colors.CYAN}🎯 Funcionalidades principales para probar:{Colors.END}")
        print("")
        print("📱 FRONTEND (React Native):")
        print("  1. Pantalla de Inicio con calendario interactivo")
        print("  2. Explorar ejercicios con filtros y búsqueda")
        print("  3. Ver planes de entrenamiento disponibles")
        print("  4. Perfil de usuario con estadísticas")
        print("  5. Navegación fluida entre pantallas")
        print("")
        print("🔧 BACKEND (Django Admin):")
        print("  1. Gestión de ejercicios y planes")
        print("  2. Análisis de rendimiento de usuarios")
        print("  3. Configuración de análisis de video")
        print("  4. Estadísticas y reportes")
        print("")
        print("🎥 ANÁLISIS DE VIDEO:")
        print("  1. Carga de videos de entrenamiento")
        print("  2. Detección automática de repeticiones")
        print("  3. Evaluación de técnica y forma")
        print("  4. Feedback personalizado")
        print("")
        print(f"{Colors.GREEN}💡 Datos de prueba incluidos:{Colors.END}")
        print("  - 3 ejercicios básicos (Push-ups, Squats, Plank)")
        print("  - Plan de entrenamiento para principiantes")
        print("  - Usuario admin configurado (admin/admin123)")
        print("")
    
    def run_integration_tests(self):
        """Ejecuta tests de integración."""
        print_section("Ejecutando Tests de Integración")
        
        try:
            test_script = os.path.join(self.project_root, 'test_integration.py')
            if os.path.exists(test_script):
                subprocess.run([sys.executable, test_script])
            else:
                print_warning("Script de tests no encontrado")
        except Exception as e:
            print_error(f"Error ejecutando tests: {e}")

def main():
    """Función principal."""
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║                              🏋️  FIT_CONTROL 🏋️                              ║")
    print("║                           SCRIPT DE INICIO RÁPIDO                           ║")
    print("║                                                                              ║")
    print("║               Aplicación de Fitness con Análisis de Video IA               ║")
    print("║                          Backend Django + React Native                      ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    
    # Parsear argumentos simples
    reset_db = '--reset' in sys.argv
    demo_data = '--demo' in sys.argv or '--reset' in sys.argv
    show_mobile = '--mobile' in sys.argv
    run_tests = '--test' in sys.argv
    
    setup = FitControlSetup()
    
    # Verificar prerrequisitos
    if not setup.check_prerequisites():
        print_error("No se cumplen los prerrequisitos")
        sys.exit(1)
    
    # Configurar entorno
    if not setup.setup_virtual_environment():
        print_error("Error configurando entorno virtual")
        sys.exit(1)
    
    if not setup.install_dependencies():
        print_error("Error instalando dependencias")
        sys.exit(1)
    
    # Configurar base de datos
    if not setup.setup_database(reset=reset_db):
        print_error("Error configurando base de datos")
        sys.exit(1)
    
    # Crear datos de demostración
    if demo_data:
        if not setup.create_demo_data():
            print_warning("No se pudieron crear datos de demostración")
    
    # Mostrar instrucciones para mobile
    if show_mobile:
        setup.show_mobile_instructions()
        return
    
    # Ejecutar tests
    if run_tests:
        setup.run_integration_tests()
        return
    
    # Mostrar guía de demostración
    setup.show_demo_guide()
    
    # Preguntar si iniciar servidor
    print(f"\n{Colors.BOLD}¿Quieres iniciar el servidor backend ahora? (y/n): {Colors.END}", end="")
    try:
        response = input().lower().strip()
        if response in ['y', 'yes', 'sí', 's', '']:
            setup.start_backend_server()
        else:
            print_info("Para iniciar el servidor manualmente:")
            print_info("  cd workout_api && python manage.py runserver")
            print_info("\nPara ver instrucciones de React Native:")
            print_info("  python start_fitcontrol.py --mobile")
    except KeyboardInterrupt:
        print_success("\n¡Hasta luego!")

if __name__ == "__main__":
    main()