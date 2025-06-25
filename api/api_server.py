#!/usr/bin/env python3
"""
API de Recolección de Información de Sistemas
------------------------------------------------------
Servidor API que recibe información de sistema desde agentes y almacena en una base de datos PostgreSQL.
- Almacena datos en una base de datos relacional normalizada
- Proporciona capacidades avanzadas de consulta
"""

from flask import Flask, request, jsonify
import os
import json
import datetime
from datetime import timezone
from pathlib import Path
from typing import Dict, Any, List
import logging
from functools import wraps
from dotenv import load_dotenv

# Cargar variables de entorno (.env)
load_dotenv()

# Importar modelos ORM
from models import db, Server, OSInfo, ProcessorInfo, Process, LoggedUser

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/sysinfo')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuración de seguridad
API_SECRET = os.getenv('API_SECRET', 'default-insecure-key')
if API_SECRET == 'default-insecure-key':
    logger.warning("Estás usando una clave API predeterminada e insegura. Define API_SECRET en el archivo .env.")

# Función de verificación de API Key
def verify_api_key():
    """
    Verificar si la solicitud contiene una API Key válida.
    
    Returns:
        bool: True si la API Key es válida, False en caso contrario
    """
    api_key = request.headers.get('Authorization')
    if not api_key or not api_key.startswith('ApiKey ') or api_key.replace('ApiKey ', '') != API_SECRET:
        return False
    return True

# Función para generar respuesta de error de autenticación
def auth_error_response():
    """
    Generar una respuesta de error cuando falla la autenticación.
    
    Returns:
        tuple: Respuesta JSON con error 401
    """
    logger.warning(f"Intento de acceso no autorizado al endpoint {request.endpoint} desde {request.remote_addr}")
    return jsonify({"error": "No autorizado. Se requiere una clave API válida."}), 401

# Inicializar la base de datos con la aplicación
db.init_app(app)

# Directorio para almacenamiento de archivos JSON
DATA_DIR = Path("./data")


def setup_app():
    """Configuración inicial de la aplicación."""
    DATA_DIR.mkdir(exist_ok=True)
    
    # Crear tablas si no existen
    with app.app_context():
        db.create_all()
        logger.info("Tablas de base de datos creadas o verificadas")


def get_filename_for_ip(ip_address: str) -> str:
    """
    Genera el nombre de archivo para almacenar datos para una dirección IP dada.
    
    Args:
        ip_address: Dirección IP del agente
        
    Returns:
        Nombre de archivo en formato <IP>_<YYYY-MM-DD>.json
    """
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    return f"{ip_address}_{today}.json"


def store_data_in_file(data: Dict[str, Any]) -> bool:
    """
    Almacena datos en un archivo JSON
    
    Args:
        data: Datos de información del sistema
        
    Returns:
        True si tiene éxito, False en caso contrario
    """
    try:
        ip_address = data.get("ip_address", "unknown")
        filename = DATA_DIR / get_filename_for_ip(ip_address)
        
        # Si el archivo existe, lo lee y agrega nuevos datos
        if filename.exists():
            with open(filename, 'r') as f:
                try:
                    existing_data = json.load(f)
                    if isinstance(existing_data, dict):
                        # Convertir un registro en una lista
                        existing_data = [existing_data]
                    elif not isinstance(existing_data, list):
                        existing_data = []
                except json.JSONDecodeError:
                    existing_data = []
            
            # Agrega nuevos datos
            existing_data.append(data)
            file_data = existing_data
        else:
            # Nuevo archivo, almacena como un solo registro
            file_data = [data]
            
        # Escribe datos en archivo
        with open(filename, 'w') as f:
            json.dump(file_data, f, indent=2)
            
        return True
    except Exception as e:
        logger.error(f"Error al almacenar datos en archivo: {e}")
        return False


