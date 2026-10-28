"""Genera el recibo como imagen PNG (antes incluir/generar_recibo.php).

Ya no se guarda en el disco (en Render el disco se borra al reiniciar):
la imagen se crea en memoria y se devuelve como bytes.
"""
import io
import os

from PIL import Image, ImageDraw, ImageFont

CARPETA_FUENTES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fuentes")


def _fuente(tamano, negrita=False):
    """DejaVu Sans (incluida en /fuentes) porque soporta tildes y ñ."""
    archivo = "DejaVuSans-Bold.ttf" if negrita else "DejaVuSans.ttf"
    try:
        return ImageFont.truetype(os.path.join(CARPETA_FUENTES, archivo), tamano)
    except OSError:
        return ImageFont.load_default(size=tamano)   # plan B (sin tildes)


def generar_recibo_png(id_pedido, nombre_cliente, items, total, fecha):
    """Devuelve los bytes del PNG del recibo."""
    ancho = 480
    alto_por_item = 26
    alto = 300 + len(items) * alto_por_item

    img = Image.new("RGB", (ancho, alto), (255, 255, 255))
    dibujo = ImageDraw.Draw(img)

    negro = (40, 30, 30)
    naranja = (232, 115, 74)
    gris = (140, 140, 140)
    linea = (220, 210, 205)

    f1, f2, f3 = _fuente(9), _fuente(11), _fuente(12)
    f5 = _fuente(16, negrita=True)

    x = 24
    y = 24

    dibujo.text((x, y), "DULCE FERIA", fill=naranja, font=f5)
    y += 24
    dibujo.text((x, y), f"Recibo de compra No. {id_pedido:06d}", fill=negro, font=f3)
    y += 20
    dibujo.text((x, y), f"Fecha: {fecha}", fill=gris, font=f2)
    y += 30

    dibujo.text((x, y), f"Cliente: {nombre_cliente}", fill=negro, font=f3)
    y += 30

    dibujo.line((x, y, ancho - x, y), fill=linea)
    y += 12

    dibujo.text((x, y), "Cant.", fill=negro, font=f3)
    dibujo.text((x + 60, y), "Producto", fill=negro, font=f3)
    dibujo.text((x + 300, y), "Subtotal", fill=negro, font=f3)
    y += 20
    dibujo.line((x, y, ancho - x, y), fill=linea)
    y += 12

    for item in items:
        dibujo.text((x, y), str(item["cantidad"]), fill=negro, font=f3)
        dibujo.text((x + 60, y), item["nombre"][:28], fill=negro, font=f3)
        dibujo.text((x + 300, y), f"${item['subtotal']:,.2f}", fill=negro, font=f3)
        y += alto_por_item

    dibujo.line((x, y, ancho - x, y), fill=linea)
    y += 20

    dibujo.text((x, y), f"TOTAL: ${total:,.2f}", fill=naranja, font=f5)
    y += 40

    dibujo.text((x, y), "Gracias por tu compra!", fill=gris, font=f2)
    y += 18
    dibujo.text((x, y), "Recibo informativo - Proyecto de Feria de Emprendedurismo", fill=gris, font=f1)
    y += 14
    dibujo.text((x, y), "No es un documento fiscal oficial", fill=gris, font=f1)

    salida = io.BytesIO()
    img.save(salida, format="PNG")
    return salida.getvalue()
