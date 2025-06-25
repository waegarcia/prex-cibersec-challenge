#!/bin/bash
# Bash Script para instalar y ejecutar el agente en Linux

# Banner
echo "===================================================="
echo "   Agente de Información de Sistemas Prex - Configuración Linux      "
echo "===================================================="
echo

# Verificar si Python está instalado
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
    echo "Python detectado: $(python3 --version)"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
    echo "Python detectado: $(python --version)"
else
    echo "Python no está instalado. Intentando instalar..."
    
    # Detectar sistema operativo
    if command -v apt-get &>/dev/null; then
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip
        PYTHON_CMD="python3"
    elif command -v yum &>/dev/null; then
        sudo yum install -y python3 python3-pip
        PYTHON_CMD="python3"
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y python3 python3-pip
        PYTHON_CMD="python3"
    else
        echo "No se pudo detectar un gestor de paquetes compatible."
        echo "Por favor, instala Python 3.7+ manualmente."
        exit 1
    fi
fi

# Verificar si pip está disponible
if ! command -v pip3 &>/dev/null && ! command -v pip &>/dev/null; then
    echo "Pip no está disponible. Intentando instalar..."
    
    if command -v apt-get &>/dev/null; then
        sudo apt-get install -y python3-pip
    elif command -v yum &>/dev/null; then
        sudo yum install -y python3-pip
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y python3-pip
    else
        echo "No se pudo detectar un gestor de paquetes compatible."
        echo "Por favor, instala pip manualmente."
        exit 1
    fi
fi

# Determinar comando de pip
if command -v pip3 &>/dev/null; then
    PIP_CMD="pip3"
else
    PIP_CMD="pip"
fi

# Instalar dependencias requeridas
echo "Instalando dependencias..."
$PIP_CMD install psutil requests

# Verificar permisos de ejecución
if [ ! -x "system_info_agent.py" ]; then
    chmod +x system_info_agent.py
fi

# Ejecutar el script
echo "Ejecutando el agente..."
$PYTHON_CMD system_info_agent.py

echo "Completado!"
