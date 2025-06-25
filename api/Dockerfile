FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para psycopg2 y el cliente PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requisitos de la API e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código del servidor API
COPY *.py .
COPY .env .
COPY schema.sql .

# Crear directorio para datos
RUN mkdir -p ./data

EXPOSE 5000

# El comando de inicio se especifica en docker-compose.yml
CMD ["python", "api_server.py"]
