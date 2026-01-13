# Ubuntu MCP Server

Servidor MCP (Model Context Protocol) para control completo de Ubuntu, incluyendo automatización de GUI.

## Características

- 🖥️ **Control del Sistema**: Ejecutar comandos, obtener información del sistema
- 📁 **Gestión de Archivos**: Leer, escribir, eliminar, listar archivos y directorios
- 📸 **Captura de Pantalla**: Tomar screenshots de toda la pantalla o áreas específicas
- 🖱️ **Control de Mouse**: Hacer click en coordenadas específicas, obtener posición
- ⌨️ **Control de Teclado**: Simular pulsaciones de teclas y atajos
- 🔄 **Gestión de Procesos**: Listar y gestionar procesos del sistema

## Instalación

```bash
# Instalar dependencias del sistema (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y python3-tk python3-dev scrot

# Instalar el servidor
pip install -e .
```

## Configuración en Claude Desktop

Añade esto a tu configuración de Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json` en macOS o `%APPDATA%/Claude/claude_desktop_config.json` en Windows):

```json
{
  "mcpServers": {
    "ubuntu-control": {
      "command": "python",
      "args": ["-m", "ubuntu_mcp.server"]
    }
  }
}
```

En Linux, el archivo de configuración está en `~/.config/Claude/claude_desktop_config.json`

## Herramientas Disponibles

### Sistema
- `execute_command`: Ejecutar comandos de shell
- `get_system_info`: Obtener información del sistema (CPU, memoria, disco, etc.)

### Archivos
- `read_file`: Leer contenido de un archivo
- `write_file`: Escribir contenido en un archivo
- `delete_file`: Eliminar archivo o directorio
- `list_directory`: Listar contenido de un directorio
- `file_exists`: Verificar si un archivo/directorio existe

### Captura de Pantalla
- `screenshot`: Capturar toda la pantalla o región específica
- `get_screen_size`: Obtener resolución de la pantalla

### Control de Mouse
- `mouse_click`: Hacer click en coordenadas específicas
- `mouse_move`: Mover el cursor a una posición
- `get_mouse_position`: Obtener posición actual del cursor

### Control de Teclado
- `type_text`: Escribir texto
- `press_key`: Presionar una tecla o combinación de teclas
- `hotkey`: Ejecutar atajo de teclado

### Procesos
- `list_processes`: Listar procesos en ejecución
- `kill_process`: Terminar un proceso por PID

## Uso

Una vez configurado, puedes pedirle a Claude que:

- "Toma una captura de pantalla"
- "Haz click en la posición (500, 300)"
- "Escribe 'Hola mundo' en el teclado"
- "Presiona Ctrl+C"
- "Lista los archivos en /home/user/Documents"
- "Ejecuta el comando 'ls -la'"
- "Muéstrame el uso de CPU y memoria"

## Seguridad

⚠️ **ADVERTENCIA**: Este servidor tiene acceso completo al sistema. Úsalo solo en entornos seguros y de confianza.

## Licencia

MIT
