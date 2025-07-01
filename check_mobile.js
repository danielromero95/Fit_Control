#!/usr/bin/env node
/**
 * 📱 FitControl Mobile - Verificador de Dependencias
 * ===================================================
 * 
 * Script de verificación para la aplicación móvil React Native.
 * Revisa dependencias, configuración y estado del proyecto.
 * 
 * Uso: node check_mobile.js
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Colores para terminal
const colors = {
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    cyan: '\x1b[36m',
    white: '\x1b[37m',
    bold: '\x1b[1m',
    reset: '\x1b[0m'
};

function printBanner() {
    console.log(`
${colors.cyan}${colors.bold}
📱 ═══════════════════════════════════════════════════════════════════
   ███████╗██╗████████╗    ██████╗ ██████╗ ███╗   ██╗████████╗██████╗  ██████╗ ██╗     
   ██╔════╝██║╚══██╔══╝   ██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝██╔══██╗██╔═══██╗██║     
   █████╗  ██║   ██║      ██║     ██║   ██║██╔██╗ ██║   ██║   ██████╔╝██║   ██║██║     
   ██╔══╝  ██║   ██║      ██║     ██║   ██║██║╚██╗██║   ██║   ██╔══██╗██║   ██║██║     
   ██║     ██║   ██║      ╚██████╗╚██████╔╝██║ ╚████║   ██║   ██║  ██║╚██████╔╝███████╗
   ╚═╝     ╚═╝   ╚═╝       ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
                                                                                        
                    🎯 Verificador de Aplicación Móvil React Native
═══════════════════════════════════════════════════════════════════${colors.reset}
    `);
}

function checkNodeVersion() {
    try {
        const nodeVersion = process.version;
        const majorVersion = parseInt(nodeVersion.slice(1).split('.')[0]);
        
        if (majorVersion >= 16) {
            console.log(`${colors.green}✅ Node.js ${nodeVersion} - Compatible${colors.reset}`);
            return true;
        } else {
            console.log(`${colors.red}❌ Node.js ${nodeVersion} - Se requiere v16 o superior${colors.reset}`);
            console.log(`   Descarga desde: https://nodejs.org/`);
            return false;
        }
    } catch (error) {
        console.log(`${colors.red}❌ Error verificando Node.js: ${error.message}${colors.reset}`);
        return false;
    }
}

function checkNpmVersion() {
    try {
        const npmVersion = execSync('npm --version', { encoding: 'utf8' }).trim();
        console.log(`${colors.green}✅ npm ${npmVersion}${colors.reset}`);
        return true;
    } catch (error) {
        console.log(`${colors.red}❌ npm no encontrado${colors.reset}`);
        return false;
    }
}

function checkMobileAppDirectory() {
    const mobileAppPath = path.join(process.cwd(), 'MobileApp');
    
    if (!fs.existsSync(mobileAppPath)) {
        console.log(`${colors.red}❌ Directorio MobileApp no encontrado${colors.reset}`);
        console.log(`   Buscado en: ${mobileAppPath}`);
        console.log(`   Ejecuta este script desde la raíz del proyecto`);
        return false;
    }
    
    console.log(`${colors.green}✅ Directorio MobileApp encontrado${colors.reset}`);
    return mobileAppPath;
}

function checkPackageJson(mobileAppPath) {
    const packageJsonPath = path.join(mobileAppPath, 'package.json');
    
    if (!fs.existsSync(packageJsonPath)) {
        console.log(`${colors.red}❌ package.json no encontrado en MobileApp${colors.reset}`);
        return null;
    }
    
    try {
        const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
        console.log(`${colors.green}✅ package.json cargado correctamente${colors.reset}`);
        return packageJson;
    } catch (error) {
        console.log(`${colors.red}❌ Error leyendo package.json: ${error.message}${colors.reset}`);
        return null;
    }
}

function checkDependencies(packageJson) {
    const requiredDependencies = {
        'react': 'React framework',
        'react-native': 'React Native framework',
        'expo': 'Expo SDK',
        '@react-navigation/native': 'Navigation library',
        '@react-navigation/drawer': 'Drawer navigation',
        'react-native-gesture-handler': 'Gesture handling',
        'react-native-safe-area-context': 'Safe area handling'
    };

    const optionalDependencies = {
        'expo-linear-gradient': 'Linear gradients',
        '@expo/vector-icons': 'Vector icons'
    };

    console.log(`\n${colors.yellow}🔍 Verificando dependencias principales...${colors.reset}`);
    
    let allRequired = true;
    const dependencies = { ...packageJson.dependencies, ...packageJson.devDependencies };
    
    for (const [dep, description] of Object.entries(requiredDependencies)) {
        if (dependencies[dep]) {
            console.log(`${colors.green}✅ ${dep} (${dependencies[dep]}) - ${description}${colors.reset}`);
        } else {
            console.log(`${colors.red}❌ ${dep} - ${description}${colors.reset}`);
            allRequired = false;
        }
    }

    console.log(`\n${colors.yellow}🔍 Verificando dependencias opcionales...${colors.reset}`);
    
    for (const [dep, description] of Object.entries(optionalDependencies)) {
        if (dependencies[dep]) {
            console.log(`${colors.green}✅ ${dep} (${dependencies[dep]}) - ${description}${colors.reset}`);
        } else {
            console.log(`${colors.yellow}⚠️ ${dep} - ${description} (recomendado)${colors.reset}`);
        }
    }

    return allRequired;
}

function checkNodeModules(mobileAppPath) {
    const nodeModulesPath = path.join(mobileAppPath, 'node_modules');
    
    if (!fs.existsSync(nodeModulesPath)) {
        console.log(`${colors.red}❌ node_modules no encontrado${colors.reset}`);
        console.log(`   Ejecuta: cd MobileApp && npm install`);
        return false;
    }
    
    console.log(`${colors.green}✅ node_modules existe${colors.reset}`);
    return true;
}

function checkExpoConfiguration(mobileAppPath) {
    const appJsonPath = path.join(mobileAppPath, 'app.json');
    const expoJsonPath = path.join(mobileAppPath, 'expo.json');
    
    if (fs.existsSync(appJsonPath)) {
        console.log(`${colors.green}✅ app.json encontrado${colors.reset}`);
        return true;
    } else if (fs.existsSync(expoJsonPath)) {
        console.log(`${colors.green}✅ expo.json encontrado${colors.reset}`);
        return true;
    } else {
        console.log(`${colors.yellow}⚠️ Configuración de Expo no encontrada${colors.reset}`);
        return false;
    }
}

function checkExpoCLI() {
    try {
        const expoVersion = execSync('npx expo --version', { encoding: 'utf8' }).trim();
        console.log(`${colors.green}✅ Expo CLI disponible (${expoVersion})${colors.reset}`);
        return true;
    } catch (error) {
        console.log(`${colors.yellow}⚠️ Expo CLI no encontrado globalmente${colors.reset}`);
        console.log(`   Usa: npx expo start (recomendado)`);
        console.log(`   O instala globalmente: npm install -g @expo/cli`);
        return false;
    }
}

function printInstallationCommands() {
    console.log(`\n${colors.cyan}📦 Comandos de instalación rápida:${colors.reset}`);
    console.log(`
${colors.white}# Navegar al directorio móvil
cd MobileApp

# Instalar dependencias básicas
npm install

# Instalar dependencias adicionales necesarias
npm install expo-linear-gradient @expo/vector-icons
npm install @react-navigation/native @react-navigation/drawer
npm install react-native-gesture-handler react-native-safe-area-context

# Iniciar la aplicación
npx expo start${colors.reset}
    `);
}

function printRunCommands() {
    console.log(`\n${colors.cyan}🚀 Comandos para ejecutar la app:${colors.reset}`);
    console.log(`
${colors.white}# Método 1: Con Expo (Recomendado)
cd MobileApp
npx expo start

# Método 2: React Native CLI
npx react-native run-android    # Para Android
npx react-native run-ios        # Para iOS (solo macOS)

# Método 3: Desarrollo web
npx expo start --web${colors.reset}
    `);
}

function printTroubleshooting() {
    console.log(`\n${colors.cyan}🔧 Solución de problemas comunes:${colors.reset}`);
    console.log(`
${colors.white}# Limpiar caché
npm cache clean --force
rm -rf node_modules package-lock.json
npm install

# Metro bundler error
npx react-native start --reset-cache

# Expo no se conecta
expo start --tunnel

# Dependencias faltantes
npm install --legacy-peer-deps${colors.reset}
    `);
}

function main() {
    printBanner();
    
    console.log(`${colors.bold}🔍 Iniciando verificación del entorno móvil...${colors.reset}\n`);
    
    let allChecksPass = true;
    
    // Verificar Node.js
    if (!checkNodeVersion()) {
        allChecksPass = false;
    }
    
    // Verificar npm
    if (!checkNpmVersion()) {
        allChecksPass = false;
    }
    
    // Verificar directorio MobileApp
    const mobileAppPath = checkMobileAppDirectory();
    if (!mobileAppPath) {
        allChecksPass = false;
        console.log(`\n${colors.red}💀 No se puede continuar sin el directorio MobileApp${colors.reset}`);
        process.exit(1);
    }
    
    // Verificar package.json
    const packageJson = checkPackageJson(mobileAppPath);
    if (!packageJson) {
        allChecksPass = false;
    }
    
    // Verificar dependencias
    if (packageJson && !checkDependencies(packageJson)) {
        allChecksPass = false;
    }
    
    // Verificar node_modules
    if (!checkNodeModules(mobileAppPath)) {
        allChecksPass = false;
    }
    
    // Verificar configuración de Expo
    checkExpoConfiguration(mobileAppPath);
    
    // Verificar Expo CLI
    checkExpoCLI();
    
    // Resumen final
    console.log(`\n${colors.bold}📋 Resumen de verificación:${colors.reset}`);
    
    if (allChecksPass) {
        console.log(`${colors.green}🎉 ¡Todo listo para ejecutar la aplicación móvil!${colors.reset}`);
        printRunCommands();
    } else {
        console.log(`${colors.red}⚠️ Se detectaron algunos problemas que deben resolverse${colors.reset}`);
        printInstallationCommands();
        printTroubleshooting();
    }
    
    console.log(`\n${colors.cyan}📖 Para más información consulta el README.md${colors.reset}`);
}

// Ejecutar verificación
if (require.main === module) {
    main();
}