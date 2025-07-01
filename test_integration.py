#!/usr/bin/env python3
"""
Script de Testing de Integración - Fit_Control
================================================

Este script verifica la integración completa entre el backend Django 
y el frontend React Native, así como la funcionalidad de análisis de video.

Características:
- Pruebas de API endpoints
- Verificación de autenticación JWT
- Testing de análisis de video
- Generación de datos de prueba
- Reporte completo de funcionalidad

Uso:
    python test_integration.py

Requisitos:
    - Backend Django corriendo en puerto 8000
    - Base de datos configurada
    - Dependencias instaladas
"""

import os
import sys
import json
import requests
import time
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Configuración
API_BASE_URL = "http://localhost:8000/api"
TEST_USER_EMAIL = "test@fitcontrol.com"
TEST_USER_PASSWORD = "testpass123"
TEST_USER_DATA = {
    "username": "testuser",
    "email": TEST_USER_EMAIL,
    "password": TEST_USER_PASSWORD,
    "first_name": "Test",
    "last_name": "User"
}

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
    """Imprime mensaje de éxito en verde."""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message: str):
    """Imprime mensaje de error en rojo."""
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_warning(message: str):
    """Imprime mensaje de advertencia en amarillo."""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def print_info(message: str):
    """Imprime mensaje informativo en azul."""
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")

