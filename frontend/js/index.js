// Catálogo (antes index.php + agregar_carrito.php)
let temporizadorMensaje;

function mostrarMensajeExito() {
    const mensaje = document.getElementById("mensaje-exito");
    mensaje.hidden = false;
    clearTimeout(temporizadorMensaje);
    temporizadorMensaje = setTimeout(() => { mensaje.hidden = true; }, 2500);
}

function tarjetaProducto(p) {
    // Las fotos se llaman Jugo1.jpg ... Jugo4.jpg según el id del producto
    const imagen = [1, 2, 3, 4].includes(p.id)
        ? `<img src="imagenes/Jugo${p.id}.jpg" alt="${esc(p.nombre)}" class="producto-img">`
        : "";

    return `
        <div class="producto-card">
            ${imagen}
            <h3>${esc(p.nombre)}</h3>
            <p class="precio">$${dinero(p.precio)}</p>
            <p class="stock">Disponibles: ${p.stock}</p>

            <form class="form-agregar" data-id="${p.id}" data-stock="${p.stock}">
                <label>Cantidad</label>
                <input type="number" name="cantidad" min="1" max="${p.stock}" value="1">
                <button type="submit">Agregar al carrito</button>
            </form>
        </div>`;
}

function agregarAlCarrito(evento) {
    evento.preventDefault();
    const formulario = evento.target;
    const id = Number(formulario.dataset.id);
    const stock = Number(formulario.dataset.stock);
    const cantidad = parseInt(formulario.cantidad.value, 10);

    if (!(id > 0) || !(cantidad > 0)) return;

    const carrito = leerCarrito();
    // No deja agregar de más si no hay más en stock
    carrito[id] = Math.min((Number(carrito[id]) || 0) + cantidad, stock);
    guardarCarrito(carrito);

    actualizarContador();
    mostrarMensajeExito();
}

document.addEventListener("DOMContentLoaded", async () => {
    actualizarContador();
    const contenedor = document.getElementById("productos");

    try {
        const productos = await api("/api/productos");
        contenedor.innerHTML = productos.length
            ? productos.map(tarjetaProducto).join("")
            : "<p>No hay productos disponibles por ahora.</p>";
        contenedor.addEventListener("submit", agregarAlCarrito);
    } catch (error) {
        contenedor.innerHTML = `<p class="mensaje-error">${esc(error.message)}</p>`;
    }
});
