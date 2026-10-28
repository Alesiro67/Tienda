"""Backend de la tienda de aguas frescas (API en Flask, se publica en Render).

Antes cada ruta devolvía una página HTML. Ahora devuelve JSON y el frontend
(Vercel) se encarga de mostrar las páginas.

    GET  /api/productos  -> catálogo con stock        (antes index.php)
    POST /api/carrito    -> carrito con precios reales (antes carrito.php)
    POST /api/compra     -> guarda el pedido y arma el recibo
                            (antes procesar_compra.php)
"""
import base64
import re
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask, jsonify, request

import config
import db
from carrito import limpiar_carrito, obtener_carrito_detallado
from generar_recibo import generar_recibo_png

app = Flask(__name__)
db.init_app(app)


class StockInsuficiente(Exception):
    pass


class ErrorDeUsuario(Exception):
    pass


# ---------------------------------------------------------------------- CORS
@app.after_request
def permitir_frontend(respuesta):
    """Deja que SOLO las páginas autorizadas (tu Vercel) llamen a esta API."""
    origen = request.headers.get("Origin", "")
    if origen in config.ORIGENES_PERMITIDOS:
        respuesta.headers["Access-Control-Allow-Origin"] = origen
        respuesta.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        respuesta.headers["Access-Control-Allow-Headers"] = "Content-Type"
        respuesta.headers["Access-Control-Max-Age"] = "86400"
    respuesta.headers["Vary"] = "Origin"
    return respuesta


@app.errorhandler(ErrorDeUsuario)
def error_de_usuario(error):
    return jsonify(error=str(error)), 400


@app.errorhandler(Exception)
def error_interno(error):
    # Los errores HTTP normales (404, 405...) se dejan pasar con su código
    codigo = getattr(error, "code", None)
    if codigo and codigo < 500:
        return jsonify(error=getattr(error, "description", "Error")), codigo
    app.logger.exception("Error interno")
    return jsonify(error="Error interno del servidor."), 500


# --------------------------------------------------------------------- rutas
@app.route("/")
def salud():
    return jsonify(ok=True, servicio="tienda-api")


@app.route("/api/productos")
def productos():
    with db.get_db().cursor() as cur:
        cur.execute("SELECT id, nombre, precio, stock FROM productos WHERE stock > 0 ORDER BY id")
        filas = cur.fetchall()
    return jsonify([
        {"id": f["id"], "nombre": f["nombre"], "precio": float(f["precio"]), "stock": f["stock"]}
        for f in filas
    ])


@app.route("/api/carrito", methods=["POST"])
def carrito():
    datos = request.get_json(silent=True) or {}
    detalle = obtener_carrito_detallado(db.get_db(), limpiar_carrito(datos.get("carrito")))
    return jsonify(
        items=[
            {
                "id_producto": i["id_producto"],
                "nombre": i["nombre"],
                "precio": float(i["precio"]),
                "cantidad": i["cantidad"],
                "stock_disponible": i["stock_disponible"],
                "subtotal": float(i["subtotal"]),
            }
            for i in detalle["items"]
        ],
        total=float(detalle["total"]),
    )


@app.route("/api/compra", methods=["POST"])
def compra():
    datos = request.get_json(silent=True) or {}
    conn = db.get_db()

    nombre = str(datos.get("nombre", "")).strip()
    whatsapp = str(datos.get("whatsapp", "")).strip()

    if nombre == "":
        raise ErrorDeUsuario("El nombre es obligatorio.")
    if len(nombre) > 150:
        raise ErrorDeUsuario("El nombre es demasiado largo.")
    if whatsapp and not re.fullmatch(r"\d{8,15}", whatsapp):
        raise ErrorDeUsuario("El WhatsApp debe tener entre 8 y 15 números, sin espacios.")

    detalle = obtener_carrito_detallado(conn, limpiar_carrito(datos.get("carrito")))
    items = detalle["items"]
    total = detalle["total"]

    if not items:
        raise ErrorDeUsuario("Tu carrito está vacío.")

    for item in items:
        if item["cantidad"] > item["stock_disponible"]:
            raise ErrorDeUsuario(f"No hay suficiente stock de {item['nombre']}.")

    # Todo se guarda en una transacción: o se guarda completo o nada.
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO clientes (nombre, whatsapp) VALUES (%s, %s) RETURNING id",
                (nombre, whatsapp),
            )
            id_cliente = cur.fetchone()["id"]

            cur.execute(
                "INSERT INTO pedidos (id_cliente, total) VALUES (%s, %s) RETURNING id",
                (id_cliente, total),
            )
            id_pedido = cur.fetchone()["id"]

            for item in items:
                cur.execute(
                    "INSERT INTO pedido_detalle "
                    "(id_pedido, id_producto, nombre_producto, cantidad, precio_unitario, subtotal) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    (id_pedido, item["id_producto"], item["nombre"],
                     item["cantidad"], item["precio"], item["subtotal"]),
                )
                # El "AND stock >= %s" evita que el stock quede en negativo
                cur.execute(
                    "UPDATE productos SET stock = stock - %s WHERE id = %s AND stock >= %s",
                    (item["cantidad"], item["id_producto"], item["cantidad"]),
                )
                if cur.rowcount == 0:
                    raise StockInsuficiente(item["nombre"])
        conn.commit()
    except StockInsuficiente as error:
        conn.rollback()
        raise ErrorDeUsuario(f"No hay suficiente stock de {error.args[0]}.")
    except Exception:
        conn.rollback()
        raise

    fecha = datetime.now(ZoneInfo(config.ZONA_HORARIA)).strftime("%d/%m/%Y %H:%M")
    png = generar_recibo_png(id_pedido, nombre, items, total, fecha)

    return jsonify(
        id=id_pedido,
        nombre=nombre,
        whatsapp=whatsapp,
        fecha=fecha,
        items=[
            {
                "nombre": i["nombre"],
                "cantidad": i["cantidad"],
                "precio": float(i["precio"]),
                "subtotal": float(i["subtotal"]),
            }
            for i in items
        ],
        total=float(total),
        recibo_png="data:image/png;base64," + base64.b64encode(png).decode("ascii"),
    ), 201


if __name__ == "__main__":
    app.run(debug=True, port=5000)