def store_data_in_db(data: Dict[str, Any]) -> bool:
    """
    Almacena la información del sistema en la base de datos.
    
    Args:
        data: Datos de información del sistema
        
    Returns:
        True si tiene éxito, False en caso contrario
    """
    try:
        ip_address = data.get("ip_address", "unknown")
        timestamp = datetime.datetime.fromisoformat(data.get("timestamp", datetime.datetime.now().isoformat()))
        
        # Buscar o crear el servidor
        server = Server.query.filter_by(ip_address=ip_address).first()
        if not server:
            server = Server(ip_address=ip_address, first_seen=timestamp, last_seen=timestamp)
            db.session.add(server)
        else:
            server.last_seen = timestamp
        
        # Guardar información del S.O.
        if "os_info" in data and data["os_info"]:
            os_info = OSInfo(
                server=server,
                timestamp=timestamp,
                system=data["os_info"].get("system"),
                release=data["os_info"].get("release"),
                version=data["os_info"].get("version"),
                platform=data["os_info"].get("platform")
            )
            db.session.add(os_info)
        
        # Guardar información del procesador
        if "processor" in data and data["processor"]:
            processor_info = ProcessorInfo(
                server=server,
                timestamp=timestamp,
                cpu_count=data["processor"].get("cpu_count"),
                model=data["processor"].get("model"),
                cpu_percent=data["processor"].get("cpu_percent", 0.0)
            )
            db.session.add(processor_info)
        
        # Guardar procesos
        if "processes" in data and isinstance(data["processes"], list):
            for proc_data in data["processes"]:
                process = Process(
                    server=server,
                    timestamp=timestamp,
                    pid=proc_data.get("pid", 0),
                    name=proc_data.get("name", "unknown"),
                    username=proc_data.get("username")
                )
                db.session.add(process)
        
        # Guardar usuarios conectados
        if "logged_in_users" in data and isinstance(data["logged_in_users"], list):
            for user_data in data["logged_in_users"]:
                logged_user = LoggedUser(
                    server=server,
                    timestamp=timestamp,
                    username=user_data.get("username", "unknown"),
                    terminal=user_data.get("terminal"),
                    host=user_data.get("host")
                )
                db.session.add(logged_user)
        
        # Commit a la base de datos
        db.session.commit()
        return True
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al almacenar datos en base de datos: {e}")
        return False


def find_data_for_ip_in_db(ip_address: str) -> Dict[str, Any]:
    """
    Busca datos para una dirección IP específica en la base de datos.
    
    Args:
        ip_address: Dirección IP para consultar
        
    Returns:
        Diccionario con información del servidor y datos históricos
    """
    try:
        server = Server.query.filter_by(ip_address=ip_address).first()
        if not server:
            return None
        
        # Construir respuesta con toda la información
        result = server.to_dict(include_relations=True)
        
        # Últimos 20 procesos
        latest_processes = Process.query.filter_by(server_id=server.id).order_by(
            Process.timestamp.desc()
        ).limit(100).all()
        
        if latest_processes:
            # Agrupamos por timestamp para mostrar los procesos en cada punto de tiempo
            processes_by_time = {}
            for proc in latest_processes:
                ts_key = proc.timestamp.isoformat()
                if ts_key not in processes_by_time:
                    processes_by_time[ts_key] = []
                processes_by_time[ts_key].append(proc.to_dict())
            
            result['latest_processes'] = processes_by_time
        
        # Últimos usuarios conectados
        latest_users = LoggedUser.query.filter_by(server_id=server.id).order_by(
            LoggedUser.timestamp.desc()
        ).limit(100).all()
        
        if latest_users:
            # Agrupamos por timestamp
            users_by_time = {}
            for user in latest_users:
                ts_key = user.timestamp.isoformat()
                if ts_key not in users_by_time:
                    users_by_time[ts_key] = []
                users_by_time[ts_key].append(user.to_dict())
            
            result['latest_users'] = users_by_time
        
        return result
    
    except Exception as e:
        logger.error(f"Error al consultar base de datos: {e}")
        return None


