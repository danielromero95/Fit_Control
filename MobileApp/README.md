# TechniqueAnalyzer - Aplicación Móvil de Análisis de Técnica Deportiva

Una aplicación móvil avanzada para Android e iOS que utiliza MediaPipe para analizar la técnica deportiva a través de grabación de video y detección de puntos clave corporales.

## 🏃‍♂️ Características

- **Grabación de Video**: Captura movimientos deportivos con la cámara del dispositivo
- **Análisis en Tiempo Real**: Detección de puntos clave corporales usando MediaPipe
- **Feedback Inteligente**: Análisis automático de la técnica y sugerencias de mejora
- **Historial de Análisis**: Seguimiento del progreso a lo largo del tiempo
- **Tema Oscuro**: Diseño moderno y elegante optimizado para cualquier momento del día
- **Múltiples Ejercicios**: Soporte para sentadillas, press banca, peso muerto, y más

## 🛠️ Configuración de Desarrollo en Windows 11

### Prerrequisitos

1. **Node.js** (versión 18 o superior)
   ```bash
   # Descargar desde https://nodejs.org/
   # O usar chocolatey
   choco install nodejs
   ```

2. **Git**
   ```bash
   # Descargar desde https://git-scm.com/
   # O usar chocolatey
   choco install git
   ```

3. **Yarn** (recomendado sobre npm)
   ```bash
   npm install -g yarn
   ```

4. **Android Studio** (para desarrollo Android)
   - Descargar desde: https://developer.android.com/studio
   - Instalar Android SDK
   - Configurar variables de entorno:
     ```
     ANDROID_HOME=C:\Users\%USERNAME%\AppData\Local\Android\Sdk
     PATH=%PATH%;%ANDROID_HOME%\platform-tools;%ANDROID_HOME%\tools
     ```

5. **JDK 11** (requerido por React Native)
   ```bash
   # Usar chocolatey
   choco install openjdk11
   ```

### Configuración para iOS (Opcional - requiere macOS para build final)

6. **Xcode** (solo macOS)
   - Para desarrollo iOS necesitarás acceso a una Mac con Xcode
   - Puedes usar servicios como macOS en la nube o GitHub Actions para CI/CD

### Configuración del Proyecto

#### 1. Navegar al directorio de la aplicación móvil
```bash
cd MobileApp
```

#### 2. Instalar dependencias
```bash
# Limpiar caché si hay problemas
yarn cache clean

# Instalar dependencias
yarn install

# Para iOS (si estás en macOS)
cd ios && pod install && cd ..
```

#### 3. Configurar Android
```bash
# Verificar configuración
npx react-native doctor

# Si hay problemas, limpiar
yarn run clean
cd android && ./gradlew clean && cd ..
```

#### 4. Configurar variables de entorno
Crear archivo `.env` en el directorio MobileApp:
```env
# MediaPipe Configuration
MEDIAPIPE_MODEL_URL=https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task

# API Configuration (si planeas usar un backend)
API_BASE_URL=http://localhost:3000

# App Configuration
APP_VERSION=1.0.0
```

### Ejecución de la Aplicación

#### Desarrollo Android
```bash
# Iniciar Metro bundler
yarn start

# En otra terminal, ejecutar en Android
yarn android

# O específicamente para debug
yarn run android --variant=debug
```

#### Desarrollo iOS (macOS requerido)
```bash
# Iniciar Metro bundler
yarn start

# En otra terminal, ejecutar en iOS
yarn ios

# O específicamente para simulador
yarn run ios --simulator="iPhone 14"
```

#### Comandos útiles
```bash
# Limpiar caché de Metro
yarn start --reset-cache

# Limpiar todo y reinstalar
yarn run clean
rm -rf node_modules
yarn install

# Ver logs en tiempo real
# Android
adb logcat | grep ReactNativeJS

# iOS (macOS)
npx react-native log-ios
```

## 📱 Estructura de la Aplicación

```
MobileApp/
├── src/
│   ├── screens/          # Pantallas principales
│   │   ├── HomeScreen.tsx       # Dashboard principal
│   │   ├── RecordingScreen.tsx  # Grabación de video
│   │   ├── AnalysisScreen.tsx   # Resultados de análisis
│   │   ├── HistoryScreen.tsx    # Historial de análisis
│   │   └── SettingsScreen.tsx   # Configuración
│   ├── components/       # Componentes reutilizables
│   ├── services/         # Servicios (MediaPipe, API)
│   ├── store/           # Estado global (Zustand)
│   └── navigation/      # Configuración de navegación
├── android/             # Código específico Android
├── ios/                 # Código específico iOS
├── package.json         # Dependencias y scripts
└── README.md           # Esta documentación
```

## 🎨 Paleta de Colores (Tema Oscuro)

