# Tienda de aguas frescas — Vercel + Render + Supabase

```
frontend/   -> Vercel    (HTML, CSS y JavaScript: lo que ve el cliente)
backend/    -> Render    (API en Flask: productos, carrito, compra)
base de datos -> Supabase (PostgreSQL)
```

El navegador del cliente abre la página en Vercel; esa página le pide los datos
al backend en Render; el backend los lee y guarda en Supabase.

## Orden para publicarla (importa el orden)

### 1. Supabase (base de datos)
1. Crea un proyecto en supabase.com y guarda la contraseña que elijas
   (usa solo letras y números para evitar problemas).
2. Abre `backend/sql/tienda_supabase.sql`, **cambia los 4 productos del final por los tuyos**
   (el 1.º usa `Jugo1.jpg`, el 2.º `Jugo2.jpg`, etc.).
3. En Supabase: **SQL Editor → New query**, pega todo el archivo y pulsa **Run**.
4. Botón **Connect** (arriba) → **Session pooler** → copia la cadena `postgresql://...`
   y cambia `[YOUR-PASSWORD]` por tu contraseña. Esa cadena es tu `DATABASE_URL`.

### 2. GitHub
Sube todo este contenido (carpetas `backend` y `frontend`) a tu repositorio.

### 3. Render (backend)
1. render.com → **New → Web Service** → elige tu repositorio.
2. Configura:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Instance Type:** Free
3. En **Environment** agrega:
   - `DATABASE_URL` = la cadena de Supabase del paso 1
   - `PYTHON_VERSION` = `3.12.8`
4. **Create Web Service**. Al terminar copia su dirección (algo como `https://tienda-xxxx.onrender.com`).
   Si abres esa dirección debe mostrar `{"ok":true,...}`, y `/api/productos` tus productos.

### 4. Conectar el frontend con el backend
Abre `frontend/js/config.js` y cambia `https://CAMBIA-ESTO.onrender.com`
por la dirección de Render (sin `/` al final). Sube el cambio a GitHub.

### 5. Vercel (frontend)
1. vercel.com → **Add New → Project** → importa tu repositorio.
2. **Root Directory:** `frontend` · **Framework Preset:** Other · sin Build Command.
3. **Deploy**. Copia la dirección que te da (algo como `https://tienda-xxxx.vercel.app`).

### 6. Autorizar a Vercel en el backend
En Render → tu servicio → **Environment** agrega:
- `FRONTEND_URL` = la dirección de Vercel (sin `/` al final)

Render se reinicia solo. Abre tu página de Vercel y prueba una compra.

## Cosas a tener en cuenta
- **Render gratis se duerme** tras unos minutos sin visitas: la primera carga puede tardar
  hasta un minuto (la página avisa). Abre tu tienda un rato antes de mostrársela a alguien.
- **Supabase gratis se pausa** tras una semana sin uso; se reactiva desde su panel.
- Si no cargan los productos y la consola del navegador (F12) dice "CORS", revisa que
  `FRONTEND_URL` sea exactamente la dirección de Vercel.

## Probar en tu PC (opcional)
Backend (terminal dentro de `backend`):
```
pip install -r requirements.txt
set DATABASE_URL=postgresql://...      (Mac/Linux: export DATABASE_URL=...)
python app.py
```
Frontend (otra terminal dentro de `frontend`):
```
python -m http.server 8000
```
y abre http://127.0.0.1:8000
