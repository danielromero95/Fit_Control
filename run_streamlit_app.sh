#!/bin/bash

# Script para ejecutar la aplicación Streamlit del Gym Performance Analyzer
echo "🌐 Iniciando Gym Performance Analyzer Streamlit Demo..."

# Verificar si el entorno conda existe
if ! conda info --envs | grep -q "gym_env"; then
    echo "❌ El entorno 'gym_env' no existe. Creándolo..."
    conda env create -f environment.yml
    if [ $? -ne 0 ]; then
        echo "❌ Error al crear el entorno conda"
        exit 1
    fi
fi

# Activar el entorno conda
echo "🔧 Activando entorno conda 'gym_env'..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate gym_env

# Verificar que estamos en el entorno correcto
if [ "$CONDA_DEFAULT_ENV" != "gym_env" ]; then
    echo "❌ Error al activar el entorno conda"
    exit 1
fi

# Cambiar al directorio src
cd src

# Ejecutar la aplicación Streamlit
echo "🚀 Iniciando aplicación Streamlit..."
echo "📱 La aplicación estará disponible en: http://localhost:8501"
streamlit run app.py

echo "✅ Aplicación Streamlit finalizada"