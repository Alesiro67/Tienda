"""Conexión a MySQL (antes: $conn = new mysqli(...) en config.php)."""
import pymysql
from pymysql.cursors import DictCursor
from flask import g

import config


def get_db():
    """Devuelve la conexión de esta petición (se crea una sola vez)."""
    if "db" not in g:
        g.db = pymysql.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            charset="utf8mb4",
            cursorclass=DictCursor,   # las filas llegan como diccionarios
        )
    return g.db


def cerrar_db(error=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_app(app):
    app.teardown_appcontext(cerrar_db)
