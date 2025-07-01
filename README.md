# TechniqueAnalyzer - Mobile App

Una aplicación móvil React Native para análisis de técnicas de ejercicio usando inteligencia artificial y análisis de poses.

## �️ Características

- **Análisis de Poses en Tiempo Real**: Detección y análisis de posturas corporales durante ejercicios
- **Feedback Instantáneo**: Correcciones y sugerencias para mejorar la técnica
- **Seguimiento de Progreso**: Historial de entrenamientos y métricas de rendimiento
- **Interfaz Intuitiva**: Diseño moderno y fácil de usar
- **Detección de Ejercicios**: Reconocimiento automático de diferentes tipos de ejercicios

## � Tecnologías

- **React Native 0.72**: Framework principal
- **TypeScript**: Tipado estático
- **TensorFlow.js**: Análisis de poses con IA
- **MediaPipe**: Detección de puntos clave corporales
- **React Navigation**: Navegación entre pantallas
- **Zustand**: Gestión de estado
- **React Native Paper**: Componentes UI

## 🚀 Configuración Rápida

### Prerrequisitos

- Node.js >= 16
- React Native CLI
- Android Studio (para Android)
- Xcode (para iOS, solo macOS)

### Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd TechniqueAnalyzer
   ```

2. **Instalar dependencias**
   ```bash
   cd MobileApp
   npm install
   ```

3. **Configurar plataformas**

   **Para Android:**
   ```bash
   npx react-native run-android
   ```

   **Para iOS:**
   ```bash
   cd ios && pod install && cd ..
   npx react-native run-ios
   ```

## 📂 Estructura del Proyecto

```
MobileApp/
├── src/                    # Código fuente de la app
├── android/               # Configuración Android
├── ios/                   # Configuración iOS
├── App.tsx               # Componente principal
├── package.json          # Dependencias y scripts
└── README.md            # Documentación de la app móvil

src/                      # Backend/API (opcional)
├── config.py            # Configuración
├── pipeline.py          # Pipeline de análisis
└── services/           # Servicios de backend
```

## 🔧 Scripts Disponibles

```bash
# Iniciar el servidor de desarrollo
npm start

# Ejecutar en Android
npm run android

# Ejecutar en iOS
npm run ios

# Limpiar cache
npm run reset

# Ejecutar tests
npm test

# Linter
npm run lint
```

## 🤖 Funcionalidades de IA

### Análisis de Poses
- Detección de 33 puntos clave corporales
- Análisis biomecánico en tiempo real
- Cálculo de ángulos articulares
- Detección de patrones de movimiento

### Ejercicios Soportados
- Sentadillas (Squats)
- Flexiones (Push-ups)
- Peso muerto (Deadlifts)
- Press de banca
- Dominadas
- Y más...

## 📊 Características Principales

### 🎯 Análisis en Tiempo Real
- Captura de video desde la cámara
- Procesamiento instantáneo de poses
- Feedback visual y auditivo

### 📈 Seguimiento de Progreso
- Historial de entrenamientos
- Métricas de rendimiento
- Gráficos de evolución
- Estadísticas detalladas

### 🎨 Interfaz de Usuario
- Diseño Material Design
- Navegación intuitiva
- Modo oscuro/claro
- Animaciones fluidas

## 🛠️ Desarrollo

### Configuración del Entorno

1. **Instalar dependencias de desarrollo**
   ```bash
   npm install --dev
   ```

2. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Editar .env con tus configuraciones
   ```

3. **Generar builds**
   ```bash
   # Android APK
   cd android && ./gradlew assembleRelease

   # iOS IPA (requiere macOS)
   npx react-native run-ios --configuration Release
   ```

### Estructura de Componentes

```
src/
├── components/          # Componentes reutilizables
├── screens/            # Pantallas de la app
├── navigation/         # Configuración de navegación
├── services/          # Servicios y APIs
├── utils/            # Utilidades
├── hooks/           # Hooks personalizados
└── types/          # Tipos TypeScript
```

## 🔧 Configuración Avanzada

### Backend API (Opcional)
Si necesitas funcionalidades de backend, puedes usar el código en `/src`:

```bash
# Instalar dependencias Python
pip install -r requirements.txt

# Configurar base de datos
python src/database.py

# Ejecutar API
python src/app.py
```

## 🚀 Despliegue

### Android
1. Generar APK firmado
2. Subir a Google Play Store

### iOS
1. Generar IPA
2. Subir a App Store Connect

## 🤝 Contribuir

1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver [LICENSE](LICENSE) para detalles.

## 🙋‍♂️ Soporte

¿Necesitas ayuda? 
- Crear un [Issue](../../issues)
- Consultar la [Documentación](../../wiki)
- Contactar al equipo de desarrollo

---

⭐ ¡No olvides dar una estrella al repositorio si te gusta el proyecto!
