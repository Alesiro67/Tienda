# Tienda de aguas frescas (Flask + MySQL)

Versión en Python de la tienda que estaba en PHP.

## Equivalencias PHP → Python

| PHP                          | Python                                   |
|------------------------------|------------------------------------------|
| `config.php`                 | `config.py` + `db.py`                    |
| `incluir/carrito_funciones.php` | `carrito_funciones.py`                |
| `incluir/generar_recibo.php` | `generar_recibo.py` (Pillow en vez de GD) |
| `index.php`                  | `app.py` → `index()` + `templates/index.html` |
| `agregar_carrito.php`        | `app.py` → `agregar_carrito()`           |
| `carrito.php`                | `app.py` → `ver_carrito()` + `templates/carrito.html` |
| `eliminar_carrito.php`       | `app.py` → `eliminar_carrito()`          |
| `procesar_compra.php`        | `app.py` → `procesar_compra()`           |
| `recibo.php`                 | `app.py` → `recibo()` + `templates/recibo.html` |
| `$_SESSION`                  | `session` de Flask                       |
| `imagenes/`, `style.css`, `recibos/` | `static/imagenes`, `static/style.css`, `static/recibos` |

## Cómo ejecutarla

1. Instala Python 3.10 o superior.
2. Crea la base de datos importando `sql/tienda_bd.sql` en MySQL (phpMyAdmin o `mysql -u root -p < sql/tienda_bd.sql`).
3. En una terminal, dentro de esta carpeta:

```
python -m venv venv
venv\Scripts\activate          (en Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python app.py
```

4. Abre http://127.0.0.1:5000

## Conexión a la base de datos

Por defecto usa los mismos datos locales que tenía el PHP (`127.0.0.1`, usuario `root`,
contraseña `root123`, base `tienda_bd`). Si tu MySQL es distinto, cámbialos con variables
de entorno antes de ejecutar:

```
set DB_PASSWORD=tu_clave        (Mac/Linux: export DB_PASSWORD=tu_clave)
set DB_USER=root
set DB_NAME=tienda_bd
set SECRET_KEY=una-frase-larga-y-secreta
```
