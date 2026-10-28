"""Funciones del carrito (antes incluir/carrito_funciones.php).

El carrito vive en la sesión con el formato { "id_producto": cantidad }.
Las claves son texto porque la sesión de Flask se guarda como JSON.
"""
from decimal import Decimal

from flask import session


def obtener_carrito_detallado(conn):
    """Cruza el carrito con la info real de la BD y calcula subtotales y total."""
    carrito = session.get("carrito", {})
    items = []
    total = Decimal("0")

    with conn.cursor() as cur:
        for id_producto, cantidad in list(carrito.items()):
            cur.execute(
                "SELECT id, nombre, precio, stock FROM productos WHERE id = %s",
                (int(id_producto),),
            )
            producto = cur.fetchone()

            if producto is None:
                # El producto ya no existe: lo quitamos del carrito
                del carrito[id_producto]
                session["carrito"] = carrito
                continue

            subtotal = producto["precio"] * cantidad
            total += subtotal

            items.append({
                "id_producto": producto["id"],
                "nombre": producto["nombre"],
                "precio": producto["precio"],
                "cantidad": cantidad,
                "stock_disponible": producto["stock"],
                "subtotal": subtotal,
            })

    return {"items": items, "total": total}


def contar_unidades_carrito():
    """Unidades totales en el carrito (para el contador del header)."""
    return sum(session.get("carrito", {}).values())
