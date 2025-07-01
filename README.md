# 🏋️ TechniqueAnalyzer - Analizador de Técnica Deportiva

**Aplicación móvil avanzada para Android** que utiliza MediaPipe para analizar la técnica deportiva a través de grabación de video y detección de puntos clave corporales. Incluye funcionalidades completas de análisis de ejercicios, generación de planes de entrenamiento con IA y seguimiento de progreso.

## 🎯 **Funcionalidades Principales**

### 📱 **Aplicación Móvil React Native**
- **🎥 Grabación de Video**: Captura movimientos deportivos con la cámara del dispositivo
- **🤖 Análisis en Tiempo Real**: Detección de puntos clave corporales usando MediaPipe
- **💡 Feedback Inteligente**: Análisis automático de la técnica y sugerencias de mejora
- **📊 Historial de Análisis**: Seguimiento del progreso a lo largo del tiempo
- **🌙 Tema Oscuro**: Diseño moderno y elegante optimizado para cualquier momento del día
- **🏋️ Múltiples Ejercicios**: Soporte para sentadillas, press banca, peso muerto, y más

### �️ **Aplicaciones de Escritorio**
- **🎮 GUI Launcher**: Interfaz gráfica moderna para ejecutar todas las aplicaciones
- **📊 Aplicación GUI PyQt**: Análisis completo de técnica deportiva con interfaz de escritorio
- **🌐 Demo Web Streamlit**: Versión web para demostraciones
- **� API Django**: Backend para servicios de análisis

## 🚀 **Configuración Completa para Windows 11**

### **Paso 1: Instalación de Prerrequisitos Básicos**

#### **1.1 Chocolatey (Gestor de Paquetes)**
Abre PowerShell como Administrador y ejecuta:
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

#### **1.2 Git**
```powershell
choco install git -y
```

#### **1.3 Node.js (versión 18 LTS)**
```powershell
choco install nodejs-lts -y
```

#### **1.4 Python (para aplicaciones de escritorio)**
```powershell
choco install python -y
```

#### **1.5 JDK 11 (requerido por React Native)**
```powershell
choco install openjdk11 -y
```

#### **1.6 Yarn (gestor de paquetes recomendado)**
```powershell
npm install -g yarn
```

### **Paso 2: Instalación de Android Studio**

#### **2.1 Descargar Android Studio**
1. Ve a: https://developer.android.com/studio
2. Descarga la versión para Windows
3. Ejecuta el instalador como Administrador

#### **2.2 Configuración de Android Studio**
1. **Abrir Android Studio**
2. **Welcome Screen** → **More Actions** → **SDK Manager**
3. En **SDK Platforms**, instalar:
   - ✅ Android 13 (API level 33)
   - ✅ Android 12 (API level 31)
   - ✅ Android 11 (API level 30)
4. En **SDK Tools**, verificar que estén instalados:
   - ✅ Android SDK Build-Tools
   - ✅ Android SDK Command-line Tools
   - ✅ Android SDK Platform-Tools
   - ✅ Android Emulator
   - ✅ Intel x86 Emulator Accelerator (HAXM installer)

#### **2.3 Configurar Variables de Entorno**
1. **Buscar "Variables de entorno"** en el menú de Windows
2. **Editar las variables de entorno del sistema**
3. **Variables del sistema** → **Nueva**

**ANDROID_HOME:**
```
Variable: ANDROID_HOME
Valor: C:\Users\%USERNAME%\AppData\Local\Android\Sdk
```

**PATH (agregar estas rutas):**
```
%ANDROID_HOME%\platform-tools
%ANDROID_HOME%\tools
%ANDROID_HOME%\tools\bin
```

#### **2.4 Verificar Instalación**
Abre una nueva ventana de PowerShell:
```powershell
adb version
android --version
```

### **Paso 3: Crear y Configurar Emulador Android**

#### **3.1 Crear Dispositivo Virtual**
1. **Android Studio** → **More Actions** → **AVD Manager**
2. **Create Virtual Device**
3. **Seleccionar dispositivo**: Pixel 6 o similar
4. **Seleccionar imagen del sistema**: 
   - Recomendado: **API 33** (Android 13)
   - Arquitectura: **x86_64** (más rápido)
5. **Configuraciones avanzadas**:
   - RAM: 4GB mínimo
   - Internal Storage: 8GB mínimo
   - Graphics: Hardware - GLES 2.0

#### **3.2 Optimizar Rendimiento del Emulador**
En la configuración avanzada del AVD:
```
CPU/ABI: x86_64
RAM: 4096 MB
VM Heap: 512 MB
Internal Storage: 8192 MB
Graphics: Hardware - GLES 2.0
Boot option: Cold boot
```

### **Paso 4: Configuración del Proyecto**

#### **4.1 Clonar el Repositorio**
```bash
git clone [URL_DEL_REPOSITORIO]
cd [NOMBRE_DEL_REPOSITORIO]
```

#### **4.2 Configurar Entorno Python (para aplicaciones de escritorio)**
```bash
# Crear entorno conda
conda env create -f environment.yml
conda activate gym_env

# O con pip si no tienes conda
pip install -r requirements.txt
```

#### **4.3 Configurar Aplicación Móvil**
```bash
# Navegar al directorio de la aplicación móvil
cd MobileApp

# Limpiar caché (si es necesario)
yarn cache clean

# Instalar dependencias
yarn install

# Verificar configuración de React Native
npx react-native doctor
```

### **Paso 5: Ejecutar la Aplicación Móvil**

