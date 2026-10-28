-- =========================================================
-- Base de datos de la tienda para SUPABASE (PostgreSQL)
-- Pégalo en Supabase -> SQL Editor -> New query -> Run
-- =========================================================

CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    precio NUMERIC(10,2) NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    whatsapp VARCHAR(20)
);

CREATE TABLE pedidos (
    id SERIAL PRIMARY KEY,
    id_cliente INTEGER NOT NULL REFERENCES clientes(id),
    total NUMERIC(10,2) NOT NULL,
    fecha TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE pedido_detalle (
    id SERIAL PRIMARY KEY,
    id_pedido INTEGER NOT NULL REFERENCES pedidos(id),
    id_producto INTEGER NOT NULL REFERENCES productos(id),
    nombre_producto VARCHAR(100) NOT NULL,
    cantidad INTEGER NOT NULL,
    precio_unitario NUMERIC(10,2) NOT NULL,
    subtotal NUMERIC(10,2) NOT NULL
);

-- ---------------------------------------------------------
-- SEGURIDAD: Supabase publica las tablas por una API abierta
-- si no tienen RLS. Con esto nadie de afuera puede leerlas ni
-- modificarlas; tu backend sí puede porque entra con la
-- contraseña de la base de datos.
-- ---------------------------------------------------------
ALTER TABLE productos       ENABLE ROW LEVEL SECURITY;
ALTER TABLE clientes        ENABLE ROW LEVEL SECURITY;
ALTER TABLE pedidos         ENABLE ROW LEVEL SECURITY;
ALTER TABLE pedido_detalle  ENABLE ROW LEVEL SECURITY;

-- ---------------------------------------------------------
-- PRODUCTOS: CAMBIA estos nombres y precios por los tuyos.
-- El orden importa: el 1.º usa imagenes/Jugo1.jpg, el 2.º Jugo2.jpg, etc.
-- ---------------------------------------------------------
INSERT INTO productos (nombre, precio, stock) VALUES
('Jamaica',  1.25, 50),
('Producto 2', 1.00, 50),
('Producto 3', 1.00, 50),
('Producto 4', 1.00, 50);
