# Sistema de Citas - Clínica Veterinaria

![Status](https://img.shields.io/badge/Status-Completed-success)
![Framework](https://img.shields.io/badge/Framework-Django-092E20?logo=django)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)

Backend desarrollado en **Python (Django)** diseñado específicamente para resolver las necesidades logísticas y administrativas de una Clínica Veterinaria. Este sistema centraliza el agendamiento de pacientes (mascotas) y la organización del personal médico.

## 🐾 Características Principales

El núcleo del sistema reside en la aplicación `citas`, la cual gestiona todos los registros de la clínica con un esquema de base de datos relacional robusto:

- **Gestión Completa de Citas:** Permite agendar especificando la fecha, la hora, la mascota, y el departamento o especialidad requerida.
- **Control de Facturación:** Integra campos para la emisión de facturas, incluyendo NIT, Apellido de Facturación y costos de servicio.
- **Migraciones Históricas:** Cuenta con un sólido registro de migraciones de la base de datos (Django ORM) para el control de versiones de los modelos de datos.
- **Despliegue en Contenedores:** Incluye un `Dockerfile` optimizado (usando Python `3.12-slim`) que instala las dependencias del sistema operativo (como soporte gráfico para ciertas librerías y `psycopg2` para bases de datos PostgreSQL) garantizando un entorno reproducible en cualquier máquina o servidor.
- **Soporte SSL/TLS:** Configuración local lista para pruebas seguras mediante certificados (archivos `.crt` y `.key`).

## 🛠️ Tecnologías Utilizadas
- **Lenguaje:** Python 3.12
- **Framework Web:** Django (Módulo `veterinaria.settings`)
- **Base de Datos:** PostgreSQL (preparado mediante dependencias en Docker)
- **Infraestructura:** Docker

---
- **Fecha de creación del repositorio:** 06 de Mayo de 2025
- **Fecha de actualización del README:** 18 de Agosto de 2026
