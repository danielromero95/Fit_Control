#!/bin/bash

# 📱 FitControl Mobile - Ejecutor Rápido
# ======================================
# 
# Script para ejecutar la aplicación móvil React Native de forma fácil.
# Incluye verificaciones automáticas y configuración del entorno.
#
# Uso: ./run_mobile.sh [opción]
# Opciones:
#   start    - Iniciar con Expo (por defecto)
#   web      - Iniciar en navegador web
#   android  - Iniciar en Android
#   ios      - Iniciar en iOS (solo macOS)
#   check    - Solo verificar dependencias

# Colores para terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Función para imprimir banner
print_banner() {
    echo -e "${CYAN}${BOLD}"
    echo "📱 ═══════════════════════════════════════════════════════════════════"
    echo "   ███████╗██╗████████╗    ██████╗ ██████╗ ███╗   ██╗████████╗██████╗  ██████╗ ██╗     "
    echo "   ██╔════╝██║╚══██╔══╝   ██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝██╔══██╗██╔═══██╗██║     "
    echo "   █████╗  ██║   ██║      ██║     ██║   ██║██╔██╗ ██║   ██║   ██████╔╝██║   ██║██║     "
    echo "   ██╔══╝  ██║   ██║      ██║     ██║   ██║██║╚██╗██║   ██║   ██╔══██╗██║   ██║██║     "
    echo "   ██║     ██║   ██║      ╚██████╗╚██████╔╝██║ ╚████║   ██║   ██║  ██║╚██████╔╝███████╗"
    echo "   ╚═╝     ╚═╝   ╚═╝       ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝"
    echo ""
    echo "                    🎯 Ejecutor de Aplicación Móvil React Native"
    echo "═══════════════════════════════════════════════════════════════════"
    echo -e "${NC}"
}

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Función para verificar Node.js
check_node() {
    if command_exists node; then
        node_version=$(node --version)
        major_version=$(echo $node_version | cut -d'.' -f1 | sed 's/v//')
        
        if [ "$major_version" -ge 16 ]; then
            echo -e "${GREEN}✅ Node.js $node_version - Compatible${NC}"
            return 0
        else
            echo -e "${RED}❌ Node.js $node_version - Se requiere v16 o superior${NC}"
            echo "   Descarga desde: https://nodejs.org/"
            return 1
        fi
    else
        echo -e "${RED}❌ Node.js no encontrado${NC}"
        echo "   Instala Node.js desde: https://nodejs.org/"
        return 1
    fi
}

# Función para verificar npm
check_npm() {
    if command_exists npm; then
        npm_version=$(npm --version)
        echo -e "${GREEN}✅ npm $npm_version${NC}"
        return 0
    else
        echo -e "${RED}❌ npm no encontrado${NC}"
        return 1
    fi
}

# Función para verificar directorio MobileApp
check_mobile_dir() {
    if [ -d "MobileApp" ]; then
        echo -e "${GREEN}✅ Directorio MobileApp encontrado${NC}"
        return 0
    else
        echo -e "${RED}❌ Directorio MobileApp no encontrado${NC}"
        echo "   Ejecuta este script desde la raíz del proyecto"
        return 1
    fi
}

# Función para verificar package.json
check_package_json() {
    if [ -f "MobileApp/package.json" ]; then
        echo -e "${GREEN}✅ package.json encontrado${NC}"
        return 0
    else
        echo -e "${RED}❌ package.json no encontrado en MobileApp${NC}"
        return 1
    fi
}

# Función para verificar node_modules
check_node_modules() {
    if [ -d "MobileApp/node_modules" ]; then
        echo -e "${GREEN}✅ node_modules existe${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️ node_modules no encontrado${NC}"
        echo "   Instalando dependencias..."
        return 1
    fi
}

# Función para instalar dependencias
install_dependencies() {
    echo -e "${CYAN}📦 Instalando dependencias...${NC}"
    
    cd MobileApp || exit 1
    
    echo "Instalando dependencias básicas..."
    npm install
    
    echo "Instalando dependencias adicionales..."
    npm install expo-linear-gradient @expo/vector-icons
    npm install @react-navigation/native @react-navigation/drawer
    npm install react-native-gesture-handler react-native-safe-area-context
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Dependencias instaladas correctamente${NC}"
        cd ..
        return 0
    else
        echo -e "${RED}❌ Error instalando dependencias${NC}"
        cd ..
        return 1
    fi
}

# Función para verificar Expo
check_expo() {
    if npx expo --version >/dev/null 2>&1; then
        expo_version=$(npx expo --version 2>/dev/null)
        echo -e "${GREEN}✅ Expo CLI disponible ($expo_version)${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️ Verificando Expo...${NC}"
        return 0  # npx expo funcionará aunque no esté instalado globalmente
    fi
}

