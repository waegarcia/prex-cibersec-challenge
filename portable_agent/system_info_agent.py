#!/usr/bin/env python3
"""
Agente Portable de Información del Sistema
---------------------------------
Este script independiente recopila información del sistema y la envía a una API de recolección.
Funciona tanto en plataformas Windows como Linux sin dependencias externas.

Uso:
  python system_info_agent.py

No se requieren argumentos. La URL de la API está preconfigurada en el script.
"""

import sys
import subprocess
import platform

# URL de la API de recolección
API_URL = "http://52.14.229.100:5000"

# Clave para autenticación con la API
API_SECRET = "8VarhXGAwTAlR7QV0UXhG3fZHWkB3O7h"

# Opcional: Modo silencioso (True = sin mensajes, False = mostrar mensajes)
QUIET_MODE = False

def ensure_dependencies():
    """Asegurar que todas las dependencias requeridas están instaladas."""
    try:
        # Verificar si necesitamos instalar dependencias
        try:
            import psutil
            import requests
        except ImportError:
            print("Instalando dependencias requeridas...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil", "requests"])
            print("Dependencias instaladas correctamente.")
    except Exception as e:
        print(f"Error al instalar las dependencias: {e}")
        print("Por favor, instala manualmente las dependencias requeridas:")
        print("pip install psutil requests")
        sys.exit(1)


# Asegurar que las dependencias estén instaladas antes de continuar
ensure_dependencies()

# Ahora podemos importar las dependencias
import socket
from datetime import datetime, timezone
import psutil
import requests
from typing import Dict, List, Any


class SystemInfoAgent:
    def __init__(self, api_url: str):
        """
        Inicializar el agente con la URL de la API.
        
        Args:
            api_url: URL del endpoint de la API para enviar datos
        """
        self.api_url = api_url
        self.system_ip = self._get_ip_address()
        
    def _get_ip_address(self) -> str:
        """Obtener la dirección IP principal del sistema."""
        try:
            # Esto crea un socket que no se conecta realmente a ningún sitio
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Esto indica al socket que se conecte a una IP pública, pero no se establece ninguna conexión
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return socket.gethostbyname(socket.gethostname())
    
    def get_processor_info(self) -> Dict[str, Any]:
        """Recopilar información del procesador."""
        cpu_info = {
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "cpu_freq": {
                "current": getattr(psutil.cpu_freq(), "current", 0),
                "min": getattr(psutil.cpu_freq(), "min", 0),
                "max": getattr(psutil.cpu_freq(), "max", 0)
            },
            "architecture": platform.machine(),
            "processor": platform.processor()
        }
        return cpu_info
    
    def get_running_processes(self) -> List[Dict[str, Any]]:
        """Recopilar información sobre los procesos en ejecución."""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'cpu_percent']):
            try:
                proc_info = proc.info
                processes.append({
                    "pid": proc_info["pid"],
                    "name": proc_info["name"],
                    "username": proc_info["username"],
                    "memory_percent": round(proc_info["memory_percent"], 2),
                    "cpu_percent": proc_info["cpu_percent"]
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return processes
    
    def get_logged_in_users(self) -> List[Dict[str, Any]]:
        """Obtener usuarios con sesiones abiertas."""
        users = []
        for user in psutil.users():
            users.append({
                "username": user.name,
                "terminal": user.terminal,
                "host": user.host,
                "started": datetime.datetime.fromtimestamp(user.started, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            })
        return users
    
    def get_os_info(self) -> Dict[str, str]:
        """Obtener nombre y versión del sistema operativo."""
        os_info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "platform": platform.platform()
        }
        return os_info
    
    def collect_all_info(self) -> Dict[str, Any]:
        """Recopilar toda la información del sistema."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        
        all_info = {
            "ip_address": self.system_ip,
            "timestamp": timestamp,
            "processor": self.get_processor_info(),
            "processes": self.get_running_processes(),
            "logged_in_users": self.get_logged_in_users(),
            "os_info": self.get_os_info()
        }
        
        return all_info
    
    def send_to_api(self, data: Dict[str, Any]) -> Dict:
        """
        Enviar datos recopilados a la API.
        
        Args:
            data: Información del sistema recopilada
            
        Returns:
            Respuesta de la API como diccionario
        """
        try:
            # Incluir la clave API en los encabezados para autenticación
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"ApiKey {API_SECRET}"
            }
            
            response = requests.post(
                f"{self.api_url}/collect",
                json=data,
                headers=headers
            )
            return {"status_code": response.status_code, "response": response.json()}
        except requests.RequestException as e:
            return {"status_code": -1, "error": str(e)}


def main():
    """Función principal para ejecutar el agente."""
    # Usar configuración global en lugar de argumentos de línea de comandos
    quiet_mode = QUIET_MODE
    api_url = API_URL
    
    # Crear una estructura de argumentos predeterminada
    args = type('Args', (), {'quiet': quiet_mode})()
    
    # Permitir anular la configuración con argumentos si se proporcionan
    if len(sys.argv) > 1:
        try:
            import argparse
            parser = argparse.ArgumentParser(description="Agente Portable de Información del Sistema")
            parser.add_argument(
                "--api", 
                type=str,
                help="URL del endpoint API (sobrescribe el valor predeterminado)"
            )
            parser.add_argument(
                "--quiet",
                action="store_true",
                help="Ejecutar en modo silencioso con salida mínima"
            )
            args, _ = parser.parse_known_args()
            
            if args.api:
                api_url = args.api
            if args.quiet:
                quiet_mode = True
                args.quiet = True
        except ImportError:
            # Si argparse no está disponible, ignoramos los argumentos
            pass
    
    # Mostrar banner a menos que estemos en modo silencioso
    if not quiet_mode:
        print("=" * 70)
        print("Agente Portable de Información del Sistema")
        print("=" * 70)
        print(f"Ejecutando en: {platform.system()} {platform.release()}")
        print("-" * 70)
    
    # Inicializar y recopilar datos
    agent = SystemInfoAgent(api_url)
    system_data = agent.collect_all_info()
    
    # Enviar datos a la API
    if not quiet_mode:
        print(f"Enviando datos a la API: {api_url}")
        
    response = agent.send_to_api(system_data)
    
    if response["status_code"] in [200, 201]:
        if not quiet_mode:
            print("Datos enviados correctamente a la API")
    else:
        if not quiet_mode:
            print(f"Error al enviar datos: {response.get('error', response)}")
            print("Falló el envío de datos a la API. Por favor, verifica la URL de la API e inténtalo de nuevo.")
            print(f"URL de la API: {api_url}")
            print(f"Detalles del error: {response}")
        return 1  # Devolver código de error

    # Imprimir resumen de los datos recopilados si no estamos en modo silencioso
    if not args.quiet:
        print("\nResumen de Información del Sistema:")
        print(f"Dirección IP: {system_data['ip_address']}")
        print(f"Sistema Operativo: {system_data['os_info']['system']} {system_data['os_info']['release']}")
        print(f"Procesador: {system_data['processor']['processor']}")
        print(f"Número de Procesos: {len(system_data['processes'])}")
        print(f"Usuarios Conectados: {', '.join([user['username'] for user in system_data['logged_in_users']])}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
