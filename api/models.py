"""
Modelos de base de datos para la API de Recolección de Información de Sistemas
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class Server(db.Model):
    """Modelo que representa un servidor monitoreado."""
    
    __tablename__ = 'servers'
    
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50), unique=True, nullable=False)
    first_seen = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    last_seen = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relaciones
    os_info = db.relationship("OSInfo", back_populates="server", cascade="all, delete-orphan")
    processor_info = db.relationship("ProcessorInfo", back_populates="server", cascade="all, delete-orphan")
    processes = db.relationship("Process", back_populates="server", cascade="all, delete-orphan")
    logged_users = db.relationship("LoggedUser", back_populates="server", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Server {self.ip_address}>"
    
    def to_dict(self, include_relations=False):
        """Convertir modelo a diccionario."""
        data = {
            "id": self.id,
            "ip_address": self.ip_address,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat()
        }
        
        if include_relations:
            # Incluir relaciones para un vistazo completo
            data['os_info'] = [os.to_dict() for os in self.os_info.order_by(OSInfo.timestamp.desc()).limit(10)]
            data['processor_info'] = [proc.to_dict() for proc in self.processor_info.order_by(ProcessorInfo.timestamp.desc()).limit(10)]
        
        return data


class OSInfo(db.Model):
    """Modelo que representa información del sistema operativo."""
    
    __tablename__ = 'os_info'
    
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    system = db.Column(db.String(100))
    release = db.Column(db.String(100))
    version = db.Column(db.String(255))
    platform = db.Column(db.String(255))
    
    # Relación
    server = db.relationship("Server", back_populates="os_info")
    
    def __repr__(self):
        return f"<OSInfo {self.system} {self.release}>"
    
    def to_dict(self):
        """Convertir modelo a diccionario."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "system": self.system,
            "release": self.release,
            "version": self.version,
            "platform": self.platform
        }


class ProcessorInfo(db.Model):
    """Modelo que representa información del procesador."""
    
    __tablename__ = 'processor_info'
    
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    cpu_count = db.Column(db.Integer)
    model = db.Column(db.String(255))
    cpu_percent = db.Column(db.Float)
    
    # Relación
    server = db.relationship("Server", back_populates="processor_info")
    
    def __repr__(self):
        return f"<ProcessorInfo {self.model}>"
    
    def to_dict(self):
        """Convertir modelo a diccionario."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "cpu_count": self.cpu_count,
            "model": self.model,
            "cpu_percent": self.cpu_percent
        }


class Process(db.Model):
    """Modelo que representa un proceso en ejecución."""
    
    __tablename__ = 'processes'
    
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    pid = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(100))
    
    # Relación
    server = db.relationship("Server", back_populates="processes")
    
    def __repr__(self):
        return f"<Process {self.pid} {self.name}>"
    
    def to_dict(self):
        """Convertir modelo a diccionario."""
        return {
            "id": self.id,
            "pid": self.pid,
            "name": self.name,
            "username": self.username
        }


class LoggedUser(db.Model):
    """Modelo que representa un usuario con sesión abierta."""
    
    __tablename__ = 'logged_users'
    
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    terminal = db.Column(db.String(100))
    host = db.Column(db.String(255))
    
    # Relación
    server = db.relationship("Server", back_populates="logged_users")
    
    def __repr__(self):
        return f"<LoggedUser {self.username}>"
    
    def to_dict(self):
        """Convertir modelo a diccionario."""
        return {
            "id": self.id,
            "username": self.username,
            "terminal": self.terminal,
            "host": self.host
        }