- **Fondo Principal**: `#121212`
- **Fondo Secundario**: `#1F1F1F`
- **Acento Principal**: `#BB86FC` (Púrpura)
- **Acento Secundario**: `#03DAC6` (Turquesa)
- **Texto Principal**: `#FFFFFF`
- **Texto Secundario**: `#AAAAAA`
- **Error/Advertencia**: `#CF6679`
- **Éxito**: `#03DAC6`

## 🔧 Configuración de VSCode/Cursor

### Extensiones Recomendadas
```json
{
  "recommendations": [
    "ms-vscode.vscode-typescript-next",
    "bradlc.vscode-tailwindcss",
    "ms-vscode.vscode-eslint",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-react-native",
    "formulahendry.auto-rename-tag",
    "christian-kohler.path-intellisense"
  ]
}
```

### Configuración de workspace (.vscode/settings.json)
```json
{
  "typescript.preferences.importModuleSpecifier": "relative",
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "eslint.workingDirectories": ["MobileApp"],
  "files.associations": {
    "*.tsx": "typescriptreact"
  }
}
```

## 📦 Dependencias Principales

### Navegación y UI
- `@react-navigation/native` - Navegación
- `@react-navigation/drawer` - Menú lateral
- `react-native-linear-gradient` - Gradientes
- `react-native-vector-icons` - Iconos

### Cámara y Video
- `react-native-vision-camera` - Grabación de video avanzada
- `react-native-permissions` - Manejo de permisos

### Análisis de IA
- `@mediapipe/tasks-vision` - Detección de poses
- `@tensorflow/tfjs-react-native` - TensorFlow para React Native

### Estado y Persistencia
- `zustand` - Manejo de estado
- `@react-native-async-storage/async-storage` - Almacenamiento local

## 🚀 Build para Producción

### Android Release
```bash
# Generar APK de release
cd android
./gradlew assembleRelease

# Generar AAB (recomendado para Google Play Store)
./gradlew bundleRelease
```

### iOS Release (macOS requerido)
```bash
# Build para distribución
npx react-native run-ios --configuration Release

# Para App Store (usar Xcode)
# Abrir ios/TechniqueAnalyzer.xcworkspace en Xcode
# Product -> Archive
```

## 🧪 Testing

```bash
# Ejecutar tests unitarios
yarn test

# Ejecutar tests en modo watch
yarn test --watch

# Coverage
yarn test --coverage
```

## 🔍 Debugging

### Flipper (Recomendado)
```bash
# Instalar Flipper
# Descargar desde: https://fbflipper.com/

# Configurar en package.json ya incluido
```

### React Native Debugger
```bash
# Instalar React Native Debugger
choco install react-native-debugger

# Usar con Metro bundler
```

### Debug en dispositivo físico

#### Android
```bash
# Habilitar debug USB en dispositivo
# Configurar ADB
adb devices

# Ejecutar en dispositivo
yarn android
```

#### iOS
```bash
# Conectar dispositivo iOS
# Confiar en la computadora
# Ejecutar desde Xcode
```

## 🔧 Solución de Problemas

### Problemas Comunes

#### Error de Metro bundler
```bash
yarn start --reset-cache
```

#### Error de dependencias nativas
```bash
# Android
cd android && ./gradlew clean && cd ..

# iOS
cd ios && rm -rf Pods && pod install && cd ..
```

#### Error de permisos de cámara
- Verificar configuración en `android/app/src/main/AndroidManifest.xml`
- Para iOS: verificar `ios/TechniqueAnalyzer/Info.plist`

### Logs útiles
```bash
# Android logs
adb logcat | grep "ReactNativeJS\|MediaPipe\|Camera"

# Metro bundler logs
yarn start --verbose
```

## 📚 Recursos

### Documentación
- [React Native](https://reactnative.dev/docs/getting-started)
- [MediaPipe](https://developers.google.com/mediapipe)
- [React Navigation](https://reactnavigation.org/)

### Tutoriales
- [React Native Camera](https://react-native-vision-camera.com/)
- [MediaPipe Pose Detection](https://developers.google.com/mediapipe/solutions/vision/pose_landmarker)

## 🤝 Contribución

1. Fork el repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## ✨ Créditos

- **MediaPipe** por Google para detección de poses
- **React Native Community** por las librerías utilizadas
- **Iconos** por Ionicons

---

## 📞 Soporte

Si tienes problemas durante el desarrollo:

1. Revisa la sección de solución de problemas
2. Verifica que todas las dependencias estén instaladas
3. Asegúrate de que Android Studio esté configurado correctamente
4. Comprueba que las variables de entorno estén configuradas

Para desarrollo desde Windows 11, este setup te permitirá desarrollar y hacer debug de la aplicación Android. Para iOS, necesitarás acceso a macOS para builds finales, pero puedes usar servicios en la nube o CI/CD para automatizar el proceso.

**¡Disfruta desarrollando TechniqueAnalyzer! 🚀**
