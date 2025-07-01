#!/bin/bash

# Script de configuración para el Easy Launcher del Gym Performance Analyzer
# Este script configura todo lo necesario para la ejecución fácil de las aplicaciones

set -e

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}🔧 ================================================${NC}"
echo -e "${BLUE}🔧   CONFIGURACIÓN EASY LAUNCHER - GYM ANALYZER  ${NC}"
echo -e "${BLUE}🔧 ================================================${NC}"
echo ""

# Función para mostrar progreso
show_progress() {
    echo -e "${CYAN}➤ $1${NC}"
}

# Función para mostrar éxito
show_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Función para mostrar error
show_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "config.yaml" ] || [ ! -d "src" ]; then
    show_error "No se encontraron los archivos del proyecto"
    echo "Ejecuta este script desde el directorio raíz del proyecto."
    exit 1
fi

show_progress "Configurando permisos de ejecución..."
chmod +x run_launcher.sh
chmod +x launcher.py
chmod +x run_app.sh
chmod +x run_gui_app.sh
chmod +x run_streamlit_app.sh
chmod +x run_django_api.sh
chmod +x run_mobile_app.sh
chmod +x verificar_entorno.sh
chmod +x GymAnalyzer-Launcher.desktop
show_success "Permisos configurados"

# Verificar dependencias
show_progress "Verificando dependencias..."

# Python
if ! command -v python3 &> /dev/null; then
    show_error "Python3 no está instalado"
    echo "Instala Python3 y vuelve a ejecutar este script."
    exit 1
fi

# Tkinter (para GUI)
if ! python3 -c "import tkinter" &> /dev/null; then
    show_progress "Instalando tkinter..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update -qq && sudo apt-get install -y python3-tk
    elif command -v yum &> /dev/null; then
        sudo yum install -y tkinter
    elif command -v pacman &> /dev/null; then
        sudo pacman -S tk
    else
        show_error "No se pudo instalar tkinter automáticamente"
        echo "Instala tkinter manualmente:"
        echo "  Ubuntu/Debian: sudo apt-get install python3-tk"
        echo "  CentOS/RHEL: sudo yum install tkinter"
        echo "  Arch: sudo pacman -S tk"
        exit 1
    fi
    show_success "tkinter instalado"
else
    show_success "tkinter disponible"
fi

# Conda
if command -v conda &> /dev/null; then
    if ! conda info --envs | grep -q gym_env; then
        show_progress "Creando entorno conda gym_env..."
        conda env create -f environment.yml
        show_success "Entorno conda creado"
    else
        show_success "Entorno conda gym_env ya existe"
    fi
else
    show_progress "Conda no encontrado - usando Python del sistema"
fi

# Crear alias para fácil acceso
show_progress "Configurando alias de shell..."

ALIAS_LINE="alias gym-launcher='cd $(pwd) && ./run_launcher.sh'"
BASHRC="$HOME/.bashrc"
ZSHRC="$HOME/.zshrc"

# Agregar alias a .bashrc si existe
if [ -f "$BASHRC" ]; then
    if ! grep -q "gym-launcher" "$BASHRC"; then
        echo "" >> "$BASHRC"
        echo "# Gym Performance Analyzer Easy Launcher" >> "$BASHRC"
        echo "$ALIAS_LINE" >> "$BASHRC"
        show_success "Alias agregado a .bashrc"
    else
        show_success "Alias ya existe en .bashrc"
    fi
fi

# Agregar alias a .zshrc si existe
if [ -f "$ZSHRC" ]; then
    if ! grep -q "gym-launcher" "$ZSHRC"; then
        echo "" >> "$ZSHRC"
        echo "# Gym Performance Analyzer Easy Launcher" >> "$ZSHRC"
        echo "$ALIAS_LINE" >> "$ZSHRC"
        show_success "Alias agregado a .zshrc"
    else
        show_success "Alias ya existe en .zshrc"
    fi
fi

# Crear directorio de aplicaciones de usuario si no existe
DESKTOP_DIR="$HOME/Desktop"
APPLICATIONS_DIR="$HOME/.local/share/applications"

if [ ! -d "$APPLICATIONS_DIR" ]; then
    mkdir -p "$APPLICATIONS_DIR"
fi

# Copiar launcher de escritorio a aplicaciones de usuario
show_progress "Instalando launcher de escritorio..."
sed "s|/workspace|$(pwd)|g" GymAnalyzer-Launcher.desktop > "$APPLICATIONS_DIR/GymAnalyzer-Launcher.desktop"
chmod +x "$APPLICATIONS_DIR/GymAnalyzer-Launcher.desktop"

# Copiar también al escritorio si existe
if [ -d "$DESKTOP_DIR" ]; then
    cp "$APPLICATIONS_DIR/GymAnalyzer-Launcher.desktop" "$DESKTOP_DIR/"
    show_success "Launcher agregado al escritorio"
fi

show_success "Launcher agregado al menú de aplicaciones"

# Actualizar base de datos de aplicaciones
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$APPLICATIONS_DIR"
fi

echo ""
echo -e "${GREEN}🎉 ¡CONFIGURACIÓN COMPLETADA!${NC}"
echo ""
echo -e "${YELLOW}Formas de ejecutar el launcher:${NC}"
echo ""
echo -e "${CYAN}1. 🖥️  Desde el menú de aplicaciones:${NC}"
echo "   Busca 'Gym Performance Analyzer' en tu menú de aplicaciones"
echo ""
echo -e "${CYAN}2. 🖱️  Desde el escritorio:${NC}"
echo "   Doble clic en el icono 'Gym Performance Analyzer' del escritorio"
echo ""
echo -e "${CYAN}3. 💻 Desde terminal (después de reiniciar terminal):${NC}"
echo "   gym-launcher"
echo ""
echo -e "${CYAN}4. 📁 Desde este directorio:${NC}"
echo "   ./run_launcher.sh"
echo ""
echo -e "${CYAN}5. 🚀 GUI Launcher directo:${NC}"
echo "   python3 launcher.py"
echo ""
echo -e "${YELLOW}💡 Tip: El GUI Launcher te permitirá ejecutar todas las aplicaciones${NC}"
echo -e "${YELLOW}    con un solo clic, sin necesidad de recordar comandos.${NC}"
echo ""

# Preguntar si quiere ejecutar ahora
read -p "¿Quieres ejecutar el GUI Launcher ahora? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    show_progress "Ejecutando GUI Launcher..."
    ./run_launcher.sh
fi