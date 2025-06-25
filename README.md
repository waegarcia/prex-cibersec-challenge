# Prex Cybersecurity Challenge

## Descripción

Este proyecto es una solución integral para el monitoreo de servidores, desarrollada como parte del desafío técnico de Cybersecurity para Prex. El sistema consta de dos componentes principales:

1. **Agente Portable**: Programa autónomo que recolecta información del sistema operativo donde se ejecuta y la envía a la API utilizando autenticación mediante API Key. No requiere configuración externa ni dependencias adicionales.

2. **API Dockerizada**: Servicio web que recibe la información de los agentes (con validación de API Key), la almacena en PostgreSQL y archivos JSON (respaldo), y permite consultas públicas por IP.

## Información recolectada

El agente recolecta la siguiente información del sistema:

- Información sobre el procesador
- Listado de procesos en ejecución
- Usuarios con sesiones activas
- Nombre y versión del sistema operativo

## Requisitos

- Python 3.7+
- Para la API: Dependencias especificadas en su archivo `requirements.txt`
- Para el agente portable: psutil y requests (instaladas automáticamente por los scripts de instalación)
- Docker y Docker Compose (solo para el despliegue de la API)

## Estructura del Proyecto

```
prex-cybersec-challenge/
├── api/
│   ├── api_server.py   # API para recibir y almacenar datos
│   ├── models.py       # Modelos SQLAlchemy para la base de datos
│   ├── requirements.txt # Dependencias de la API
│   ├── Dockerfile      # Configuración para dockerizar la API
│   ├── docker-compose.yml # Configuración para despliegue con Docker y PostgreSQL
│   └── schema.sql      # Esquema SQL para la inicialización de la base de datos
│   └── data/           # Directorio creado para almacenar datos JSON
│
├── portable_agent/
│   ├── system_info_agent.py  # Agente portable para recolectar datos
│   ├── install_and_run.ps1   # Script de instalación para Windows
│   └── install_and_run.sh    # Script de instalación para Linux
│
├── LICENSE             # Licencia del proyecto
└── README.md           # Este archivo
```

## Instalación y Uso

### API (Servidor)

1. **Requisitos previos**: 
   - Docker y Docker Compose instalados

2. **Despliegue local**:
   ```bash
   cd api
   docker-compose up -d
   ```

   Esto iniciará dos contenedores:
   - API Flask en el puerto 5000
   - PostgreSQL en el puerto 5432 (no expuesto externamente)

3. **Verificación**:
   Acceda a http://localhost:5000/health para comprobar que la API está funcionando correctamente.
   
   Para ver la API de ejemplo en AWS: http://52.14.229.100:5000/health

### Agente Portable (Clientes)

#### Windows

1. Copie la carpeta `portable_agent` al servidor destino
2. Ejecute PowerShell como administrador
3. Permita la ejecución de scripts si es necesario:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
   ```
4. Ejecute el script de instalación:
   ```powershell
   .\install_and_run.ps1
   ```

#### Linux

1. Copie la carpeta `portable_agent` al servidor destino
2. Otorgue permisos de ejecución:
   ```bash
   chmod +x install_and_run.sh
   ```
3. Ejecute el script de instalación:
   ```bash
   ./install_and_run.sh
   ```

#### Opciones adicionales del agente

El agente acepta varios parámetros de línea de comandos:

- `--url URL` - URL de la API (por defecto: configuración interna)
- `--interval SEGUNDOS` - Intervalo de recolección en segundos (por defecto: una sola ejecución)
- `--quiet` - Modo silencioso, sin mensajes en consola

Ejemplo:
```bash
python system_info_agent.py --url http://52.14.229.100:5000 --interval 300
```

## Despliegue en AWS EC2

### API Desplegada

La API ya está desplegada en una instancia EC2 de AWS y está accesible en:

- **URL**: http://52.14.229.100:5000
- **Estado**: http://52.14.229.100:5000/health
- **Servidores monitoreados**: http://52.14.229.100:5000/servers

Puede probar el agente portable configurado para enviar datos a esta API de ejemplo.

### Instrucciones para su propio despliegue

1. Inicie una instancia EC2 con su AMI preferida

2. Instale Docker y Docker Compose:
   ```bash
   sudo apt update
   sudo apt install -y docker.io docker-compose
   sudo usermod -aG docker $USER
   # Reinicie la sesión para aplicar los cambios de grupo
   ```

3. Copie el código de la API:
   ```bash
   git clone https://github.com/waegarcia/prex-cibersec-challenge.git
   # O suba manualmente la carpeta api
   ```

4. Configure las variables de entorno:
   ```bash
   cd prex-cibersec-challenge/api
   cp .env.example .env
   # Edite el archivo .env con sus credenciales seguras
   nano .env
   ```
   
   **Importante**: Configure una clave API segura y única en el archivo .env:
   ```
   API_SECRET=SuClaveSecretaSeguraYUnica
   ```

5. Inicie la API:
   ```bash
   # Docker Compose utilizará automáticamente el archivo .env
   docker-compose up -d
   ```

6. Configure los agentes en los servidores que desea monitorear para que apunten a la IP o dominio de su instancia EC2.

## Personalización del Agente

Para modificar la URL de la API a la que el agente envía los datos:

1. Abra el archivo `portable_agent/system_info_agent.py`
2. Edite el valor de la variable `API_URL` al inicio del archivo:
   ```python
   # URL de la API de recolección
   API_URL = "http://52.14.229.100:5000"  # Instancia EC2 de ejemplo
   ```

Para configurar la clave API para autenticación:

1. Asegúrese de que la misma clave esté configurada en el archivo `.env` de la API
2. Actualice el valor de la variable `API_SECRET` en el archivo `portable_agent/system_info_agent.py`:
   ```python
   # Clave secreta para la autenticación con la API
   API_SECRET = "SuClaveSecretaSeguraYUnica"
   ```
3. Guarde el archivo y vuelva a distribuirlo a los servidores

## Detalles Técnicos

- **Almacenamiento de datos**: Los datos se guardan en PostgreSQL (principal) y archivos JSON (respaldo)
- **Zona horaria**: Todas las marcas de tiempo utilizan UTC para evitar problemas de zona horaria
- **Endpoints de la API**:
  - `POST /collect` - Para recibir datos de los agentes (requiere autenticación con API Key)
  - `GET /query/<ip_address>` - Para consultar datos de un servidor específico (acceso público)
  - `GET /servers` - Para listar todos los servidores monitoreados (acceso público)
  - `GET /health` - Para verificar el estado de la API (acceso público)
  - `GET /` - Información general de la API (acceso público)

- **Autenticación**: El endpoint `/collect` requiere un encabezado de autenticación en formato: 
  ```
  Authorization: ApiKey TuClaveSecreta
  ```

## Consideraciones adicionales

- El agente funciona tanto en Windows como en Linux
- El agente no requiere configuración externa ni instalación manual de dependencias
- Los datos se almacenan en formato JSON como respaldo y en PostgreSQL como fuente principal
- La API está dockerizada para facilitar su despliegue en AWS EC2
- El agente se diseñó para ser 100% portable y simple de ejecutar en cualquier servidor
- La seguridad se implementa mediante autenticación con API Key para proteger el endpoint de recolección
- En modo producción (`FLASK_ENV=production`), el modo debug está desactivado por seguridad
