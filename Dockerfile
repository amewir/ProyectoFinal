# Usa imagen oficial de Python slim (ligera)
FROM python:3.12-slim

# Variables de entorno para que Python no cree .pyc y buffer sea directo
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=veterinaria.settings

# Directorio de trabajo
WORKDIR /app

# Instala dependencias del sistema para psycopg2 y otras librerías
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copia el archivo requirements.txt
COPY requirements.txt /app/

# Instala las dependencias de Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copia todo el proyecto a la imagen
COPY . /app/

# Expone el puerto 8000 para Django
EXPOSE 8000

# Comando por defecto para ejecutar Gunicorn
CMD ["gunicorn", "veterinaria.wsgi:application", "--bind", "0.0.0.0:8000"]
