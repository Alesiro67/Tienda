"""Configuración (antes config.php).

Los datos de conexión se leen de variables de entorno; si no existen se usan
los mismos valores locales que tenías en PHP. Nunca escribas aquí contraseñas
de un servidor real.
"""
import os

DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "root123")
DB_NAME = os.environ.get("DB_NAME", "tienda_bd")

# Clave para firmar la sesión (equivale a session_start() de PHP).
SECRET_KEY = os.environ.get("SECRET_KEY", "cambia-esta-clave-en-produccion")
