# 🏋️ Fit_Control

## Aplicación de Fitness Inteligente con Análisis de Video IA

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://djangoproject.com)
[![React Native](https://img.shields.io/badge/React%20Native-0.72-61dafb.svg)](https://reactnative.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://typescriptlang.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8-red.svg)](https://opencv.org)

**Fit_Control** es una aplicación completa de fitness que combina un backend robusto en Django con un frontend móvil moderno en React Native. La aplicación incluye análisis de video con inteligencia artificial para evaluar la técnica de ejercicios en tiempo real.

---

## 🌟 Características Principales

### 🎥 **Análisis de Video Inteligente**
- Detección automática de poses y movimientos
- Conteo preciso de repeticiones
- Evaluación de técnica y forma
- Feedback personalizado en tiempo real
- Compatible con Python 3.13 (sin MediaPipe)

### 📱 **Frontend React Native**
- **Calendario Interactivo**: Visualiza entrenamientos programados por día
- **Biblioteca de Ejercicios**: Explora ejercicios con filtros avanzados
- **Planes de Entrenamiento**: Descubre y sigue planes personalizados
- **Perfil y Estadísticas**: Tracking completo de progreso y logros
- **Navegación Fluida**: Interfaz intuitiva con Material Design

### 🔧 **Backend Django Robusto**
- **API REST Completa**: Endpoints optimizados para móviles
- **Autenticación JWT**: Seguridad con refresh automático
- **Base de Datos Optimizada**: Modelos relacionales complejos
- **Admin Panel**: Gestión completa desde interfaz web
- **Análisis de Performance**: Métricas detalladas de usuario

### 🎯 **Funcionalidades Avanzadas**
- Sistema de logros y gamificación
- Análisis de progreso con gráficos
- Recomendaciones personalizadas
- Seguimiento de planes de entrenamiento
- Sincronización offline/online

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                     FIT_CONTROL                             │
├─────────────────────────────────────────────────────────────┤
│  Frontend (React Native + TypeScript)                      │
│  ├── 📱 TodayScreen (Calendario interactivo)               │
│  ├── 🏋️ ExercisesScreen (Biblioteca de ejercicios)         │
│  ├── 📋 PlansScreen (Planes de entrenamiento)              │
│  └── 👤 ProfileScreen (Perfil y estadísticas)              │
├─────────────────────────────────────────────────────────────┤
│  API REST (Django REST Framework)                          │
│  ├── 🔐 Authentication (JWT + Refresh tokens)              │
│  ├── 🏃 Exercises API (CRUD + filtros)                     │
│  ├── 📊 Plans API (Seguimiento + recomendaciones)          │
│  ├── 📈 Analytics API (Estadísticas + progreso)            │
│  └── 🎥 Video Analysis API (IA + OpenCV)                   │
├─────────────────────────────────────────────────────────────┤
│  Backend (Django + PostgreSQL/SQLite)                      │
│  ├── 💾 Modelos de Datos (Ejercicios, Planes, Usuarios)    │
│  ├── 🧠 Motor de Análisis (OpenCV + Computer Vision)       │
│  ├── 📊 Sistema de Estadísticas (Métricas + Logros)        │
│  └── ⚡ Optimizaciones de Performance                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Inicio Rápido

### Prerrequisitos

- **Python 3.8+** (Recomendado: 3.13)
- **Node.js 16+** (Para React Native)
- **Git**
- **Android Studio** (Para desarrollo Android)
- **Xcode** (Para desarrollo iOS - solo macOS)

### 🎯 Instalación Automática

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/fit-control.git
cd fit-control

# Ejecutar script de inicio automático
python start_fitcontrol.py --demo
```

### 📋 Instalación Manual

#### 1. Backend (Django)

```bash
# Crear entorno virtual
python -m venv fit_control_env

# Activar entorno virtual
# Windows:
fit_control_env\Scripts\activate
# macOS/Linux:
source fit_control_env/bin/activate

# Instalar dependencias
cd workout_api
pip install -r requirements.txt

# Configurar base de datos
python manage.py migrate
python manage.py createsuperuser

# Crear datos de demostración (opcional)
python manage.py shell -c "exec(open('create_demo_data.py').read())"

# Iniciar servidor
python manage.py runserver
```

#### 2. Frontend (React Native)

```bash
# Navegar al directorio mobile
cd MobileApp

# Instalar dependencias
npm install

# Para Android
npx react-native run-android

# Para iOS (solo macOS)
npx react-native run-ios
```

---

## 📖 Guía de Uso

### 🔐 **Autenticación**

```typescript
// Login con JWT
const login = async (username: string, password: string) => {
  const response = await api.post('/auth/login/', { username, password });
  const { access, refresh } = response.data;
  // Tokens se guardan automáticamente
};
```

### 🏋️ **Análisis de Video**

```python
# Backend - Análisis de ejercicio
from analysis.video_analyzer import analyze_exercise_video

result = analyze_exercise_video(
    video_path="/path/to/video.mp4",
    exercise_type="push_up"
)

# Resultado incluye:
# - Conteo de repeticiones
# - Puntuación de técnica
# - Feedback personalizado
# - Métricas de movimiento
```

### 📱 **Navegación Mobile**

```typescript
// Estructura de navegación
const AppNavigator = () => (
  <Tab.Navigator>
    <Tab.Screen name="Hoy" component={TodayScreen} />
    <Tab.Screen name="Ejercicios" component={ExercisesScreen} />
    <Tab.Screen name="Planes" component={PlansScreen} />
    <Tab.Screen name="Perfil" component={ProfileScreen} />
  </Tab.Navigator>
);
```

---

## 🧪 Testing

### Tests Automáticos de Integración

```bash
# Ejecutar suite completa de tests
python test_integration.py

# Tests específicos
python start_fitcontrol.py --test
```

### Tests Manuales

1. **Backend**: Acceder a `http://localhost:8000/admin/`
2. **API**: Probar endpoints en `http://localhost:8000/api/`
3. **Mobile**: Usar emulador Android/iOS
4. **Integración**: Verificar sincronización de datos

---

## 📊 API Endpoints

### 🔐 Autenticación
- `POST /api/auth/login/` - Login con JWT
- `POST /api/auth/register/` - Registro de usuario
- `POST /api/auth/refresh/` - Renovar token

### 🏋️ Ejercicios
- `GET /api/exercises/` - Listar ejercicios
- `GET /api/exercises/{id}/` - Detalle de ejercicio
- `GET /api/exercises/?muscle_groups=chest,arms` - Filtrar ejercicios

### 📋 Planes
- `GET /api/plans/` - Listar planes
- `POST /api/plans/{id}/follow/` - Seguir plan
- `GET /api/plans/recommended/` - Planes recomendados

### 📈 Estadísticas
- `GET /api/users/{id}/stats/` - Estadísticas de usuario
- `GET /api/users/{id}/progress/` - Progreso detallado
- `POST /api/log/` - Registrar entrenamiento

### 🎥 Análisis
- `POST /api/analyze/` - Analizar video de ejercicio

---

## 🛠️ Desarrollo

### Estructura del Proyecto

```
fit-control/
├── 📁 workout_api/          # Backend Django
│   ├── 📁 workouts/         # App de ejercicios y planes
│   ├── 📁 analysis/         # App de análisis de video
│   ├── 📁 authentication/   # App de usuarios y auth
│   └── 📁 workout_project/  # Configuración principal
├── 📁 MobileApp/            # Frontend React Native
│   ├── 📁 src/
│   │   ├── 📁 screens/      # Pantallas principales
│   │   ├── 📁 services/     # API y servicios
│   │   ├── 📁 store/        # Estado global (Zustand)
│   │   └── 📁 types/        # Definiciones TypeScript
│   └── 📄 package.json
├── 📄 start_fitcontrol.py   # Script de inicio automático
├── 📄 test_integration.py   # Tests de integración
└── 📄 README.md
```

### Configuración de Desarrollo

```python
# workout_api/workout_project/settings.py
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '10.0.2.2']  # Para emulador Android

# CORS para React Native
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

### Variables de Entorno

```bash
# .env (crear en workout_api/)
SECRET_KEY=tu-secret-key-muy-segura
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
CORS_ALLOW_ALL_ORIGINS=True
```

---

## 🐛 Solución de Problemas

### Problemas Comunes

#### 1. **Error de MediaPipe con Python 3.13**
```bash
# Solución: Usar OpenCV alternativo
pip install opencv-python==4.8.1.78
# El sistema usa implementación custom sin MediaPipe
```

#### 2. **React Native no conecta al backend**
```typescript
// Verificar configuración de API
const API_BASE_URL = __DEV__ 
  ? 'http://10.0.2.2:8000/api'  // Android emulator
  : 'https://api.fitcontrol.com/api';
```

#### 3. **Errores de CORS**
```python
# settings.py
CORS_ALLOW_ALL_ORIGINS = True  # Solo para desarrollo
CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]  # Producción
```

### Logs y Debug

```bash
# Backend logs
tail -f workout_api/logs/debug.log

# Frontend logs (React Native)
npx react-native log-android  # Android
npx react-native log-ios      # iOS
```

---

## 🤝 Contribuir

### Guía de Contribución

1. **Fork** el repositorio
2. Crear **branch** de feature (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** cambios (`git commit -am 'Add: nueva funcionalidad'`)
4. **Push** a branch (`git push origin feature/nueva-funcionalidad`)
5. Crear **Pull Request**

### Estándares de Código

- **Python**: PEP 8, Black formatter
- **TypeScript**: ESLint + Prettier
- **Commits**: Conventional Commits
- **Tests**: Cobertura mínima 80%

---

## 📈 Roadmap

### 🎯 Versión 1.1
- [ ] Integración completa con MediaPipe
- [ ] Análisis de video en tiempo real
- [ ] Modo offline completo
- [ ] Notificaciones push

### 🎯 Versión 1.2
- [ ] Social features (amigos, desafíos)
- [ ] Apple Health / Google Fit integration
- [ ] Wearables support
- [ ] AI personal trainer

### 🎯 Versión 2.0
- [ ] Multiplataforma (Web app)
- [ ] Machine Learning avanzado
- [ ] Realidad aumentada
- [ ] Marketplace de planes

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

---

## 👥 Equipo

**Desarrollado con ❤️ por el equipo de Fit_Control**

- **Backend**: Django REST Framework + OpenCV
- **Frontend**: React Native + TypeScript
- **IA**: Computer Vision + Machine Learning
- **UX/UI**: Material Design + React Native Paper

---

## 🙏 Agradecimientos

- [Django](https://djangoproject.com) - Framework web robusto
- [React Native](https://reactnative.dev) - Desarrollo móvil multiplataforma
- [OpenCV](https://opencv.org) - Computer vision y análisis de video
- [React Native Paper](https://reactnativepaper.com) - Componentes Material Design

---

## 📞 Soporte

¿Necesitas ayuda? Contáctanos:

- 📧 **Email**: soporte@fitcontrol.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/tu-usuario/fit-control/issues)
- 💬 **Discord**: [Comunidad Fit_Control](https://discord.gg/fitcontrol)
- 📖 **Docs**: [Documentación completa](https://docs.fitcontrol.com)

---

<div align="center">

### ⭐ ¡Si te gusta el proyecto, dale una estrella! ⭐

**Fit_Control** - *Revolucionando el fitness con inteligencia artificial*

[![GitHub stars](https://img.shields.io/github/stars/tu-usuario/fit-control.svg?style=social&label=Star)](https://github.com/tu-usuario/fit-control)
[![GitHub forks](https://img.shields.io/github/forks/tu-usuario/fit-control.svg?style=social&label=Fork)](https://github.com/tu-usuario/fit-control/fork)

</div>
