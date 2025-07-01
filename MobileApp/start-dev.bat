@echo off
echo.
echo ========================================
echo  TechniqueAnalyzer - Inicio Desarrollo
echo ========================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist "package.json" (
    echo [ERROR] No se encontró package.json
    echo Asegúrate de estar en el directorio MobileApp
    pause
    exit /b 1
)

echo [INFO] Verificando dependencias...
yarn --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Yarn no está instalado
    echo Ejecuta primero: setup-windows.bat
    pause
    exit /b 1
)

echo [INFO] Limpiando caché de Metro...
yarn start --reset-cache >nul 2>&1

echo.
echo Opciones de desarrollo:
echo 1. Iniciar Metro bundler
echo 2. Ejecutar en Android
echo 3. Ejecutar Metro + Android (recomendado)
echo 4. Limpiar proyecto y reinstalar
echo 5. Ver logs de Android
echo 6. Salir
echo.

set /p option="Selecciona una opción (1-6): "

if "%option%"=="1" (
    echo [INFO] Iniciando Metro bundler...
    yarn start
) else if "%option%"=="2" (
    echo [INFO] Ejecutando en Android...
    yarn android
) else if "%option%"=="3" (
    echo [INFO] Iniciando Metro bundler en nueva ventana...
    start cmd /k "echo Metro Bundler - TechniqueAnalyzer && yarn start"
    timeout /t 3 >nul
    echo [INFO] Ejecutando en Android...
    yarn android
) else if "%option%"=="4" (
    echo [INFO] Limpiando proyecto...
    yarn run clean
    echo [INFO] Eliminando node_modules...
    rmdir /s /q node_modules 2>nul
    echo [INFO] Reinstalando dependencias...
    yarn install
    echo [INFO] Limpiando Android...
    cd android && call gradlew clean && cd ..
    echo [OK] Proyecto limpio, ya puedes desarrollar
) else if "%option%"=="5" (
    echo [INFO] Mostrando logs de Android (Ctrl+C para salir)...
    adb logcat | findstr "ReactNativeJS\|MediaPipe\|Camera\|TechniqueAnalyzer"
) else if "%option%"=="6" (
    echo Saliendo...
    exit /b 0
) else (
    echo [ERROR] Opción inválida
    pause
    goto :eof
)

echo.
echo ¡Desarrollo iniciado! 🚀
echo.
pause