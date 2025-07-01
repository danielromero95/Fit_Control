# 🏋️ FitControl - Gym Performance Analyzer

> **Análisis inteligente de ejercicios de fuerza mediante computer vision**

Plataforma integral que combina análisis de vídeo con inteligencia artificial para mejorar tu técnica de entrenamiento y seguir tu progreso. Incluye aplicaciones de escritorio, móvil y web.

![FitControl Banner](assets/FitControl_logo.ico)

## ✨ Características Principales

- 🎯 **Análisis automático de ejercicios** mediante detección de pose
- 📊 **Dashboard en tiempo real** con métricas de rendimiento
- 📱 **Aplicación móvil** moderna con React Native
- 🖥️ **Aplicación de escritorio** avanzada con PyQt
- 🌐 **Interfaz web** interactiva con Streamlit
- 🎮 **Sistema de gamificación** con logros y objetivos
- 📈 **Seguimiento de progreso** detallado
- 🤖 **Recomendaciones personalizadas** basadas en IA

---

## 🚀 Instalación Rápida

### Prerrequisitos

Antes de comenzar, asegúrate de tener instalado:

1. **Python 3.8+** - [Descargar aquí](https://www.python.org/downloads/)
2. **Node.js 16+** - [Descargar aquí](https://nodejs.org/)
3. **Git** - [Descargar aquí](https://git-scm.com/)
4. **Conda** (recomendado) - [Descargar Miniconda](https://docs.conda.io/en/latest/miniconda.html)

### Paso 1: Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd gym-performance-analyzer
```

### Paso 2: Configurar el Entorno Python

#### Opción A: Con Conda (Recomendado)

```bash
# Crear y activar entorno
conda env create -f environment.yml
conda activate gym_env
```

#### Opción B: Con pip

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno (Windows)
venv\Scripts\activate

# Activar entorno (macOS/Linux)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 3: Instalar Dependencias Adicionales

```bash
# Dependencias para gráficos interactivos
pip install plotly streamlit-plotly-events

# Dependencias de PyQt (si no están incluidas)
pip install PyQt5 qtawesome
```

---

## 🖥️ Ejecutar Aplicación de Escritorio

### Método 1: Ejecutor Rápido (Recomendado)

Crea un archivo `run_desktop.py` en la raíz del proyecto:

```python
#!/usr/bin/env python3
"""
Ejecutor rápido para la aplicación de escritorio FitControl
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def main():
    try:
        print("🏋️ Iniciando FitControl Desktop...")
        print("📁 Directorio del proyecto:", project_root)
        
        # Verificar dependencias críticas
        try:
            import PyQt5
            print("✅ PyQt5 encontrado")
        except ImportError:
            print("❌ PyQt5 no encontrado. Instálalo con: pip install PyQt5")
            return
            
        try:
            import qtawesome
            print("✅ QtAwesome encontrado")
        except ImportError:
            print("❌ QtAwesome no encontrado. Instálalo con: pip install qtawesome")
            return
        
        # Importar y ejecutar la aplicación
        from gui.main import main as run_app
        print("🚀 Lanzando aplicación...")
        run_app()
        
    except Exception as e:
        print(f"❌ Error al iniciar la aplicación: {e}")
        print("\n🔧 Soluciones posibles:")
        print("1. Verifica que el entorno virtual esté activado")
        print("2. Instala las dependencias: pip install -r requirements.txt")
        print("3. Ejecuta desde el directorio raíz del proyecto")

if __name__ == "__main__":
    main()
```

**Ejecutar:**

```bash
# Activar entorno
conda activate gym_env  # o source venv/bin/activate

# Ejecutar aplicación
python run_desktop.py
```

### Método 2: Ejecución Directa

```bash
# Desde el directorio raíz
conda activate gym_env
cd src
python gui/main.py
```

### 🔧 Solución de Problemas Desktop

#### Problema: Error de importación PyQt5
```bash
# Solución
pip install PyQt5 PyQt5-tools
```

#### Problema: Error de iconos
```bash
# Solución
pip install qtawesome
```

#### Problema: Error de base de datos
```bash
# Crear directorio data si no existe
mkdir -p data
```

---

## 📱 Ejecutar Aplicación Móvil

### Paso 1: Configurar Entorno React Native

```bash
# Navegar al directorio móvil
cd MobileApp

# Instalar dependencias
npm install

# Instalar dependencias adicionales necesarias
npm install expo-linear-gradient @expo/vector-icons
npm install @react-navigation/native @react-navigation/drawer
npm install react-native-gesture-handler react-native-safe-area-context
```

### Paso 2: Configurar Expo (Recomendado para principiantes)

```bash
# Instalar Expo CLI globalmente
npm install -g expo-cli

# O usar la nueva herramienta Expo
npm install -g @expo/cli
```

### Paso 3: Ejecutar la Aplicación

#### Opción A: Con Expo (Más fácil)

```bash
# Desde MobileApp/
npx expo start

# O si tienes expo-cli instalado
expo start
```

#### Opción B: Con React Native CLI

```bash
# Para Android
npx react-native run-android

# Para iOS (solo macOS)
npx react-native run-ios
```

### Paso 4: Ver en tu Dispositivo

1. **Instala Expo Go** en tu móvil:
   - [Android: Google Play Store](https://play.google.com/store/apps/details?id=host.exp.exponent)
   - [iOS: App Store](https://apps.apple.com/app/expo-go/id982107779)

2. **Escanea el código QR** que aparece en la terminal o navegador

3. **¡La app se abrirá en tu móvil!**

### 🔧 Solución de Problemas Móvil

#### Problema: npm install falla
```bash
# Limpiar caché
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

#### Problema: Metro bundler error
```bash
# Reiniciar Metro
npx react-native start --reset-cache
```

#### Problema: Expo no se conecta
```bash
# Verificar que estés en la misma red WiFi
# Usar conexión por túnel
expo start --tunnel
```

---

## 🌐 Ejecutar Aplicación Web (Bonus)

### Streamlit Básico

```bash
# Activar entorno
conda activate gym_env

# Ejecutar app básica
cd src
streamlit run app.py
```

### Streamlit Mejorado

```bash
# Ejecutar versión mejorada
streamlit run enhanced_app.py
```

**Abrir en navegador:** http://localhost:8501

---

## 📁 Estructura del Proyecto Actualizada

```
gym-performance-analyzer/
├── 🖥️ Aplicación Desktop
│   ├── src/gui/                    # Interfaz PyQt
│   ├── src/database.py             # Base de datos
│   ├── themes/                     # Temas visuales
│   └── run_desktop.py              # Ejecutor rápido
│
├── 📱 Aplicación Móvil
│   ├── MobileApp/                  # App React Native
│   ├── MobileApp/src/screens/      # Pantallas
│   ├── MobileApp/package.json      # Dependencias
│   └── MobileApp/App.tsx           # Componente principal
│
├── 🌐 Aplicación Web
│   ├── src/app.py                  # Streamlit básico
│   ├── src/enhanced_app.py         # Streamlit mejorado
│   └── src/pipeline.py             # Pipeline de análisis
│
├── 📊 Backend Compartido
│   ├── src/database.py             # Base de datos SQLite
│   ├── src/database_extensions.py  # Métricas avanzadas
│   ├── config.yaml                 # Configuración
│   └── environment.yml             # Entorno Python
│
└── 📚 Documentación
    ├── README.md                   # Este archivo
    ├── MEJORAS_IMPLEMENTADAS.md    # Changelog detallado
    └── docs/                       # Documentación adicional
```

---

## 🎮 Primeros Pasos - Guía Rápida

### 1. Probar la Aplicación de Escritorio

1. **Ejecuta:** `python run_desktop.py`
2. **Explora** el dashboard con métricas simuladas
3. **Navega** entre las diferentes secciones
4. **Prueba** cargar un vídeo de ejercicio (opcional)

### 2. Probar la Aplicación Móvil

1. **Ejecuta:** `cd MobileApp && npx expo start`
2. **Escanea** el código QR con Expo Go
3. **Explora** las pantallas de inicio y ejercicios
4. **Prueba** la navegación del menú lateral

### 3. Comparar Funcionalidades

| Característica | 🖥️ Desktop | 📱 Móvil | 🌐 Web |
|---------------|-----------|--------|--------|
| Dashboard | ✅ Completo | ✅ Moderno | ✅ Interactivo |
| Análisis de vídeo | ✅ Avanzado | ⏳ Futuro | ✅ Básico |
| Ejercicios | ✅ Completo | ✅ Biblioteca | ⏳ Futuro |
| Progreso | ✅ Gráficos | ✅ Estadísticas | ✅ Charts |
| Planes | ✅ Calendario | ✅ Vista previa | ⏳ Futuro |

---

## 🔍 Scripts de Verificación

### Verificar Instalación Desktop

Crea `check_desktop.py`:

```python
def check_desktop_requirements():
    requirements = {
        'PyQt5': False,
        'qtawesome': False,
        'sqlite3': False,
        'opencv-cv2': False
    }
    
    for req in requirements:
        try:
            __import__(req.replace('-', '_'))
            requirements[req] = True
            print(f"✅ {req}")
        except ImportError:
            print(f"❌ {req} - pip install {req}")
    
    return all(requirements.values())

if __name__ == "__main__":
    print("🔍 Verificando dependencias para Desktop...")
    if check_desktop_requirements():
        print("\n🎉 ¡Todo listo para ejecutar la app desktop!")
    else:
        print("\n⚠️ Instala las dependencias faltantes")
```

### Verificar Instalación Móvil

```bash
# Desde MobileApp/
node -e "
const pkg = require('./package.json');
console.log('📱 Verificando dependencias móvil...');
console.log('✅ React Native:', pkg.dependencies['react-native'] ? 'OK' : '❌');
console.log('✅ Expo:', pkg.dependencies['expo'] ? 'OK' : '❌');
console.log('✅ Navigation:', pkg.dependencies['@react-navigation/native'] ? 'OK' : '❌');
"
```

---

## 🆘 Soporte y Ayuda

### Problemas Comunes

1. **"Module not found"**
   ```bash
   # Verificar que estás en el directorio correcto
   pwd
   # Verificar que el entorno está activado
   conda info --envs
   ```

2. **"No se puede conectar al dispositivo móvil"**
   ```bash
   # Verificar red WiFi (mismo dispositivo)
   # Usar túnel de Expo
   expo start --tunnel
   ```

3. **"Error de base de datos"**
   ```bash
   # Crear directorio data
   mkdir -p data
   # Dar permisos
   chmod 755 data
   ```

### Comandos de Emergencia

```bash
# Resetear entorno Python
conda deactivate
conda env remove -n gym_env
conda env create -f environment.yml

# Resetear aplicación móvil
cd MobileApp
rm -rf node_modules
npm install

# Limpiar cachés
npm cache clean --force
pip cache purge
```

---

## 🏆 ¡Felicidades!

Si has llegado hasta aquí y tienes ambas aplicaciones funcionando, ¡has configurado exitosamente **FitControl**! 

### Próximos pasos:
1. 🎯 Explora todas las funcionalidades
2. 📊 Revisa las métricas del dashboard
3. 🎮 Prueba los diferentes temas
4. 📱 Compara la experiencia móvil vs desktop
5. 🔄 Sincroniza datos entre plataformas

---

## 📞 Contacto y Contribuciones

- 🐛 **Reportar bugs:** Abre un issue describiendo el problema
- 💡 **Sugerir mejoras:** Ideas y feedback son bienvenidos
- 🤝 **Contribuir:** Fork, mejora y envía pull requests

---

*README actualizado: Diciembre 2024*
*Versión: 2.0 - Multiplataforma*