# Función principal de verificación
run_checks() {
    echo -e "${BOLD}🔍 Realizando verificaciones iniciales...${NC}"
    echo ""
    
    local all_good=true
    
    # Verificar Node.js
    if ! check_node; then
        all_good=false
    fi
    
    # Verificar npm
    if ! check_npm; then
        all_good=false
    fi
    
    # Verificar directorio
    if ! check_mobile_dir; then
        all_good=false
        echo -e "${RED}💀 No se puede continuar sin el directorio MobileApp${NC}"
        exit 1
    fi
    
    # Verificar package.json
    if ! check_package_json; then
        all_good=false
        echo -e "${RED}💀 No se puede continuar sin package.json${NC}"
        exit 1
    fi
    
    # Verificar node_modules
    if ! check_node_modules; then
        echo -e "${YELLOW}📦 Instalando dependencias faltantes...${NC}"
        if ! install_dependencies; then
            all_good=false
            echo -e "${RED}💀 Error instalando dependencias${NC}"
            exit 1
        fi
    fi
    
    # Verificar Expo
    check_expo
    
    if [ "$all_good" = true ]; then
        echo -e "\n${GREEN}🎉 Todas las verificaciones pasaron exitosamente${NC}"
        return 0
    else
        echo -e "\n${RED}⚠️ Algunas verificaciones fallaron${NC}"
        return 1
    fi
}

# Función para ejecutar la aplicación
run_app() {
    local mode="$1"
    
    echo -e "\n${CYAN}🚀 Iniciando aplicación móvil...${NC}"
    echo -e "${WHITE}📱 Modo: $mode${NC}"
    echo ""
    
    cd MobileApp || exit 1
    
    case "$mode" in
        "start"|"")
            echo -e "${CYAN}Iniciando con Expo...${NC}"
            echo -e "${WHITE}📋 Instrucciones:${NC}"
            echo "1. Escanea el código QR con la app Expo Go"
            echo "2. O presiona 'w' para abrir en navegador"
            echo "3. Presiona Ctrl+C para detener"
            echo ""
            npx expo start
            ;;
        "web")
            echo -e "${CYAN}Iniciando en navegador web...${NC}"
            npx expo start --web
            ;;
        "android")
            echo -e "${CYAN}Iniciando en Android...${NC}"
            echo "Asegúrate de tener un emulador de Android ejecutándose"
            npx react-native run-android
            ;;
        "ios")
            if [[ "$OSTYPE" == "darwin"* ]]; then
                echo -e "${CYAN}Iniciando en iOS...${NC}"
                echo "Asegúrate de tener un simulador de iOS disponible"
                npx react-native run-ios
            else
                echo -e "${RED}❌ iOS solo es compatible con macOS${NC}"
                exit 1
            fi
            ;;
        *)
            echo -e "${RED}❌ Modo no reconocido: $mode${NC}"
            show_help
            exit 1
            ;;
    esac
    
    cd ..
}

# Función para mostrar ayuda
show_help() {
    echo -e "${CYAN}📖 Ayuda - FitControl Mobile${NC}"
    echo ""
    echo -e "${BOLD}Uso:${NC}"
    echo "    ./run_mobile.sh [opción]"
    echo ""
    echo -e "${BOLD}Opciones:${NC}"
    echo "    start     - Iniciar con Expo (por defecto)"
    echo "    web       - Iniciar en navegador web"
    echo "    android   - Iniciar en Android"
    echo "    ios       - Iniciar en iOS (solo macOS)"
    echo "    check     - Solo verificar dependencias"
    echo "    help      - Mostrar esta ayuda"
    echo ""
    echo -e "${BOLD}Ejemplos:${NC}"
    echo "    ./run_mobile.sh          # Modo por defecto (Expo)"
    echo "    ./run_mobile.sh start    # Expo con código QR"
    echo "    ./run_mobile.sh web      # Ejecutar en navegador"
    echo "    ./run_mobile.sh check    # Solo verificar"
    echo ""
    echo -e "${BOLD}Problemas comunes:${NC}"
    echo "    • 'comando no encontrado' → chmod +x run_mobile.sh"
    echo "    • 'Node.js no encontrado' → Instala desde nodejs.org"
    echo "    • 'Expo no se conecta' → Usa --tunnel: npx expo start --tunnel"
    echo ""
}

# Función para limpiar en caso de interrupción
cleanup() {
    echo -e "\n\n${YELLOW}⏹️ Aplicación interrumpida por el usuario${NC}"
    echo -e "${WHITE}👋 ¡Hasta luego!${NC}"
    exit 0
}

# Configurar trap para Ctrl+C
trap cleanup SIGINT SIGTERM

# Función principal
main() {
    local mode="$1"
    
    # Procesar argumentos
    case "$mode" in
        "help"|"-h"|"--help")
            print_banner
            show_help
            exit 0
            ;;
        "check")
            print_banner
            run_checks
            exit $?
            ;;
        "start"|"web"|"android"|"ios"|"")
            print_banner
            if run_checks; then
                run_app "$mode"
            else
                echo -e "${RED}💀 No se puede continuar debido a errores en las verificaciones${NC}"
                exit 1
            fi
            ;;
        *)
            print_banner
            echo -e "${RED}❌ Opción no reconocida: $mode${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Verificar si el script tiene permisos de ejecución
if [ ! -x "$0" ]; then
    echo -e "${YELLOW}⚠️ Dando permisos de ejecución al script...${NC}"
    chmod +x "$0"
fi

# Ejecutar función principal con todos los argumentos
main "$@"