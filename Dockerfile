#imagen ligera de Python 3.11
FROM python:3.11-slim

#directorio de trabajo dentro del contenedor
WORKDIR /app

ENV PYTHONPATH=/app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el contenido del contexto al contenedor
COPY . /app

# Muestra el contenido para depuración 
RUN echo "Contenido1 de /app:" && ls -l /app

# Expone el puerto por defecto de Gunicorn 
EXPOSE 8080

# Comando para ejecutar la app usando Gunicorn
ENV PORT=8080
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8080", "--workers", "1", "--threads", "8", "--timeout", "180", "--graceful-timeout", "30", "--keep-alive", "5"]