#### **5.1 Iniciar Emulador Android**
1. **Android Studio** → **AVD Manager**
2. **Clic en ▶️** junto a tu dispositivo virtual
3. **Esperar a que cargue completamente** (puede tardar 2-3 minutos la primera vez)

#### **5.2 Verificar Conexión**
```bash
# Verificar que el emulador esté conectado
adb devices
# Deberías ver algo como: emulator-5554    device
```

#### **5.3 Ejecutar la Aplicación**
Desde el directorio `MobileApp`:

```bash
# Opción 1: Usar el script automatizado (recomendado)
./start-dev.bat

# Opción 2: Ejecutar manualmente
# Terminal 1: Iniciar Metro bundler
yarn start

# Terminal 2: Ejecutar en Android
yarn android
```

### **Paso 6: Ejecutar Aplicaciones de Escritorio**

#### **6.1 GUI Launcher (Recomendado)**
```bash
# Configuración automática (solo la primera vez)
./setup_easy_launcher.sh

# Ejecutar launcher
./run_launcher.sh
# O simplemente: gym-launcher
```

#### **6.2 Aplicaciones Individuales**
```bash
# Aplicación GUI completa
./run_gui_app.sh

# Demo web Streamlit
./run_streamlit_app.sh

# API Django
./run_django_api.sh
```

## 🛠️ **Solución de Problemas Comunes**

### **Problemas con Android Studio/Emulador**

#### **Error: "ANDROID_HOME no está configurado"**
```bash
# Verificar variables de entorno
echo $ANDROID_HOME
# Si está vacío, configurar según Paso 2.3
```

#### **Error: "adb no encontrado"**
```bash
# Agregar platform-tools al PATH
# Windows: C:\Users\%USERNAME%\AppData\Local\Android\Sdk\platform-tools
```

#### **Emulador muy lento**
1. **Verificar BIOS**: Habilitar Intel VT-x/AMD-V
2. **Windows Features**: Activar Hyper-V y Windows Hypervisor Platform
3. **AVD Settings**: Usar x86_64 y Graphics: Hardware

#### **Error: "Unable to locate adb"**
```bash
# Restart adb server
adb kill-server
adb start-server
```

### **Problemas con React Native**

#### **Error de Metro bundler**
```bash
yarn start --reset-cache
```

#### **Error de dependencias**
```bash
# Limpiar e reinstalar
cd MobileApp
rm -rf node_modules
yarn cache clean
yarn install
```

#### **Error de Gradle (Android)**
```bash
cd MobileApp/android
./gradlew clean
cd ..
yarn android
```

### **Problemas con Python/Conda**

#### **Error de entorno**
```bash
# Verificar entorno activo
conda info --envs
conda activate gym_env
```

#### **Error de dependencias Python**
```bash
# Reinstalar requirements
pip install -r requirements.txt --force-reinstall
```

## 📱 **Guía de Uso de la Aplicación Móvil**

### **Primer Uso**
1. **Abrir la aplicación** en el emulador
2. **Permitir permisos** de cámara cuando se solicite
3. **Seleccionar ejercicio** (sentadilla, press banca, etc.)
4. **Grabar movimiento** siguiendo las instrucciones en pantalla
5. **Ver análisis** con feedback automático

### **Características Principales**
- **📊 Dashboard**: Resumen de progreso y estadísticas
- **🎥 Grabación**: Captura de video con guías visuales
- **📈 Análisis**: Resultados detallados con puntos clave
- **📅 Historial**: Seguimiento de evolución en el tiempo
- **⚙️ Configuración**: Personalización de la experiencia

## 🎯 **Estructura del Proyecto**

```text
├── MobileApp/                    # Aplicación móvil React Native
│   ├── src/
│   │   ├── screens/             # Pantallas principales
│   │   ├── components/          # Componentes reutilizables
│   │   ├── services/            # MediaPipe y servicios API
│   │   └── store/               # Estado global (Zustand)
│   ├── android/                 # Código específico Android
│   └── package.json             # Dependencias móviles
├── src/                         # Aplicaciones de escritorio
│   ├── gui/                     # Aplicación PyQt
│   ├── services/                # IA generativa
│   └── pipeline.py              # Pipeline de análisis
├── environment.yml              # Entorno Conda
├── requirements.txt             # Dependencias Python
└── README.md                    # Esta documentación
```

## 🚀 **Comandos Rápidos**

### **Desarrollo Móvil**
```bash
cd MobileApp
yarn start          # Iniciar Metro bundler
yarn android        # Ejecutar en Android
yarn reset          # Limpiar caché
adb devices         # Ver dispositivos conectados
```

### **Desarrollo Escritorio**
```bash
./run_launcher.sh                # GUI Launcher
./run_gui_app.sh                # Aplicación PyQt
./run_streamlit_app.sh          # Demo web
conda activate gym_env          # Activar entorno
```

## 📞 **Soporte y Recursos**

### **Documentación Oficial**
- [React Native](https://reactnative.dev/docs/getting-started)
- [Android Studio](https://developer.android.com/studio/intro)
- [MediaPipe](https://developers.google.com/mediapipe)

### **Verificación Final**
Antes de reportar problemas, ejecuta:
```bash
# Verificar entorno móvil
cd MobileApp && npx react-native doctor

# Verificar entorno Python
./verificar_entorno.sh

# Verificar conexión Android
adb devices
```

---

**¡Listo para analizar tu técnica deportiva! 🏋️‍♂️**

> **Nota**: Este setup está optimizado para Windows 11. La primera ejecución puede tardar más debido a la descarga de dependencias y la configuración inicial del emulador Android.
