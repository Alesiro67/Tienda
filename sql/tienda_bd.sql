-- =========================================================
-- Base de datos: tienda_bd
-- Proyecto: Feria de Emprendedurismo
-- =========================================================

CREATE DATABASE IF NOT EXISTS tienda_bd CHARACTER SET utf8mb4;
USE tienda_bd;

-- ---------------------------------------------------------
-- Productos disponibles en la tienda
-- ---------------------------------------------------------
CREATE TABLE productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0
);

-- ---------------------------------------------------------
-- Clientes que compran
-- ---------------------------------------------------------
CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    whatsapp VARCHAR(20)
);

-- ---------------------------------------------------------
-- Pedido = una compra completa (puede tener varios productos)
-- ---------------------------------------------------------
CREATE TABLE pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id)
);

-- ---------------------------------------------------------
-- Detalle del pedido = cada producto dentro de un pedido
-- ---------------------------------------------------------
CREATE TABLE pedido_detalle (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido INT NOT NULL,
    id_producto INT NOT NULL,
    nombre_producto VARCHAR(100) NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id),
    FOREIGN KEY (id_producto) REFERENCES productos(id)
);

-- ---------------------------------------------------------
-- Productos de ejemplo (ajusta nombres/precios a tu gusto)
-- ---------------------------------------------------------
INSERT INTO productos (nombre, precio, stock) VALUES
('Churros preparados', 1.50, 50),
('Pepinos con limón, sal y alguashte', 1.00, 50);
