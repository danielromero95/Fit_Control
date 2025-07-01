#!/bin/bash

# TechniqueAnalyzer Mobile App Starter
echo "🏋️ Iniciando TechniqueAnalyzer Mobile App..."
echo ""

# Verificar si Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "❌ Node.js no está instalado. Por favor instala Node.js >= 16"
    exit 1
fi

# Verificar versión de Node.js
NODE_VERSION=$(node -v)
echo "✅ Node.js detectado: $NODE_VERSION"

# Cambiar al directorio de la app móvil
cd MobileApp

# Verificar si package.json existe
if [ ! -f "package.json" ]; then
    echo "❌ No se encontró package.json en MobileApp/"
    exit 1
fi

echo "📦 Instalando dependencias..."
npm install

echo ""
echo "🚀 Para ejecutar la app móvil:"
echo ""
echo "📱 Android:"
echo "   npx react-native run-android"
echo ""
echo "🍎 iOS (solo macOS):"
echo "   cd ios && pod install && cd .."
echo "   npx react-native run-ios"
echo ""
echo "🔄 Para limpiar cache:"
echo "   npx react-native start --reset-cache"
echo ""
echo "✨ ¡App móvil lista para desarrollo!"