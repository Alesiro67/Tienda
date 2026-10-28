"""Cruza el carrito que manda el frontend con los datos reales de la BD
(antes incluir/carrito_funciones.php). El carrito llega como { "id": cantidad }."""
from decimal import Decimal


def limpiar_carrito(crudo):
    """Convierte {"1": 2, ...} en {1: 2, ...} ignorando valores inválidos."""
    limpio = {}
    if not isinstance(crudo, dict):
        return limpio
    for id_texto, cantidad in crudo.items():
        try:
            id_producto = int(id_texto)
            cantidad = int(cantidad)
        except (TypeError, ValueError):
            continue
        if id_producto > 0 and 0 < cantidad <= 1000:
            limpio[id_producto] = cantidad
    return limpio


def obtener_carrito_detallado(conn, carrito):
    """Devuelve los productos del carrito con precio y stock actuales + total."""
    items = []
    total = Decimal("0")
    if not carrito:
        return {"items": items, "total": total}

    ids = list(carrito.keys())
    marcas = ", ".join(["%s"] * len(ids))
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT id, nombre, precio, stock FROM productos WHERE id IN ({marcas}) ORDER BY id",
            ids,
        )
        productos = cur.fetchall()

    # Los productos que ya no existen simplemente no aparecen
    for producto in productos:
        cantidad = carrito[producto["id"]]
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
