# Agente Portable de Monitoreo

## Descripción

Este agente portable es un programa autónomo diseñado para recolectar información del sistema operativo (Windows o Linux) y enviarla a una API centralizada de monitoreo. El agente es parte del proyecto Prex Cybersecurity Challenge.

## Características

- **Portable**: Funciona sin instalación en Windows y Linux
- **Autónomo**: Instala automáticamente sus dependencias
- **Seguro**: Usa autenticación mediante API Key
- **Flexible**: Puede ejecutarse una vez o en intervalos regulares
- **Liviano**: Mínimo impacto en el rendimiento del sistema

## Información Recolectada

El agente recolecta:

- **Procesador**: Tipo, núcleos, uso
- **Procesos**: Lista de procesos en ejecución con detalles
- **Usuarios**: Sesiones activas en el sistema
- **Sistema Operativo**: Nombre y versión

## Requisitos

- Python 3.7+ (instalado en el sistema)
- Conexión a internet (para enviar datos y descargar dependencias si es necesario)
- Permisos de administrador/root (para instalar dependencias)

## Instalación y Uso

### En Windows

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

### En Linux

1. Copie la carpeta `portable_agent` al servidor destino
2. Otorgue permisos de ejecución:
   ```bash
   chmod +x install_and_run.sh
   ```
3. Ejecute el script de instalación:
   ```bash
   ./install_and_run.sh
   ```

## Opciones de Configuración

### Parámetros de Línea de Comandos

El agente acepta varios parámetros:

- `--url URL` - URL de la API (por defecto: http://52.14.229.100:5000)
- `--interval SEGUNDOS` - Intervalo de recolección en segundos (por defecto: ejecución única)
- `--quiet` - Modo silencioso, sin mensajes en consola

Ejemplos:

```bash
# Enviar datos a una API personalizada
python system_info_agent.py --url http://mi-api-personalizada.com:5000

# Enviar datos cada 5 minutos (300 segundos)
python system_info_agent.py --interval 300

# Ejecución silenciosa con intervalo personalizado
python system_info_agent.py --interval 60 --quiet
```

### Configuración Interna

Si desea modificar la configuración predeterminada, edite las variables al inicio del archivo `system_info_agent.py`:

```python
# URL de la API de recolección
API_URL = "http://52.14.229.100:5000"

# Clave para autenticación en la API
API_SECRET = "d4t0s-s3rv3r-4g3nt-s3cr3t"
```

## Seguridad

- La comunicación con la API usa autenticación mediante API Key
- La clave se envía en el encabezado HTTP `Authorization: ApiKey <clave>`
- Todas las marcas de tiempo se manejan en UTC para consistencia global
- Los errores son manejados de forma segura sin exponer información sensible

## Solución de Problemas

### Errores comunes:

1. **Error de conexión**: Verifique que la API esté en línea y accesible
2. **Error 401 Unauthorized**: Verifique que la API_SECRET sea correcta
3. **Error al instalar dependencias**: Asegúrese de tener permisos de administrador/root

### Logs:

El agente muestra información detallada en la consola a menos que se use el modo `--quiet`.

## Nota sobre Zonas Horarias

Todas las marcas de tiempo se manejan en UTC para evitar problemas con zonas horarias y horario de verano.
