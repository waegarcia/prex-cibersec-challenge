# PowerShell Script para instalar y ejecutar el agente en Windows

# Banner
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "   Agente de Información de Sistemas Prex - Configuración Windows    " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host

# Verificar si Python está instalado
try {
    $pythonVersion = python --version
    Write-Host "Python detectado: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "Python no está instalado o no está en el PATH." -ForegroundColor Red
    Write-Host "Por favor instala Python 3.7+ desde https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

# Verificar si pip está disponible
try {
    $pipVersion = python -m pip --version
    Write-Host "Pip detectado: $pipVersion" -ForegroundColor Green
}
catch {
    Write-Host "Pip no está disponible." -ForegroundColor Red
    Write-Host "Instalando pip..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest https://bootstrap.pypa.io/get-pip.py -OutFile get-pip.py
        python get-pip.py
        Remove-Item get-pip.py
    }
    catch {
        Write-Host "No se pudo instalar pip. Por favor instálalo manualmente." -ForegroundColor Red
        exit 1
    }
}

# Instalar dependencias requeridas
Write-Host "Instalando dependencias..." -ForegroundColor Yellow
python -m pip install psutil requests

# Ejecutar el script
Write-Host "Ejecutando el agente..." -ForegroundColor Green
python system_info_agent.py

Write-Host "Completado!" -ForegroundColor Green
