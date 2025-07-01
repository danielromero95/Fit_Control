# Gym Performance Analyzer - Script PowerShell para Windows 11
# Versión optimizada para PowerShell moderno

param(
    [string]$App = "launcher"
)

# Configuración de colores y estilo
$Host.UI.RawUI.BackgroundColor = "Black"
$Host.UI.RawUI.ForegroundColor = "White"
Clear-Host

Write-Host "🏋️  " -NoNewline -ForegroundColor Blue
Write-Host "GYM PERFORMANCE ANALYZER" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor DarkGray
Write-Host ""

# Función para mostrar mensajes con colores
function Show-Message {
    param([string]$Message, [string]$Type = "Info")
    
    switch ($Type) {
        "Success" { Write-Host "✅ " -NoNewline -ForegroundColor Green; Write-Host $Message -ForegroundColor White }
        "Error"   { Write-Host "❌ " -NoNewline -ForegroundColor Red; Write-Host $Message -ForegroundColor White }
        "Warning" { Write-Host "⚠️  " -NoNewline -ForegroundColor Yellow; Write-Host $Message -ForegroundColor White }
        "Info"    { Write-Host "ℹ️  " -NoNewline -ForegroundColor Blue; Write-Host $Message -ForegroundColor White }
        "Action"  { Write-Host "🚀 " -NoNewline -ForegroundColor Magenta; Write-Host $Message -ForegroundColor White }
    }
}

# Verificar PowerShell
if ($PSVersionTable.PSVersion.Major -lt 5) {
    Show-Message "Se requiere PowerShell 5.0 o superior" "Error"
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Verificar conda
Show-Message "Verificando conda..." "Info"
try {
    $condaVersion = & conda --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Show-Message "Conda encontrado: $condaVersion" "Success"
    } else {
        throw "Conda no encontrado"
    }
} catch {
    Show-Message "Conda no está instalado o no está en PATH" "Error"
    Show-Message "Descarga Anaconda desde: https://www.anaconda.com/products/distribution" "Info"
    
    # Ofrecer abrir el navegador
    $openBrowser = Read-Host "¿Quieres abrir el sitio de descarga? (s/n)"
    if ($openBrowser -eq "s" -or $openBrowser -eq "S") {
        Start-Process "https://www.anaconda.com/products/distribution"
    }
    
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Verificar entorno gym_env
Show-Message "Verificando entorno gym_env..." "Info"
try {
    $envList = & conda env list 2>$null | Select-String "gym_env"
    if ($envList) {
        Show-Message "Entorno gym_env encontrado" "Success"
    } else {
        Show-Message "Entorno gym_env no encontrado. Creando..." "Warning"
        
        if (Test-Path "environment.yml") {
            Show-Message "Creando entorno desde environment.yml..." "Action"
            & conda env create -f environment.yml
            if ($LASTEXITCODE -eq 0) {
                Show-Message "Entorno creado exitosamente" "Success"
            } else {
                Show-Message "Error creando el entorno" "Error"
                Read-Host "Presiona Enter para salir"
                exit 1
            }
        } else {
            Show-Message "Archivo environment.yml no encontrado" "Error"
            Read-Host "Presiona Enter para salir"
            exit 1
        }
    }
} catch {
    Show-Message "Error verificando entornos conda" "Error"
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Activar entorno
Show-Message "Activando entorno gym_env..." "Action"
& conda activate gym_env

# Función para ejecutar aplicaciones
function Start-GymApp {
    param([string]$AppType)
    
    switch ($AppType) {
        "launcher" {
            Show-Message "Iniciando Launcher gráfico..." "Action"
            if (Test-Path "launcher_windows.py") {
                python launcher_windows.py
            } else {
                Show-Message "launcher_windows.py no encontrado" "Error"
                return $false
            }
        }
        "gui" {
            Show-Message "Iniciando aplicación GUI de escritorio..." "Action"
            if (Test-Path "src/gui/main.py") {
                python src/gui/main.py
            } else {
                Show-Message "Aplicación GUI no encontrada" "Error"
                return $false
            }
        }
        "web" {
            Show-Message "Iniciando interfaz web Streamlit..." "Action"
            if (Test-Path "src/enhanced_app.py") {
                Show-Message "Abriendo en http://localhost:8501" "Info"
                Start-Process "http://localhost:8501"
                streamlit run src/enhanced_app.py --server.port=8501
            } else {
                Show-Message "Aplicación Streamlit no encontrada" "Error"
                return $false
            }
        }
        default {
            Show-Message "Tipo de aplicación no reconocido: $AppType" "Error"
            return $false
        }
    }
    return $true
}

# Menú interactivo si no se especifica app
if ($App -eq "launcher") {
    Write-Host ""
    Write-Host "SELECCIONA UNA APLICACIÓN:" -ForegroundColor Cyan
    Write-Host "1. 🖥️  Launcher gráfico (recomendado)" -ForegroundColor White
    Write-Host "2. 🖥️  Aplicación de escritorio (PyQt)" -ForegroundColor White
    Write-Host "3. 🌐 Interfaz web (Streamlit)" -ForegroundColor White
    Write-Host "4. ❌ Salir" -ForegroundColor White
    Write-Host ""
    
    do {
        $choice = Read-Host "Selecciona una opción (1-4)"
        switch ($choice) {
            "1" { 
                $result = Start-GymApp "launcher"
                break 
            }
            "2" { 
                $result = Start-GymApp "gui"
                break 
            }
            "3" { 
                $result = Start-GymApp "web"
                break 
            }
            "4" { 
                Show-Message "Saliendo..." "Info"
                exit 0 
            }
            default { 
                Show-Message "Opción no válida. Selecciona 1-4." "Warning"
            }
        }
    } while ($choice -notmatch '^[1-4]$')
} else {
    # Ejecutar app específica
    $result = Start-GymApp $App
}

# Mostrar resultado
if ($result) {
    Show-Message "Aplicación cerrada correctamente" "Success"
} else {
    Show-Message "Error ejecutando la aplicación" "Error"
}

Write-Host ""
Read-Host "Presiona Enter para salir"