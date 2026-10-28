// Carrito y pago (antes carrito.php + eliminar_carrito.php + procesar_compra.php)
const contenido = document.getElementById("contenido");

function mostrarVacio() {
    contenido.innerHTML = `
        <section class="formulario carrito-triste">
            <p><strong>¡Uy! Tu carrito está vacío.</strong></p>
            <a href="index.html" class="boton-descarga" style="text-decoration: none;">Ir al catálogo</a>
        </section>`;
}

function mostrarCarrito(datos) {
    const filas = datos.items.map((item) => `
        <tr>
            <td>${esc(item.nombre)}</td>
            <td>${item.cantidad}</td>
            <td>$${dinero(item.precio)}</td>
            <td>$${dinero(item.subtotal)}</td>
            <td><a href="#" class="eliminar" data-id="${item.id_producto}">Quitar</a></td>
        </tr>`).join("");

    contenido.innerHTML = `
        <section class="carrito-tabla">
            <table>
                <thead>
                    <tr>
                        <th>Producto</th>
                        <th>Cantidad</th>
                        <th>Precio</th>
                        <th>Subtotal</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>${filas}</tbody>
            </table>
            <p class="total-carrito">Total: $${dinero(datos.total)}</p>
        </section>

        <section class="formulario">
            <h2>Finalizar compra</h2>
            <div id="error-compra" class="mensaje-error" hidden></div>
            <form id="form-compra">
                <label for="nombre">Nombre y apellido</label>
                <input type="text" id="nombre" name="nombre" maxlength="150" required>

                <label for="whatsapp">Número de WhatsApp (opcional)</label>
                <input type="text" id="whatsapp" name="whatsapp" pattern="[0-9]{8,15}"
                       title="Numero SIN ESPACIOS ej; 50366780311">

                <button type="submit" id="boton-pagar">Pagar y generar recibo</button>
            </form>
        </section>`;

    // Quitar un producto
    contenido.querySelectorAll(".eliminar").forEach((enlace) => {
        enlace.addEventListener("click", (evento) => {
            evento.preventDefault();
            const carrito = leerCarrito();
            delete carrito[enlace.dataset.id];
            guardarCarrito(carrito);
            cargarCarrito();
        });
    });

    document.getElementById("form-compra").addEventListener("submit", pagar);
}

async function cargarCarrito() {
    const carrito = leerCarrito();
    if (Object.keys(carrito).length === 0) return mostrarVacio();

    try {
        const datos = await api("/api/carrito", { method: "POST", body: { carrito } });

        // Si algún producto ya no existe, se quita del carrito guardado
        const vigente = {};
        datos.items.forEach((i) => { vigente[i.id_producto] = i.cantidad; });
        guardarCarrito(vigente);

        if (datos.items.length === 0) return mostrarVacio();
        mostrarCarrito(datos);
    } catch (error) {
        contenido.innerHTML = `<p class="mensaje-error">${esc(error.message)}</p>`;
    }
}

async function pagar(evento) {
    evento.preventDefault();
    const boton = document.getElementById("boton-pagar");
    const cajaError = document.getElementById("error-compra");
    cajaError.hidden = true;
    boton.disabled = true;
    boton.textContent = "Procesando...";

    try {
        const pedido = await api("/api/compra", {
            method: "POST",
            body: {
                carrito: leerCarrito(),
                nombre: document.getElementById("nombre").value.trim(),
                whatsapp: document.getElementById("whatsapp").value.trim(),
            },
        });

        // Se guarda para mostrarlo en recibo.html y se vacía el carrito
        sessionStorage.setItem("ultimo_pedido", JSON.stringify(pedido));
        guardarCarrito({});
        window.location.href = "recibo.html";
    } catch (error) {
        cajaError.textContent = error.message;
        cajaError.hidden = false;
        boton.disabled = false;
        boton.textContent = "Pagar y generar recibo";
    }
}

document.addEventListener("DOMContentLoaded", cargarCarrito);
