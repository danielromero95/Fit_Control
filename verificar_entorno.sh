#!/bin/bash

# Script para verificar que el entorno está listo para ejecutar las aplicaciones
echo "🔍 Verificando entorno para Gym Performance Analyzer..."
echo "=================================================="

# Variables para el resumen final
errors=0
warnings=0

# Función para mostrar estado
check_status() {
    if [ $1 -eq 0 ]; then
        echo "✅ $2"
    else
        echo "❌ $2"
        ((errors++))
    fi
}

check_warning() {
    echo "⚠️ $1"
    ((warnings++))
}

echo ""
echo "🐍 Verificando Python y Conda..."
echo "---------------------------------"

# Verificar Python
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version)
    check_status 0 "Python encontrado: $python_version"
else
    check_status 1 "Python 3 no encontrado"
fi

# Verificar Conda
if command -v conda &> /dev/null; then
    conda_version=$(conda --version)
    check_status 0 "Conda encontrado: $conda_version"
    
    # Verificar entorno gym_env
    if conda info --envs | grep -q "gym_env"; then
        check_status 0 "Entorno 'gym_env' existe"
    else
        check_warning "Entorno 'gym_env' no existe (se creará automáticamente)"
    fi
else
    check_status 1 "Conda no encontrado - necesario para GUI y Streamlit"
fi

echo ""
echo "🌐 Verificando Node.js y npm..."
echo "-------------------------------"

# Verificar Node.js
if command -v node &> /dev/null; then
    node_version=$(node --version)
    check_status 0 "Node.js encontrado: $node_version"
else
    check_status 1 "Node.js no encontrado - necesario para app móvil"
fi

# Verificar npm
if command -v npm &> /dev/null; then
    npm_version=$(npm --version)
    check_status 0 "npm encontrado: $npm_version"
else
    check_status 1 "npm no encontrado - necesario para app móvil"
fi

echo ""
echo "📱 Verificando herramientas móviles..."
echo "-------------------------------------"

# Verificar React Native CLI
if command -v react-native &> /dev/null; then
    rn_version=$(react-native --version | head -n1)
    check_status 0 "React Native CLI: $rn_version"
else
    check_warning "React Native CLI no instalado (se instalará automáticamente)"
fi

# Verificar ADB (Android)
if command -v adb &> /dev/null; then
    check_status 0 "ADB (Android Debug Bridge) encontrado"
else
    check_warning "ADB no encontrado - necesario para desarrollo Android"
fi

echo ""
echo "🔧 Verificando archivos del proyecto..."
echo "--------------------------------------"

# Verificar archivos clave
files=("environment.yml" "src/app.py" "src/gui/main.py" "workout_api/manage.py" "MobileApp/package.json")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        check_status 0 "Archivo encontrado: $file"
    else
        check_status 1 "Archivo faltante: $file"
    fi
done

# Verificar scripts de ejecución
scripts=("run_app.sh" "run_gui_app.sh" "run_streamlit_app.sh" "run_django_api.sh" "run_mobile_app.sh")
for script in "${scripts[@]}"; do
    if [ -f "$script" ] && [ -x "$script" ]; then
        check_status 0 "Script ejecutable: $script"
    elif [ -f "$script" ]; then
        check_warning "Script existe pero no es ejecutable: $script"
    else
        check_status 1 "Script faltante: $script"
    fi
done

echo ""
echo "🌐 Verificando puertos disponibles..."
echo "------------------------------------"

# Verificar puertos
ports=(8000 8501)
for port in "${ports[@]}"; do
    if ! netstat -tuln 2>/dev/null | grep -q ":$port "; then
        check_status 0 "Puerto $port disponible"
    else
        check_warning "Puerto $port en uso - puede causar conflictos"
    fi
done

echo ""
echo "📊 RESUMEN DE VERIFICACIÓN"
echo "=========================="

if [ $errors -eq 0 ] && [ $warnings -eq 0 ]; then
    echo "🎉 ¡Perfecto! Tu entorno está completamente listo."
    echo "   Puedes ejecutar cualquier aplicación sin problemas."
elif [ $errors -eq 0 ]; then
    echo "✅ Tu entorno está listo con algunas advertencias menores."
    echo "   Las aplicaciones deberían funcionar correctamente."
    echo "   Advertencias: $warnings"
else
    echo "⚠️ Se encontraron algunos problemas que necesitan atención."
    echo "   Errores: $errors | Advertencias: $warnings"
fi

echo ""
echo "🚀 PRÓXIMOS PASOS:"
echo "=================="

if [ $errors -gt 0 ]; then
    echo "1. Soluciona los errores mostrados arriba"
    echo "2. Ejecuta este script nuevamente para verificar"
    echo "3. Una vez solucionado, ejecuta: ./run_app.sh"
else
    echo "¡Estás listo para empezar!"
    echo "Ejecuta: ./run_app.sh"
fi

echo ""
echo "📚 Para más ayuda, consulta: GUIA_EJECUCION.md"

exit $errors