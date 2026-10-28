// Recibo (antes recibo.php). Los datos vienen del pedido que acaba de guardar el backend.
document.addEventListener("DOMContentLoaded", () => {
    let pedido = null;
    try {
        pedido = JSON.parse(sessionStorage.getItem("ultimo_pedido"));
    } catch (e) { /* sin datos */ }

    // Si no hay compra reciente, se regresa al catálogo
    if (!pedido) {
        window.location.href = "index.html";
        return;
    }

    const folio = String(pedido.id).padStart(6, "0");

    // Mensaje predefinido para el enlace de WhatsApp (Click to Chat)
    const lista = pedido.items
        .map((i) => `${i.cantidad}x ${i.nombre} ($${dinero(i.subtotal)})\n`)
        .join("");
    const mensaje =
        `Hola ${pedido.nombre} Aqui esta tu recibo (muestra este ticket a la hora de comprar tu producto):\n\n` +
        `Pedido No. ${folio}\n${lista}\nTotal: $${dinero(pedido.total)}\n\nGracias por tu compra!`;

    const numero = (pedido.whatsapp || "").replace(/\D/g, "");
    const enlaceWhatsapp = numero
        ? `https://wa.me/${numero}?text=${encodeURIComponent(mensaje)}`
        : "";

    const filas = pedido.items.map((i) => `
        <tr>
            <td>${i.cantidad}x ${esc(i.nombre)}</td>
            <td>$${dinero(i.subtotal)}</td>
        </tr>`).join("");

    document.getElementById("recibo").innerHTML = `
        <div class="recibo-ticket" id="ticket">
            <h2>Recibo o Ticket</h2>
            <p>Recibo No. ${folio}</p>
            <p>${esc(pedido.fecha)}</p>
            <p><strong>Cliente:</strong> ${esc(pedido.nombre)}</p>
            <hr>
            <table class="tabla-ticket">${filas}</table>
            <hr>
            <p class="total-ticket">TOTAL: $${dinero(pedido.total)}</p>
            <p class="aviso-ticket">Recibo informativo — no es un documento fiscal oficial.</p>
        </div>

        <div class="acciones-recibo no-imprimir">
            <a href="${pedido.recibo_png}" download="recibo_${folio}.png" class="boton-descarga">
                Descargar como imagen
            </a>
            <button type="button" id="boton-imprimir" class="boton-descarga boton-secundario">
                Guardar como PDF (imprimir)
            </button>
            ${enlaceWhatsapp ? `
            <a href="${enlaceWhatsapp}" target="_blank" rel="noopener" class="boton-descarga boton-whatsapp">
                Enviar por WhatsApp
            </a>` : ""}
            <br><br>
            <a href="index.html">← Volver al catálogo</a>
        </div>`;

    document.getElementById("boton-imprimir").addEventListener("click", () => window.print());
});
