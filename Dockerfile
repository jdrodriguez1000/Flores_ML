# Etapa 1: Build y Dependencias
FROM python:3.12-slim as builder

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt
# Añadimos fastapi y uvicorn explícitamente si no están en requirements.txt
RUN pip install --no-cache-dir --prefix=/install fastapi uvicorn pydantic-settings httpx

# Etapa 2: Imagen Final Ligera
FROM python:3.12-slim

WORKDIR /app

# Copiar dependencias instaladas
COPY --from=builder /install /usr/local

# Copiar el código de la aplicación
COPY src/ ./src/
COPY models/ ./models/
COPY data/ ./data/

# Variables de entorno por defecto
ENV PYTHONPATH=/app
ENV SHADOW_MODE=True
ENV API_PORT=8000

# Exponer el puerto
EXPOSE 8000

# Comando para ejecutar la API
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
