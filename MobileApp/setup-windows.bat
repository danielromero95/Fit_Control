@echo off
echo.
echo ========================================
echo  TechniqueAnalyzer Setup para Windows
echo ========================================
echo.

REM Verificar si Node.js está instalado
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js no está instalado.
    echo Por favor instala Node.js desde: https://nodejs.org/
    echo O usa chocolatey: choco install nodejs
    pause
    exit /b 1
)

echo [OK] Node.js encontrado
node --version

REM Verificar si Yarn está instalado
yarn --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Yarn no encontrado, instalando...
    npm install -g yarn
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudo instalar Yarn
        pause
        exit /b 1
    )
)

echo [OK] Yarn encontrado
yarn --version

REM Verificar si Android Studio está configurado
if not exist "%ANDROID_HOME%" (
    echo [WARNING] ANDROID_HOME no está configurado
    echo Por favor instala Android Studio y configura las variables de entorno:
    echo ANDROID_HOME=C:\Users\%USERNAME%\AppData\Local\Android\Sdk
    echo PATH=%PATH%;%ANDROID_HOME%\platform-tools;%ANDROID_HOME%\tools
    echo.
    echo ¿Continuar sin Android Studio? (y/N)
    set /p continue="Respuesta: "
    if /i not "%continue%"=="y" (
        echo Configuración cancelada
        pause
        exit /b 1
    )
) else (
    echo [OK] Android Studio configurado en: %ANDROID_HOME%
)

REM Verificar si JDK está instalado
java -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Java JDK no encontrado
    echo Se recomienda instalar JDK 11: choco install openjdk11
    echo.
)

echo.
echo ========================================
echo  Instalando dependencias...
echo ========================================
echo.

REM Limpiar caché anterior
echo [INFO] Limpiando caché...
yarn cache clean

REM Instalar dependencias
echo [INFO] Instalando dependencias de React Native...
yarn install
if %errorlevel% neq 0 (
    echo [ERROR] Error instalando dependencias
    pause
    exit /b 1
)

echo [OK] Dependencias instaladas correctamente

REM Crear archivo .env si no existe
if not exist ".env" (
    echo [INFO] Creando archivo .env...
    echo # MediaPipe Configuration > .env
    echo MEDIAPIPE_MODEL_URL=https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task >> .env
    echo. >> .env
    echo # API Configuration >> .env
    echo API_BASE_URL=http://localhost:3000 >> .env
    echo. >> .env
    echo # App Configuration >> .env
    echo APP_VERSION=1.0.0 >> .env
    echo [OK] Archivo .env creado
)

REM Configurar Android si está disponible
if exist "%ANDROID_HOME%" (
    echo.
    echo [INFO] Verificando configuración de Android...
    npx react-native doctor
    
    echo.
    echo [INFO] Limpiando build de Android...
    cd android
    call gradlew clean
    cd ..
)

REM Configurar permisos de iconos
echo [INFO] Configurando iconos...
npx react-native-asset

echo.
echo ========================================
echo  Configuración VSCode/Cursor
echo ========================================
echo.

REM Crear configuración de VSCode
if not exist ".vscode" mkdir .vscode

echo [INFO] Creando configuración de workspace...
echo { > .vscode/settings.json
echo   "typescript.preferences.importModuleSpecifier": "relative", >> .vscode/settings.json
echo   "editor.formatOnSave": true, >> .vscode/settings.json
echo   "editor.defaultFormatter": "esbenp.prettier-vscode", >> .vscode/settings.json
echo   "eslint.workingDirectories": ["MobileApp"], >> .vscode/settings.json
echo   "files.associations": { >> .vscode/settings.json
echo     "*.tsx": "typescriptreact" >> .vscode/settings.json
echo   } >> .vscode/settings.json
echo } >> .vscode/settings.json

echo { > .vscode/extensions.json
echo   "recommendations": [ >> .vscode/extensions.json
echo     "ms-vscode.vscode-typescript-next", >> .vscode/extensions.json
echo     "ms-vscode.vscode-eslint", >> .vscode/extensions.json
echo     "esbenp.prettier-vscode", >> .vscode/extensions.json
echo     "ms-vscode.vscode-react-native", >> .vscode/extensions.json
echo     "formulahendry.auto-rename-tag", >> .vscode/extensions.json
echo     "christian-kohler.path-intellisense" >> .vscode/extensions.json
echo   ] >> .vscode/extensions.json
echo } >> .vscode/extensions.json

echo.
echo ========================================
echo  ¡Configuración Completada!
echo ========================================
echo.

echo TechniqueAnalyzer está listo para desarrollar.
echo.
echo Próximos pasos:
echo 1. Abre el proyecto en VSCode/Cursor
echo 2. Instala las extensiones recomendadas
echo 3. Conecta un dispositivo Android o inicia un emulador
echo 4. Ejecuta: yarn start
echo 5. En otra terminal: yarn android
echo.

if exist "%ANDROID_HOME%" (
    echo ¿Quieres iniciar el Metro bundler ahora? (y/N)
    set /p startMetro="Respuesta: "
    if /i "%startMetro%"=="y" (
        echo [INFO] Iniciando Metro bundler...
        start cmd /k "yarn start"
        echo.
        echo Metro bundler iniciado en nueva ventana.
        echo Para ejecutar en Android, abre otra terminal y ejecuta: yarn android
    )
)

echo.
echo ¡Disfruta desarrollando TechniqueAnalyzer! 🚀
echo.
pause