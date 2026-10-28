"""Configuración del backend. Todo se lee de variables de entorno
(en Render se configuran en Environment). Nunca escribas contraseñas aquí."""
import os

# Cadena de conexión de Supabase (Connect -> Session pooler)
DATABASE_URL = os.environ.get("DATABASE_URL", "")

# Páginas autorizadas a llamar a esta API (tu dirección de Vercel, sin "/" al final).
# Varias se separan con coma. Las de localhost sirven para probar en tu PC.
ORIGENES_PERMITIDOS = [
    o.strip().rstrip("/")
    for o in os.environ.get("FRONTEND_URL", "").split(",")
    if o.strip()
] + ["http://127.0.0.1:8000", "http://localhost:8000"]

# Hora que se muestra en los recibos (el servidor de Render trabaja en UTC)
ZONA_HORARIA = os.environ.get("ZONA_HORARIA", "America/El_Salvador")
