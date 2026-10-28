"""Genera el recibo como imagen PNG (antes incluir/generar_recibo.php).

PHP usaba la librería GD; en Python se usa Pillow (pip install Pillow).
"""
import os
import time
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
CARPETA_RECIBOS = os.path.join(BASE, "static", "recibos")
CARPETA_FUENTES = os.path.join(BASE, "fuentes")


def _fuente(tamano, negrita=False):
    """Carga DejaVu Sans (incluida en /fuentes) porque soporta tildes y ñ."""
    archivo = "DejaVuSans-Bold.ttf" if negrita else "DejaVuSans.ttf"
    try:
        return ImageFont.truetype(os.path.join(CARPETA_FUENTES, archivo), tamano)
    except OSError:
        return ImageFont.load_default(size=tamano)   # plan B (sin tildes)


def generar_recibo_imagen(id_pedido, nombre_cliente, items, total):
    """Crea el PNG del recibo y devuelve su ruta relativa a /static."""
    ancho = 480
    alto_por_item = 26
    alto = 300 + len(items) * alto_por_item

    img = Image.new("RGB", (ancho, alto), (255, 255, 255))
    dibujo = ImageDraw.Draw(img)

    # Colores
    negro = (40, 30, 30)
    naranja = (232, 115, 74)
    gris = (140, 140, 140)
    linea = (220, 210, 205)

    # Tamaños de letra (equivalen a las fuentes 1, 2, 3 y 5 de GD)
    f1 = _fuente(9)
    f2 = _fuente(11)
    f3 = _fuente(12)
    f5 = _fuente(16, negrita=True)

    x = 24
    y = 24

    # Encabezado
    dibujo.text((x, y), "DULCE FERIA", fill=naranja, font=f5)
    y += 24
    dibujo.text((x, y), f"Recibo de compra No. {id_pedido:06d}", fill=negro, font=f3)
    y += 20
    dibujo.text((x, y), "Fecha: " + datetime.now().strftime("%d/%m/%Y %H:%M"), fill=gris, font=f2)
    y += 30

    # Cliente
    dibujo.text((x, y), f"Cliente: {nombre_cliente}", fill=negro, font=f3)
    y += 30

    # Línea separadora
    dibujo.line((x, y, ancho - x, y), fill=linea)
    y += 12

    # Encabezado de tabla
    dibujo.text((x, y), "Cant.", fill=negro, font=f3)
    dibujo.text((x + 60, y), "Producto", fill=negro, font=f3)
    dibujo.text((x + 300, y), "Subtotal", fill=negro, font=f3)
    y += 20
    dibujo.line((x, y, ancho - x, y), fill=linea)
    y += 12

    # Filas de productos
    for item in items:
        dibujo.text((x, y), str(item["cantidad"]), fill=negro, font=f3)
        dibujo.text((x + 60, y), item["nombre"][:28], fill=negro, font=f3)
        dibujo.text((x + 300, y), f"${item['subtotal']:,.2f}", fill=negro, font=f3)
        y += alto_por_item

    dibujo.line((x, y, ancho - x, y), fill=linea)
    y += 20

    # Total
    dibujo.text((x, y), f"TOTAL: ${total:,.2f}", fill=naranja, font=f5)
    y += 40

    # Pie de página
    dibujo.text((x, y), "Gracias por tu compra!", fill=gris, font=f2)
    y += 18
    dibujo.text((x, y), "Recibo informativo - Proyecto de Feria de Emprendedurismo", fill=gris, font=f1)
    y += 14
    dibujo.text((x, y), "No es un documento fiscal oficial", fill=gris, font=f1)

    # Guardar archivo
    nombre_archivo = f"recibo_{id_pedido}_{int(time.time())}.png"
    os.makedirs(CARPETA_RECIBOS, exist_ok=True)
    img.save(os.path.join(CARPETA_RECIBOS, nombre_archivo))

    return f"recibos/{nombre_archivo}"
