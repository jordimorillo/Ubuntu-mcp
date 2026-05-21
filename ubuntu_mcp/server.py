#!/usr/bin/env python3
"""
Servidor MCP para control de Ubuntu con automatización de GUI.
Proporciona herramientas para control del sistema, archivos, captura de pantalla,
mouse, teclado y gestión de procesos.
"""

import asyncio
import os
import subprocess
import json
import base64
from pathlib import Path
from typing import Any
import io

import pyautogui
import psutil
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent


# Configurar PyAutoGUI
pyautogui.FAILSAFE = True  # Mover el mouse a la esquina superior izquierda aborta
pyautogui.PAUSE = 0.1  # Pausa entre acciones


# Crear servidor MCP
app = Server("ubuntu-control")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Lista todas las herramientas disponibles."""
    return [
        # Herramientas del sistema
        Tool(
            name="execute_command",
            description="Ejecuta un comando de shell en Ubuntu. Devuelve stdout, stderr y código de salida.",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Comando a ejecutar"
                    },
                    "cwd": {
                        "type": "string",
                        "description": "Directorio de trabajo (opcional)"
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Timeout en segundos (default: 30)"
                    }
                },
                "required": ["command"]
            }
        ),
        Tool(
            name="get_system_info",
            description="Obtiene información del sistema: CPU, memoria, disco, red, etc.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        
        # Herramientas de archivos
        Tool(
            name="read_file",
            description="Lee el contenido de un archivo",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Ruta del archivo a leer"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="write_file",
            description="Escribe contenido en un archivo (crea o sobreescribe)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Ruta del archivo"
                    },
                    "content": {
                        "type": "string",
                        "description": "Contenido a escribir"
                    }
                },
                "required": ["path", "content"]
            }
        ),
        Tool(
            name="delete_file",
            description="Elimina un archivo o directorio",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Ruta del archivo o directorio a eliminar"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Si es directorio, eliminar recursivamente"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="list_directory",
            description="Lista el contenido de un directorio",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Ruta del directorio"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="file_exists",
            description="Verifica si un archivo o directorio existe",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Ruta a verificar"
                    }
                },
                "required": ["path"]
            }
        ),
        
        # Herramientas de captura de pantalla
        Tool(
            name="screenshot",
            description="Captura la pantalla completa o una región específica. Devuelve la imagen en base64.",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {
                        "type": "object",
                        "description": "Región a capturar (x, y, width, height). Si se omite, captura toda la pantalla",
                        "properties": {
                            "x": {"type": "number"},
                            "y": {"type": "number"},
                            "width": {"type": "number"},
                            "height": {"type": "number"}
                        }
                    },
                    "save_path": {
                        "type": "string",
                        "description": "Ruta opcional para guardar la imagen"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_screen_size",
            description="Obtiene la resolución de la pantalla",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        
        # Herramientas de mouse
        Tool(
            name="mouse_click",
            description="Hace click en una posición específica de la pantalla",
            inputSchema={
                "type": "object",
                "properties": {
                    "x": {
                        "type": "number",
                        "description": "Coordenada X"
                    },
                    "y": {
                        "type": "number",
                        "description": "Coordenada Y"
                    },
                    "button": {
                        "type": "string",
                        "enum": ["left", "right", "middle"],
                        "description": "Botón del mouse (default: left)"
                    },
                    "clicks": {
                        "type": "number",
                        "description": "Número de clicks (default: 1)"
                    }
                },
                "required": ["x", "y"]
            }
        ),
        Tool(
            name="mouse_move",
            description="Mueve el cursor a una posición específica",
            inputSchema={
                "type": "object",
                "properties": {
                    "x": {
                        "type": "number",
                        "description": "Coordenada X"
                    },
                    "y": {
                        "type": "number",
                        "description": "Coordenada Y"
                    },
                    "duration": {
                        "type": "number",
                        "description": "Duración del movimiento en segundos (default: 0)"
                    }
                },
                "required": ["x", "y"]
            }
        ),
        Tool(
            name="get_mouse_position",
            description="Obtiene la posición actual del cursor",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        
        # Herramientas de teclado
        Tool(
            name="type_text",
            description="Escribe texto simulando el teclado",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Texto a escribir"
                    },
                    "interval": {
                        "type": "number",
                        "description": "Intervalo entre teclas en segundos (default: 0)"
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="press_key",
            description="Presiona una tecla o combinación de teclas. Ejemplos: 'enter', 'ctrl', 'a', etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Tecla a presionar (enter, tab, ctrl, alt, shift, etc.)"
                    },
                    "presses": {
                        "type": "number",
                        "description": "Número de veces a presionar (default: 1)"
                    }
                },
                "required": ["key"]
            }
        ),
        Tool(
            name="hotkey",
            description="Ejecuta un atajo de teclado. Ejemplo: ['ctrl', 'c'] para copiar",
            inputSchema={
                "type": "object",
                "properties": {
                    "keys": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Lista de teclas a presionar simultáneamente"
                    }
                },
                "required": ["keys"]
            }
        ),
        
        # Herramientas de procesos
        Tool(
            name="list_processes",
            description="Lista los procesos en ejecución",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "number",
                        "description": "Número máximo de procesos a listar (default: 50)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="kill_process",
            description="Termina un proceso por su PID",
            inputSchema={
                "type": "object",
                "properties": {
                    "pid": {
                        "type": "number",
                        "description": "ID del proceso"
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Forzar terminación (SIGKILL)"
                    }
                },
                "required": ["pid"]
            }
        ),

        # Herramientas de ventanas
        Tool(
            name="list_windows",
            description="Lista las ventanas abiertas del sistema",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_active_window",
            description="Obtiene información de la ventana activa actual",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="switch_to_window",
            description="Cambia a una ventana específica por su título o nombre",
            inputSchema={
                "type": "object",
                "properties": {
                    "window_name": {
                        "type": "string",
                        "description": "Nombre o parte del título de la ventana"
                    }
                },
                "required": ["window_name"]
            }
        ),
        Tool(
            name="switch_to_next_window",
            description="Cambia a la siguiente ventana del sistema",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent | ImageContent]:
    """Maneja las llamadas a las herramientas."""
    
    try:
        # Herramientas del sistema
        if name == "execute_command":
            command = arguments["command"]
            cwd = arguments.get("cwd")
            timeout = arguments.get("timeout", 30)
            
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }, indent=2)
            )]
        
        elif name == "get_system_info":
            info = {
                "cpu": {
                    "percent": psutil.cpu_percent(interval=1),
                    "count": psutil.cpu_count(),
                    "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                },
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent,
                    "used": psutil.virtual_memory().used
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "used": psutil.disk_usage('/').used,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent
                },
                "network": psutil.net_io_counters()._asdict(),
                "boot_time": psutil.boot_time()
            }
            
            return [TextContent(type="text", text=json.dumps(info, indent=2))]
        
        # Herramientas de archivos
        elif name == "read_file":
            path = Path(arguments["path"]).expanduser()
            content = path.read_text()
            return [TextContent(type="text", text=content)]
        
        elif name == "write_file":
            path = Path(arguments["path"]).expanduser()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(arguments["content"])
            return [TextContent(type="text", text=f"Archivo escrito: {path}")]
        
        elif name == "delete_file":
            path = Path(arguments["path"]).expanduser()
            if path.is_dir():
                if arguments.get("recursive", False):
                    import shutil
                    shutil.rmtree(path)
                else:
                    path.rmdir()
            else:
                path.unlink()
            return [TextContent(type="text", text=f"Eliminado: {path}")]
        
        elif name == "list_directory":
            path = Path(arguments["path"]).expanduser()
            items = []
            for item in path.iterdir():
                items.append({
                    "name": item.name,
                    "path": str(item),
                    "is_dir": item.is_dir(),
                    "size": item.stat().st_size if item.is_file() else None
                })
            return [TextContent(type="text", text=json.dumps(items, indent=2))]
        
        elif name == "file_exists":
            path = Path(arguments["path"]).expanduser()
            exists = path.exists()
            return [TextContent(type="text", text=json.dumps({
                "exists": exists,
                "is_file": path.is_file() if exists else None,
                "is_dir": path.is_dir() if exists else None
            }))]
        
        # Herramientas de captura de pantalla
        elif name == "screenshot":
            region = arguments.get("region")
            save_path = arguments.get("save_path") or "/tmp/screenshot.png"
            
            # Intentar con grim (Wayland) primero
            try:
                if region:
                    subprocess.run([
                        "grim", "-g",
                        f"{region['x']},{region['y']} {region['width']}x{region['height']}",
                        save_path
                    ], check=True)
                else:
                    subprocess.run(["grim", save_path], check=True)
            except Exception:
                # Fallback a pyautogui (X11)
                if region:
                    screenshot = pyautogui.screenshot(
                        region=(region["x"], region["y"], region["width"], region["height"])
                    )
                else:
                    screenshot = pyautogui.screenshot()
                screenshot.save(save_path)
            
            with open(save_path, "rb") as f:
                img_base64 = base64.b64encode(f.read()).decode()
            
            return [
                ImageContent(
                    type="image",
                    data=img_base64,
                    mimeType="image/png"
                )
            ]
        
        elif name == "get_screen_size":
            size = pyautogui.size()
            return [TextContent(type="text", text=json.dumps({
                "width": size.width,
                "height": size.height
            }))]
        
        # Herramientas de mouse
        elif name == "mouse_click":
            x = arguments["x"]
            y = arguments["y"]
            button = arguments.get("button", "left")
            clicks = arguments.get("clicks", 1)
            
            pyautogui.click(x, y, clicks=clicks, button=button)
            return [TextContent(type="text", text=f"Click en ({x}, {y}) con botón {button}")]
        
        elif name == "mouse_move":
            x = arguments["x"]
            y = arguments["y"]
            duration = arguments.get("duration", 0)
            
            pyautogui.moveTo(x, y, duration=duration)
            return [TextContent(type="text", text=f"Cursor movido a ({x}, {y})")]
        
        elif name == "get_mouse_position":
            pos = pyautogui.position()
            return [TextContent(type="text", text=json.dumps({
                "x": pos.x,
                "y": pos.y
            }))]
        
        # Herramientas de teclado
        elif name == "type_text":
            text = arguments["text"]
            interval = arguments.get("interval", 0)
            
            pyautogui.write(text, interval=interval)
            return [TextContent(type="text", text=f"Texto escrito: {text[:50]}...")]
        
        elif name == "press_key":
            key = arguments["key"]
            presses = arguments.get("presses", 1)
            
            pyautogui.press(key, presses=presses)
            return [TextContent(type="text", text=f"Tecla presionada: {key}")]
        
        elif name == "hotkey":
            keys = arguments["keys"]
            pyautogui.hotkey(*keys)
            return [TextContent(type="text", text=f"Atajo ejecutado: {'+'.join(keys)}")]
        
        # Herramientas de procesos
        elif name == "list_processes":
            limit = arguments.get("limit", 50)
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Ordenar por uso de CPU
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            processes = processes[:limit]
            
            return [TextContent(type="text", text=json.dumps(processes, indent=2))]
        
        elif name == "kill_process":
            pid = arguments["pid"]
            force = arguments.get("force", False)
            
            process = psutil.Process(pid)
            if force:
                process.kill()
            else:
                process.terminate()
            
            return [TextContent(type="text", text=f"Proceso {pid} terminado")]
        
        # Herramientas de ventanas
        elif name == "list_windows":
            result = subprocess.run(
                ["xdotool", "search", "--name", "."],
                capture_output=True,
                text=True
            )
            window_ids = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
            windows = []
            for wid in window_ids:
                name_result = subprocess.run(
                    ["xdotool", "getwindowname", wid],
                    capture_output=True,
                    text=True
                )
                title = name_result.stdout.strip()
                if title:
                    windows.append({
                        "id": wid,
                        "title": title
                    })
            return [TextContent(type="text", text=json.dumps(windows, indent=2))]
        
        elif name == "get_active_window":
            result = subprocess.run(
                ["xdotool", "getactivewindow", "getwindowname"],
                capture_output=True,
                text=True
            )
            active_id = subprocess.run(
                ["xdotool", "getactivewindow"],
                capture_output=True,
                text=True
            )
            return [TextContent(type="text", text=json.dumps({
                "id": active_id.stdout.strip(),
                "title": result.stdout.strip()
            }, indent=2))]
        
        elif name == "switch_to_window":
            window_name = arguments["window_name"]
            result = subprocess.run(
                ["xdotool", "search", "--name", window_name],
                capture_output=True,
                text=True
            )
            window_ids = [wid.strip() for wid in result.stdout.strip().split('\n') if wid.strip()]
            if window_ids:
                subprocess.run(["xdotool", "windowactivate", "--sync", window_ids[0]])
                return [TextContent(type="text", text=f"Cambiado a ventana: {window_name}")]
            return [TextContent(type="text", text=f"No se encontró ventana: {window_name}")]
        
        elif name == "switch_to_next_window":
            subprocess.run(["xdotool", "key", "alt+Tab"])
            return [TextContent(type="text", text="Cambiado a siguiente ventana")]
        
        else:
            return [TextContent(type="text", text=f"Herramienta desconocida: {name}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Punto de entrada principal."""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def main_sync():
    """Wrapper síncrono para el entry point."""
    asyncio.run(main())

if __name__ == "__main__":
    main_sync()
