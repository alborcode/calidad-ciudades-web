# Dockerfile - Calidad Ciudades Web
# Imagen de producción para NiceGUI

FROM python:3.14-slim

# Establecer directorio de trabajo
WORKDIR /app

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY app/ ./app/

# Crear directorio de datos (se montará como volumen)
RUN mkdir -p /app/data

# Puerto por defecto de NiceGUI
EXPOSE 8080

# Comando para ejecutar la aplicación
CMD ["python", "-m", "app.main"]