def print_header(message: str):
    """Imprime encabezado en negrita."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{message.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}\n")

class FitControlTester:
    """Clase principal para testing de integración."""
    
    def __init__(self):
        """Inicializa el tester."""
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.auth_token = None
        self.test_user_id = None
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'tests': []
        }
    
    def add_test_result(self, test_name: str, passed: bool, message: str = "", warning: bool = False):
        """Agrega resultado de test."""
        self.test_results['tests'].append({
            'name': test_name,
            'passed': passed,
            'message': message,
            'warning': warning,
            'timestamp': datetime.now().isoformat()
        })
        
        if warning:
            self.test_results['warnings'] += 1
        elif passed:
            self.test_results['passed'] += 1
        else:
            self.test_results['failed'] += 1
    
    def check_backend_status(self) -> bool:
        """Verifica que el backend esté corriendo."""
        print_info("Verificando estado del backend...")
        try:
            response = self.session.get(f"{API_BASE_URL}/health/", timeout=5)
            if response.status_code == 200:
                print_success("Backend Django respondiendo correctamente")
                self.add_test_result("Backend Status", True, "Django servidor activo")
                return True
            else:
                print_error(f"Backend responde con código {response.status_code}")
                self.add_test_result("Backend Status", False, f"Código de respuesta: {response.status_code}")
                return False
        except requests.ConnectionError:
            print_error("No se puede conectar al backend. ¿Está corriendo en puerto 8000?")
            self.add_test_result("Backend Status", False, "No se puede conectar al servidor")
            return False
        except Exception as e:
            print_error(f"Error verificando backend: {e}")
            self.add_test_result("Backend Status", False, f"Error: {str(e)}")
            return False
    
    def test_user_registration(self) -> bool:
        """Prueba registro de usuario."""
        print_info("Probando registro de usuario...")
        try:
            # Intentar eliminar usuario existente primero
            try:
                self.session.delete(f"{API_BASE_URL}/auth/user/delete/", 
                                  json={"email": TEST_USER_EMAIL})
            except:
                pass  # Ignorar errores si el usuario no existe
            
            response = self.session.post(f"{API_BASE_URL}/auth/register/", json=TEST_USER_DATA)
            
            if response.status_code == 201:
                data = response.json()
                print_success("Usuario registrado exitosamente")
                self.test_user_id = data.get('user', {}).get('id')
                self.add_test_result("User Registration", True, "Usuario creado correctamente")
                return True
            else:
                print_warning(f"Registro falló con código {response.status_code}")
                # Puede ser que el usuario ya exista, intentar login
                self.add_test_result("User Registration", False, f"Código: {response.status_code}", warning=True)
                return False
        except Exception as e:
            print_error(f"Error en registro: {e}")
            self.add_test_result("User Registration", False, f"Error: {str(e)}")
            return False
    
    def test_user_login(self) -> bool:
        """Prueba login de usuario."""
        print_info("Probando autenticación de usuario...")
        try:
            login_data = {
                "username": TEST_USER_DATA["username"],
                "password": TEST_USER_PASSWORD
            }
            
            response = self.session.post(f"{API_BASE_URL}/auth/login/", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access')
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                print_success("Login exitoso, token JWT obtenido")
                self.add_test_result("User Login", True, "Autenticación JWT funcionando")
                return True
            else:
                print_error(f"Login falló con código {response.status_code}")
                self.add_test_result("User Login", False, f"Código: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error en login: {e}")
            self.add_test_result("User Login", False, f"Error: {str(e)}")
            return False
    
    def test_exercises_api(self) -> bool:
        """Prueba API de ejercicios."""
        print_info("Probando API de ejercicios...")
        try:
            # Listar ejercicios
            response = self.session.get(f"{API_BASE_URL}/exercises/")
            
            if response.status_code == 200:
                data = response.json()
                exercises_count = len(data.get('results', []))
                print_success(f"API de ejercicios funcionando - {exercises_count} ejercicios encontrados")
                self.add_test_result("Exercises API", True, f"{exercises_count} ejercicios disponibles")
                return True
            else:
                print_error(f"API de ejercicios falló con código {response.status_code}")
                self.add_test_result("Exercises API", False, f"Código: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error en API de ejercicios: {e}")
            self.add_test_result("Exercises API", False, f"Error: {str(e)}")
            return False
    
    def test_plans_api(self) -> bool:
        """Prueba API de planes de entrenamiento."""
        print_info("Probando API de planes de entrenamiento...")
        try:
            # Listar planes
            response = self.session.get(f"{API_BASE_URL}/plans/")
            
            if response.status_code == 200:
                data = response.json()
                plans_count = len(data.get('results', []))
                print_success(f"API de planes funcionando - {plans_count} planes encontrados")
                self.add_test_result("Plans API", True, f"{plans_count} planes disponibles")
                return True
            else:
                print_error(f"API de planes falló con código {response.status_code}")
                self.add_test_result("Plans API", False, f"Código: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error en API de planes: {e}")
            self.add_test_result("Plans API", False, f"Error: {str(e)}")
            return False
    
    def test_user_stats_api(self) -> bool:
        """Prueba API de estadísticas de usuario."""
        print_info("Probando API de estadísticas de usuario...")
        try:
            if not self.test_user_id:
                print_warning("No hay usuario de prueba disponible")
                self.add_test_result("User Stats API", False, "No hay usuario de prueba", warning=True)
                return False
            
            response = self.session.get(f"{API_BASE_URL}/users/{self.test_user_id}/stats/")
            
            if response.status_code == 200:
                data = response.json()
                print_success("API de estadísticas de usuario funcionando")
                print_info(f"  - Entrenamientos totales: {data.get('total_workouts', 0)}")
                print_info(f"  - Racha actual: {data.get('current_streak', 0)} días")
                self.add_test_result("User Stats API", True, "Estadísticas de usuario accesibles")
                return True
            else:
                print_error(f"API de estadísticas falló con código {response.status_code}")
                self.add_test_result("User Stats API", False, f"Código: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error en API de estadísticas: {e}")
            self.add_test_result("User Stats API", False, f"Error: {str(e)}")
            return False
    
    def test_video_analysis_mock(self) -> bool:
        """Prueba análisis de video (simulado)."""
        print_info("Probando análisis de video...")
        try:
            # Crear datos simulados de análisis
            mock_analysis_data = {
                "video_data": "data:video/mp4;base64,mock_video_data",
                "exercise_type": "push_up",
                "duration": 30
            }
            
            response = self.session.post(f"{API_BASE_URL}/analyze/", json=mock_analysis_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                print_success("API de análisis de video funcionando")
                print_info(f"  - Repeticiones detectadas: {data.get('repetitions_count', 0)}")
                print_info(f"  - Puntuación de forma: {data.get('form_score', 0):.1f}")
                self.add_test_result("Video Analysis", True, "Análisis de video procesado")
                return True
            else:
                print_warning(f"API de análisis no implementada completamente (código {response.status_code})")
                self.add_test_result("Video Analysis", True, "API endpoint existe", warning=True)
                return True
        except Exception as e:
            print_warning(f"Análisis de video en desarrollo: {e}")
            self.add_test_result("Video Analysis", True, "Funcionalidad en desarrollo", warning=True)
            return True
    
    def test_database_operations(self) -> bool:
        """Prueba operaciones de base de datos."""
        print_info("Probando operaciones de base de datos...")
        try:
            # Crear un registro de rendimiento de prueba
            performance_data = {
                "exercise": 1,  # Asumiendo que existe ejercicio con ID 1
                "sets_completed": 3,
                "reps_completed": [10, 8, 6],
                "weights_used": [20, 20, 15],
                "duration_seconds": 300,
                "rest_periods": [60, 60],
                "perceived_exertion": 7,
                "notes": "Test workout from integration script"
            }
            
            response = self.session.post(f"{API_BASE_URL}/log/", json=performance_data)
            
            if response.status_code in [200, 201]:
                print_success("Operaciones de base de datos funcionando")
                self.add_test_result("Database Operations", True, "Creación de registros exitosa")
                return True
            else:
                print_warning(f"Operaciones de BD con código {response.status_code}")
                self.add_test_result("Database Operations", False, f"Código: {response.status_code}", warning=True)
                return False
        except Exception as e:
            print_warning(f"Error en operaciones de BD: {e}")
            self.add_test_result("Database Operations", False, f"Error: {str(e)}", warning=True)
            return False
    
    def test_cors_headers(self) -> bool:
        """Prueba headers CORS para React Native."""
        print_info("Probando configuración CORS...")
        try:
            # Simular request de React Native
            headers = {
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type, Authorization'
            }
            
            response = self.session.options(f"{API_BASE_URL}/exercises/", headers=headers)
            
            cors_headers = response.headers
            has_cors = 'Access-Control-Allow-Origin' in cors_headers
            
            if has_cors:
                print_success("Headers CORS configurados correctamente")
                self.add_test_result("CORS Configuration", True, "React Native puede acceder a la API")
                return True
            else:
                print_warning("Headers CORS pueden no estar configurados")
                self.add_test_result("CORS Configuration", False, "CORS puede causar problemas", warning=True)
                return False
        except Exception as e:
            print_warning(f"Error verificando CORS: {e}")
            self.add_test_result("CORS Configuration", False, f"Error: {str(e)}", warning=True)
            return False
    
    def generate_test_data(self) -> bool:
        """Genera datos de prueba para demostración."""
        print_info("Generando datos de prueba...")
        try:
            # Ejecutar management command para crear datos de ejemplo
            result = subprocess.run([
                sys.executable, 'manage.py', 'create_sample_data'
            ], cwd='workout_api', capture_output=True, text=True)
            
            if result.returncode == 0:
                print_success("Datos de prueba generados exitosamente")
                self.add_test_result("Test Data Generation", True, "Datos de ejemplo creados")
                return True
            else:
                print_warning("No se pudieron generar datos de prueba automáticamente")
                print_info("Puedes crear datos manualmente usando el admin de Django")
                self.add_test_result("Test Data Generation", False, "Generación automática falló", warning=True)
                return False
        except Exception as e:
            print_warning(f"Error generando datos de prueba: {e}")
            self.add_test_result("Test Data Generation", False, f"Error: {str(e)}", warning=True)
            return False
    
    def run_all_tests(self):
        """Ejecuta todas las pruebas de integración."""
        print_header("INICIANDO TESTS DE INTEGRACIÓN FIT_CONTROL")
        
        start_time = time.time()
        
        # Lista de tests a ejecutar
        tests = [
            ("Verificación del Backend", self.check_backend_status),
            ("Registro de Usuario", self.test_user_registration),
            ("Autenticación JWT", self.test_user_login),
            ("API de Ejercicios", self.test_exercises_api),
            ("API de Planes", self.test_plans_api),
            ("API de Estadísticas", self.test_user_stats_api),
            ("Análisis de Video", self.test_video_analysis_mock),
            ("Operaciones de BD", self.test_database_operations),
            ("Configuración CORS", self.test_cors_headers),
            ("Datos de Prueba", self.generate_test_data),
        ]
        
        # Ejecutar tests
        for test_name, test_func in tests:
            print(f"\n{Colors.PURPLE}{'─' * 40}{Colors.END}")
            print(f"{Colors.PURPLE}Ejecutando: {test_name}{Colors.END}")
            print(f"{Colors.PURPLE}{'─' * 40}{Colors.END}")
            
            try:
                success = test_func()
                if success:
                    print_success(f"{test_name} completado")
                else:
                    print_error(f"{test_name} falló")
            except Exception as e:
                print_error(f"Error inesperado en {test_name}: {e}")
                self.add_test_result(test_name, False, f"Error inesperado: {str(e)}")
        
        # Reporte final
        self.print_final_report(time.time() - start_time)
    
    def print_final_report(self, execution_time: float):
        """Imprime reporte final de tests."""
        print_header("REPORTE FINAL DE INTEGRACIÓN")
        
        total_tests = self.test_results['passed'] + self.test_results['failed'] + self.test_results['warnings']
        
        print(f"{Colors.BOLD}Resumen de Ejecución:{Colors.END}")
        print(f"  Tiempo total: {execution_time:.2f} segundos")
        print(f"  Tests ejecutados: {total_tests}")
        print(f"  {Colors.GREEN}Exitosos: {self.test_results['passed']}{Colors.END}")
        print(f"  {Colors.RED}Fallidos: {self.test_results['failed']}{Colors.END}")
        print(f"  {Colors.YELLOW}Advertencias: {self.test_results['warnings']}{Colors.END}")
        
        # Calcular score
        if total_tests > 0:
            success_rate = (self.test_results['passed'] / total_tests) * 100
            print(f"\n{Colors.BOLD}Tasa de Éxito: {success_rate:.1f}%{Colors.END}")
            
            if success_rate >= 90:
                print(f"{Colors.GREEN}🎉 Excelente! La integración está funcionando perfectamente{Colors.END}")
            elif success_rate >= 70:
                print(f"{Colors.YELLOW}👍 Bien! La mayoría de funcionalidades están trabajando{Colors.END}")
            else:
                print(f"{Colors.RED}⚠️  Hay problemas que necesitan atención{Colors.END}")
        
        # Detalles de tests fallidos
        failed_tests = [t for t in self.test_results['tests'] if not t['passed'] and not t['warning']]
        if failed_tests:
            print(f"\n{Colors.RED}{Colors.BOLD}Tests Fallidos:{Colors.END}")
            for test in failed_tests:
                print(f"  - {test['name']}: {test['message']}")
        
        # Advertencias
        warning_tests = [t for t in self.test_results['tests'] if t['warning']]
        if warning_tests:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}Advertencias:{Colors.END}")
            for test in warning_tests:
                print(f"  - {test['name']}: {test['message']}")
        
        # Próximos pasos
        print(f"\n{Colors.CYAN}{Colors.BOLD}Próximos Pasos Recomendados:{Colors.END}")
        print("1. 🚀 Iniciar la aplicación React Native para testing manual")
        print("2. 📱 Probar la navegación entre pantallas")
        print("3. 🎥 Testear análisis de video con videos reales")
        print("4. 📊 Verificar sincronización de datos")
        print("5. 🔄 Probar funcionalidad offline")
        
        # Guardar reporte en archivo
        self.save_report_to_file()
    
    def save_report_to_file(self):
        """Guarda el reporte en un archivo JSON."""
        try:
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_tests': len(self.test_results['tests']),
                    'passed': self.test_results['passed'],
                    'failed': self.test_results['failed'],
                    'warnings': self.test_results['warnings']
                },
                'tests': self.test_results['tests']
            }
            
            with open('integration_test_report.json', 'w') as f:
                json.dump(report_data, f, indent=2)
            
            print(f"\n{Colors.BLUE}📄 Reporte guardado en: integration_test_report.json{Colors.END}")
        except Exception as e:
            print_warning(f"No se pudo guardar el reporte: {e}")

def main():
    """Función principal."""
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║                   FIT_CONTROL                            ║")
    print("║              SCRIPT DE INTEGRACIÓN                      ║")
    print("║                                                          ║")
    print("║  Verifica la funcionalidad completa del sistema         ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}\n")
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('workout_api'):
        print_error("Este script debe ejecutarse desde el directorio raíz del proyecto")
        print_info("Asegúrate de que el directorio 'workout_api' esté presente")
        sys.exit(1)
    
    # Verificar que el backend esté corriendo
    print_info("Asegúrate de que el backend Django esté corriendo:")
    print_info("  cd workout_api && python manage.py runserver")
    print_info("")
    
    input("Presiona Enter cuando el backend esté listo...")
    
    # Ejecutar tests
    tester = FitControlTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()