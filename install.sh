#!/bin/bash
# Script de instalación para Ubuntu MCP Server

echo "=== Instalando Ubuntu MCP Server ==="

# Instalar dependencias del sistema
echo "Instalando dependencias del sistema..."
sudo apt-get update
sudo apt-get install -y python3-tk python3-dev scrot xdotool

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias de Python
echo "Instalando dependencias de Python..."
pip install --upgrade pip
pip install -e .

echo ""
echo "=== Instalación completada ==="
echo ""
echo "Para usar el servidor, añade esta configuración a Claude Desktop:"
echo ""
echo '{
  "mcpServers": {
    "ubuntu-control": {
      "command": "'$(pwd)'/venv/bin/python",
      "args": ["-m", "ubuntu_mcp.server"]
    }
  }
}'
echo ""
echo "Archivo de configuración en Linux: ~/.config/Claude/claude_desktop_config.json"
