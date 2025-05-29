# Usar imagen oficial de Python 3.12 (basado en los archivos __pycache__)
FROM python:3.12-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Crear un usuario no root para mayor seguridad
RUN adduser --disabled-password --gecos "" appuser

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements.txt primero para aprovechar la caché de Docker
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Crear directorio de logs y dar permisos
RUN mkdir -p /app/logs && \
    chown -R appuser:appuser /app

# Cambiar al usuario no root
USER appuser

# Exponer el puerto fijo
EXPOSE 8001

# Comando para ejecutar la aplicación (formato JSON recomendado)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8001"]