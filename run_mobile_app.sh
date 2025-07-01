#!/bin/bash

# Script para ejecutar la aplicación móvil React Native
echo "📱 Iniciando FitControl Mobile App..."

# Cambiar al directorio MobileApp
cd MobileApp

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js no está instalado. Por favor instala Node.js primero."
    echo "📥 Descárgalo desde: https://nodejs.org/"
    exit 1
fi

# Verificar npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm no está disponible"
    exit 1
fi

# Instalar dependencias
echo "📦 Instalando dependencias de Node.js..."
npm install

# Verificar si React Native CLI está instalado globalmente
if ! command -v react-native &> /dev/null; then
    echo "🔧 Instalando React Native CLI globalmente..."
    npm install -g react-native-cli
fi

# Verificar si hay dispositivos Android conectados
echo "🔍 Verificando dispositivos Android..."
if command -v adb &> /dev/null; then
    adb devices
else
    echo "⚠️ ADB no encontrado. Asegúrate de tener Android SDK instalado."
fi

echo ""
echo "📱 Opciones disponibles:"
echo "1. Ejecutar en Android (dispositivo/emulador)"
echo "2. Ejecutar en iOS (solo macOS)"
echo "3. Solo iniciar Metro bundler"
echo ""

read -p "Selecciona una opción (1-3): " choice

case $choice in
    1)
        echo "🤖 Iniciando aplicación en Android..."
        npm run android
        ;;
    2)
        if [[ "$OSTYPE" == "darwin"* ]]; then
            echo "🍎 Iniciando aplicación en iOS..."
            cd ios && pod install && cd ..
            npm run ios
        else
            echo "❌ iOS solo está disponible en macOS"
            exit 1
        fi
        ;;
    3)
        echo "📦 Iniciando Metro bundler..."
        npm start
        ;;
    *)
        echo "❌ Opción no válida"
        exit 1
        ;;
esac

echo "✅ Aplicación móvil finalizada"