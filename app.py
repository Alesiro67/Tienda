"""Tienda de aguas frescas - versión Flask (antes en PHP).

Equivalencias con los archivos PHP originales:
    index.php            -> index()
    agregar_carrito.php  -> agregar_carrito()
    carrito.php          -> ver_carrito()
    eliminar_carrito.php -> eliminar_carrito()
    procesar_compra.php  -> procesar_compra()
    recibo.php           -> recibo()
"""
import re
from datetime import datetime
from functools import wraps
from urllib.parse import quote_plus

from flask import Flask, make_response, redirect, render_template, request, session, url_for
from markupsafe import escape

import config
import db
from carrito_funciones import contar_unidades_carrito, obtener_carrito_detallado
from generar_recibo import generar_recibo_imagen

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
db.init_app(app)


class StockInsuficiente(Exception):
    pass


# ---------------------------------------------------------------- utilidades
@app.template_filter("dinero")
def dinero(valor):
    """Equivale a number_format($valor, 2) de PHP -> 1,234.50"""
    return f"{valor:,.2f}"


def sin_cache(vista):
    """Equivale a los header("Cache-Control: no-store...") del PHP."""
    @wraps(vista)
    def envoltura(*args, **kwargs):
        respuesta = make_response(vista(*args, **kwargs))
        respuesta.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        respuesta.headers["Pragma"] = "no-cache"
        return respuesta
    return envoltura


def a_entero(valor):
    """Equivale a intval() de PHP: si no es número devuelve 0."""
    try:
        return int(valor)
    except (TypeError, ValueError):
        return 0


# -------------------------------------------------------------------- rutas
@app.route("/")
@sin_cache
def index():
    with db.get_db().cursor() as cur:
        cur.execute("SELECT * FROM productos WHERE stock > 0")
        productos = cur.fetchall()
    return render_template(
        "index.html",
        productos=productos,
        unidades_carrito=contar_unidades_carrito(),
    )


@app.route("/agregar_carrito", methods=["POST"])
def agregar_carrito():
    id_producto = a_entero(request.form.get("id_producto", 0))
    cantidad = a_entero(request.form.get("cantidad", 1))

    if id_producto <= 0 or cantidad <= 0:
        return redirect(url_for("index"))

    # Verifica que el producto exista y que haya stock
    with db.get_db().cursor() as cur:
        cur.execute("SELECT stock FROM productos WHERE id = %s", (id_producto,))
        producto = cur.fetchone()

    if producto is None:
        return redirect(url_for("index"))

    carrito = session.get("carrito", {})
    cantidad_actual = carrito.get(str(id_producto), 0)
    nueva_cantidad = cantidad_actual + cantidad

    # No deja agregar de más si no hay más en stock
    if nueva_cantidad > producto["stock"]:
        nueva_cantidad = producto["stock"]

    carrito[str(id_producto)] = nueva_cantidad
    session["carrito"] = carrito

    return redirect(url_for("index", agregado=1))


@app.route("/carrito")
def ver_carrito():
    carrito = obtener_carrito_detallado(db.get_db())
    return render_template("carrito.html", items=carrito["items"], total=carrito["total"])


@app.route("/eliminar_carrito")
def eliminar_carrito():
    id_producto = a_entero(request.args.get("id", 0))

    carrito = session.get("carrito", {})
    if str(id_producto) in carrito:
        del carrito[str(id_producto)]
        session["carrito"] = carrito

    return redirect(url_for("ver_carrito"))


@app.route("/procesar_compra", methods=["POST"])
def procesar_compra():
    conn = db.get_db()
    carrito = obtener_carrito_detallado(conn)
    items = carrito["items"]
    total = carrito["total"]

    if not items:
        return redirect(url_for("ver_carrito"))

    nombre = request.form.get("nombre", "").strip()
    whatsapp = request.form.get("whatsapp", "").strip()

    if nombre == "":
        return "Error: el nombre es obligatorio.", 400

    # Verifica si hay stock antes de hacer nada
    for item in items:
        if item["cantidad"] > item["stock_disponible"]:
            return f"Error: no hay suficiente stock de {escape(item['nombre'])}.", 400

    # Todo el guardado va en una transacción: o se guarda completo o nada.
    try:
        with conn.cursor() as cur:
            # Se guarda el cliente
            cur.execute(
                "INSERT INTO clientes (nombre, whatsapp) VALUES (%s, %s)",
                (nombre, whatsapp),
            )
            id_cliente = cur.lastrowid

            # Se crea el pedido, ya con la cuenta completa
            cur.execute(
                "INSERT INTO pedidos (id_cliente, total) VALUES (%s, %s)",
                (id_cliente, total),
            )
            id_pedido = cur.lastrowid

            # Se guarda el detalle y se descuenta del stock
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
        return f"Error: no hay suficiente stock de {escape(error.args[0])}.", 400
    except Exception:
        conn.rollback()
        raise

    # Genera la imagen del recibo
    ruta_recibo = generar_recibo_imagen(id_pedido, nombre, items, total)

    # Vacía el carrito
    session["carrito"] = {}

    # Guarda la info para mostrarla en recibo.php (la sesión solo admite JSON,
    # por eso los Decimal de MySQL se pasan a float)
    session["ultimo_pedido"] = {
        "id": id_pedido,
        "nombre": nombre,
        "whatsapp": whatsapp,
        "items": [
            {
                "id_producto": i["id_producto"],
                "nombre": i["nombre"],
                "precio": float(i["precio"]),
                "cantidad": i["cantidad"],
                "subtotal": float(i["subtotal"]),
            }
            for i in items
        ],
        "total": float(total),
        "recibo": ruta_recibo,
    }

    return redirect(url_for("recibo"))


@app.route("/recibo")
@sin_cache
def recibo():
    pedido = session.get("ultimo_pedido")
    if not pedido:
        return redirect(url_for("index"))

    # Mensaje predefinido para el enlace de WhatsApp (Click to Chat)
    lista_productos = "".join(
        f"{i['cantidad']}x {i['nombre']} (${i['subtotal']:,.2f})\n" for i in pedido["items"]
    )
    mensaje = (
        f"Hola {pedido['nombre']} Aqui esta tu recibo "
        "(muestra este ticket a la hora de comprar tu producto):\n\n"
        f"Pedido No. {pedido['id']:06d}\n"
        f"{lista_productos}"
        f"\nTotal: ${pedido['total']:,.2f}\n\nGracias por tu compra!"
    )

    whatsapp_limpio = re.sub(r"\D", "", pedido.get("whatsapp") or "")
    enlace_whatsapp = (
        f"https://wa.me/{whatsapp_limpio}?text={quote_plus(mensaje)}"
        if whatsapp_limpio else None
    )

    return render_template(
        "recibo.html",
        pedido=pedido,
        fecha=datetime.now().strftime("%d/%m/%Y %H:%M"),
        enlace_whatsapp=enlace_whatsapp,
    )


if __name__ == "__main__":
    app.run(debug=True)
