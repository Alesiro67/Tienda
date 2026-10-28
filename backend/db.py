"""Conexión a PostgreSQL de Supabase (antes: MySQL con mysqli)."""
import psycopg
from psycopg.rows import dict_row
from flask import g

import config


def get_db():
    """Devuelve la conexión de esta petición (se crea una sola vez)."""
    if "db" not in g:
        if not config.DATABASE_URL:
            raise RuntimeError("Falta la variable de entorno DATABASE_URL")
        g.db = psycopg.connect(
            config.DATABASE_URL,
            row_factory=dict_row,      # las filas llegan como diccionarios
            prepare_threshold=None,    # necesario si se usa el pooler de Supabase
        )
    return g.db


def cerrar_db(error=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_app(app):
    app.teardown_appcontext(cerrar_db)
