-- Schema para base de datos normalizada del sistema de relevamiento
-- PostgreSQL

-- Servidores monitoreados
CREATE TABLE IF NOT EXISTS servers (
    id SERIAL PRIMARY KEY,
    ip_address VARCHAR(50) NOT NULL,
    first_seen TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_ip UNIQUE (ip_address)
);

-- Información del sistema operativo
CREATE TABLE IF NOT EXISTS os_info (
    id SERIAL PRIMARY KEY,
    server_id INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    system VARCHAR(100),
    release VARCHAR(100),
    version VARCHAR(255),
    platform VARCHAR(255),
    FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE
);

-- Información del procesador
CREATE TABLE IF NOT EXISTS processor_info (
    id SERIAL PRIMARY KEY,
    server_id INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cpu_count INTEGER,
    model VARCHAR(255),
    cpu_percent FLOAT,
    FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE
);

-- Procesos en ejecución
CREATE TABLE IF NOT EXISTS processes (
    id SERIAL PRIMARY KEY,
    server_id INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    pid INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    username VARCHAR(100),
    FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE
);

-- Usuarios con sesión
CREATE TABLE IF NOT EXISTS logged_users (
    id SERIAL PRIMARY KEY,
    server_id INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    username VARCHAR(100) NOT NULL,
    terminal VARCHAR(100),
    host VARCHAR(255),
    FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE
);

-- Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_server_ip ON servers(ip_address);
CREATE INDEX IF NOT EXISTS idx_processes_server_time ON processes(server_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_os_info_server_time ON os_info(server_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_processor_server_time ON processor_info(server_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_users_server_time ON logged_users(server_id, timestamp);
