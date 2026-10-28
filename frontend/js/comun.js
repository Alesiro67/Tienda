// Funciones compartidas por todas las páginas.

// ---- Carrito: se guarda en el navegador con el formato { "id_producto": cantidad } ----
function leerCarrito() {
    try {
        const carrito = JSON.parse(localStorage.getItem("carrito") || "{}");
        return carrito && typeof carrito === "object" ? carrito : {};
    } catch (e) {
        return {};
    }
}

function guardarCarrito(carrito) {
    try {
        localStorage.setItem("carrito", JSON.stringify(carrito));
    } catch (e) { /* si el navegador no deja guardar, se ignora */ }
}

function contarUnidades() {
    return Object.values(leerCarrito()).reduce((suma, n) => suma + (Number(n) || 0), 0);
}

function actualizarContador() {
    const contador = document.getElementById("contador");
    if (contador) contador.textContent = contarUnidades();
}

// ---- Formato ----
// Equivale a number_format($n, 2) de PHP -> 1,234.50
function dinero(n) {
    return Number(n).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// Equivale a htmlspecialchars() de PHP: evita que un texto escrito por un
// cliente se interprete como HTML.
function esc(texto) {
    return String(texto).replace(/[&<>"']/g, (c) => (
        { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]
    ));
}

// ---- Comunicación con el backend ----
async function api(ruta, { method = "GET", body } = {}) {
    // El plan gratis de Render "duerme" el servidor: la primera visita puede tardar.
    const aviso = document.getElementById("aviso-servidor");
    const temporizador = setTimeout(() => { if (aviso) aviso.hidden = false; }, 4000);

    try {
        const respuesta = await fetch(API_URL + ruta, {
            method,
            headers: body ? { "Content-Type": "application/json" } : {},
            body: body ? JSON.stringify(body) : undefined,
        });
        let datos = {};
        try { datos = await respuesta.json(); } catch (e) { /* respuesta sin JSON */ }
        if (!respuesta.ok) throw new Error(datos.error || "Ocurrió un error en el servidor.");
        return datos;
    } catch (error) {
        if (error instanceof TypeError) {
            throw new Error("No se pudo conectar con el servidor. Intenta de nuevo en un momento.");
        }
        throw error;
    } finally {
        clearTimeout(temporizador);
        if (aviso) aviso.hidden = true;
    }
}
