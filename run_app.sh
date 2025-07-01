#!/bin/bash

# Script maestro para ejecutar las aplicaciones del Gym Performance Analyzer
clear
echo "🏋️ ==============================================="
echo "🏋️   GYM PERFORMANCE ANALYZER - LAUNCHER       "
echo "🏋️ ==============================================="
echo ""
echo "Selecciona qué aplicación quieres ejecutar:"
echo ""
echo "1. 🖥️  Aplicación GUI (PyQt) - Interfaz de escritorio completa"
echo "2. 🌐 Demo Streamlit - Interfaz web para análisis rápido"
echo "3. 🔧 API Django - Backend/API para entrenamientos"
echo "4. 📱 Aplicación Móvil (React Native) - FitControl"
echo "5. 🚀 Ejecutar todas las aplicaciones (en paralelo)"
echo "6. ❌ Salir"
echo ""

read -p "Introduce tu opción (1-6): " choice

case $choice in
    1)
        echo ""
        echo "🖥️ Iniciando Aplicación GUI..."
        ./run_gui_app.sh
        ;;
    2)
        echo ""
        echo "🌐 Iniciando Demo Streamlit..."
        ./run_streamlit_app.sh
        ;;
    3)
        echo ""
        echo "🔧 Iniciando API Django..."
        ./run_django_api.sh
        ;;
    4)
        echo ""
        echo "📱 Iniciando Aplicación Móvil..."
        ./run_mobile_app.sh
        ;;
    5)
        echo ""
        echo "🚀 Iniciando todas las aplicaciones en paralelo..."
        echo "⚠️  Nota: Esto ejecutará múltiples terminales. Usa Ctrl+C para detener."
        echo ""
        
        # Ejecutar cada aplicación en segundo plano
        echo "🌐 Iniciando Streamlit en puerto 8501..."
        gnome-terminal --title="Streamlit App" -- bash -c "./run_streamlit_app.sh; exec bash" &
        
        sleep 2
        echo "🔧 Iniciando Django API en puerto 8000..."
        gnome-terminal --title="Django API" -- bash -c "./run_django_api.sh; exec bash" &
        
        sleep 2
        echo "📱 Iniciando aplicación móvil..."
        gnome-terminal --title="Mobile App" -- bash -c "./run_mobile_app.sh; exec bash" &
        
        sleep 2
        echo "🖥️ Iniciando aplicación GUI..."
        ./run_gui_app.sh
        ;;
    6)
        echo ""
        echo "👋 ¡Hasta luego!"
        exit 0
        ;;
    *)
        echo ""
        echo "❌ Opción no válida. Por favor selecciona una opción del 1 al 6."
        exit 1
        ;;
esac

echo ""
echo "✅ Proceso completado. ¡Gracias por usar Gym Performance Analyzer!"