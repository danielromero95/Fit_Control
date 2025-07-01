#!/bin/bash

# Script para ejecutar el GUI Launcher del Gym Performance Analyzer
# Este script proporciona la manera más fácil de acceder a todas las aplicaciones

set -e  # Salir si hay algún error

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}🏋️ ================================================${NC}"
echo -e "${BLUE}🏋️   GYM PERFORMANCE ANALYZER - GUI LAUNCHER    ${NC}"
echo -e "${BLUE}🏋️ ================================================${NC}"
echo ""

# Verificar si Python está disponible
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: Python3 no está instalado o no está en el PATH${NC}"
    echo "Por favor instala Python3 y vuelve a intentar."
    exit 1
fi

# Verificar si tkinter está disponible
if ! python3 -c "import tkinter" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Advertencia: tkinter no está disponible${NC}"
    echo "Instalando tkinter..."
    
    # Intentar instalar tkinter según el sistema
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y python3-tk
    elif command -v yum &> /dev/null; then
        sudo yum install -y tkinter
    elif command -v pacman &> /dev/null; then
        sudo pacman -S tk
    else
        echo -e "${RED}❌ No se pudo instalar tkinter automáticamente${NC}"
        echo "Por favor instala tkinter manualmente para tu sistema."
        echo "Ubuntu/Debian: sudo apt-get install python3-tk"
        echo "CentOS/RHEL: sudo yum install tkinter"
        echo "Arch: sudo pacman -S tk"
        exit 1
    fi
fi

# Verificar que estamos en el directorio correcto
if [ ! -f "config.yaml" ] || [ ! -d "src" ]; then
    echo -e "${RED}❌ Error: No se encontraron los archivos del proyecto${NC}"
    echo "Asegúrate de ejecutar este script desde el directorio raíz del proyecto."
    exit 1
fi

# Activar entorno conda si existe
if command -v conda &> /dev/null && conda info --envs | grep -q gym_env; then
    echo -e "${YELLOW}🔧 Activando entorno conda gym_env...${NC}"
    eval "$(conda shell.bash hook)"
    conda activate gym_env
fi

# Hacer el launcher ejecutable
chmod +x launcher.py

# Preguntar qué launcher usar
echo -e "${YELLOW}Selecciona el tipo de launcher:${NC}"
echo "1. 🎨 GUI Launcher Completo (recomendado)"
echo "2. 🔧 GUI Launcher Simple (para sistemas limitados)"
echo "3. 💻 Launcher de Terminal"
echo ""
read -p "Elige una opción (1-3) [1]: " launcher_choice
launcher_choice=${launcher_choice:-1}

case $launcher_choice in
    1)
        echo -e "${GREEN}🚀 Iniciando GUI Launcher Completo...${NC}"
        echo ""
        
        if python3 launcher.py; then
            echo ""
            echo -e "${GREEN}✅ GUI Launcher cerrado correctamente${NC}"
        else
            echo ""
            echo -e "${RED}❌ Error ejecutando GUI Launcher Completo${NC}"
            echo -e "${YELLOW}Probando launcher simple...${NC}"
            python3 -c "import sys; sys.path.insert(0, 'src'); from gui.simple_launcher import main; main()"
        fi
        ;;
    2)
        echo -e "${GREEN}🚀 Iniciando GUI Launcher Simple...${NC}"
        echo ""
        
        if python3 -c "import sys; sys.path.insert(0, 'src'); from gui.simple_launcher import main; main()"; then
            echo ""
            echo -e "${GREEN}✅ GUI Launcher Simple cerrado correctamente${NC}"
        else
            echo ""
            echo -e "${RED}❌ Error ejecutando GUI Launcher Simple${NC}"
            echo -e "${YELLOW}Usando launcher de terminal...${NC}"
            ./run_app.sh
        fi
        ;;
    3)
        echo -e "${GREEN}🚀 Iniciando Launcher de Terminal...${NC}"
        echo ""
        ./run_app.sh
        ;;
    *)
        echo -e "${RED}❌ Opción no válida. Usando launcher completo por defecto.${NC}"
        python3 launcher.py
        ;;
esac

# Si hubo errores, mostrar alternativas
if [ $? -ne 0 ]; then
    echo ""
    echo -e "${YELLOW}💡 Alternativas si hay problemas:${NC}"
    echo "1. Ejecutar aplicaciones individualmente:"
    echo "   ./run_gui_app.sh       # Aplicación GUI"
    echo "   ./run_streamlit_app.sh # Demo web"
    echo "   ./run_django_api.sh    # API Django"
    echo "   ./run_mobile_app.sh    # App móvil"
    echo ""
    echo "2. Verificar el entorno:"
    echo "   ./verificar_entorno.sh"
    echo ""
    echo "3. Configurar de nuevo:"
    echo "   ./setup_easy_launcher.sh"
fi