def find_data_for_ip_in_files(ip_address: str) -> List[Dict[str, Any]]:
    """
    Busca todos los datos para una dirección IP dada en archivos JSON
    
    Args:
        ip_address: Dirección IP a buscar
        
    Returns:
        Lista de registros de datos para la IP
    """
    results = []
    
    try:
        # Busca todos los archivos que puedan contener datos para esta IP
        file_pattern = f"{ip_address}_*.json"
        for file_path in DATA_DIR.glob(file_pattern):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        results.extend(data)
                    elif isinstance(data, dict):
                        results.append(data)
            except json.JSONDecodeError:
                logger.warning(f"No se pudo analizar el archivo JSON: {file_path}")
            except Exception as e:
                logger.error(f"Error al leer el archivo {file_path}: {e}")
    except Exception as e:
        logger.error(f"Error al buscar archivos: {e}")
    
    return results


@app.route('/collect', methods=['POST'])
def collect_data():
    """Endpoint para recolectar información del sistema desde los agentes."""
    # Verificar autenticación
    if not verify_api_key():
        return auth_error_response()
        
    if not request.is_json:
        return jsonify({"status": "error", "message": "La solicitud debe ser JSON"}), 400
    
    data = request.get_json()
    
    # Validar campos requeridos
    required_fields = ["ip_address", "processor", "processes", "logged_in_users", "os_info"]
    for field in required_fields:
        if field not in data:
            return jsonify({"status": "error", "message": f"Campo requerido faltante: {field}"}), 400
    
    # Agrega timestamp si no está presente
    if "timestamp" not in data:
        data["timestamp"] = datetime.datetime.now(timezone.utc).isoformat()
    
    # Almacena en base de datos
    db_result = store_data_in_db(data)
    
    # Almacena en archivo
    file_result = store_data_in_file(data)
    
    if db_result or file_result:
        return jsonify({"status": "success", "message": "Datos almacenados correctamente"}), 201
    else:
        return jsonify({"status": "error", "message": "Error al almacenar datos"}), 500


@app.route('/query/<ip_address>', methods=['GET'])
def query_data(ip_address):
    """
    Endpoint para consultar datos para una dirección IP específica.
    
    Args:
        ip_address: Dirección IP para consultar
    """
    # Intentar obtener datos de la base de datos (forma preferida)
    db_results = find_data_for_ip_in_db(ip_address)
    
    if db_results:
        return jsonify({"status": "success", "data": db_results}), 200
    
    # Fallback a los archivos JSON si no hay datos en la base de datos
    file_results = find_data_for_ip_in_files(ip_address)
    
    if file_results:
        return jsonify({"status": "success", "data": file_results}), 200
    
    # No hay datos en ninguna fuente
    return jsonify({"status": "error", "message": f"No se encontraron datos para la IP: {ip_address}"}), 404


@app.route('/servers', methods=['GET'])
def list_servers():
    """Endpoint para listar todos los servidores monitoreados."""
    try:
        servers = Server.query.all()
        result = [server.to_dict() for server in servers]
        return jsonify({"status": "success", "servers": result}), 200
    except Exception as e:
        logger.error(f"Error al listar servidores: {e}")
        return jsonify({"status": "error", "message": "Error al listar servidores"}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de verificación del sistema"""
    db_status = "ok"
    
    # Verificar conexión a la base de datos
    try:
        from sqlalchemy import text
        db.session.execute(text("SELECT 1"))
        db.session.commit()
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return jsonify({
        "status": "ok", 
        "message": "API en ejecución",
        "database": db_status,
        "timestamp": datetime.datetime.now(timezone.utc).isoformat()
    }), 200


@app.route('/', methods=['GET'])
def root():
    """Endpoint raíz con información de la API."""
    return jsonify({
        "name": "API de Recolección de Información de Sistemas",
        "version": "2.0.0",
        "database_support": True,
        "endpoints": {
            "/collect": "POST - Enviar datos de información del sistema",
            "/query/<ip_address>": "GET - Consultar datos para una dirección IP específica",
            "/servers": "GET - Listar todos los servidores monitoreados",
            "/health": "GET - Verificar estado del sistema"
        }
    }), 200


if __name__ == "__main__":
    setup_app()
    # En producción, FLASK_ENV debe ser 'production' y DEBUG debe ser False
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)
