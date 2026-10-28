// Dirección del backend (la que te da Render al publicarlo, sin "/" al final).
// Cuando estás probando en tu PC usa el backend local automáticamente.
const API_URL = ["localhost", "127.0.0.1"].includes(location.hostname)
    ? "http://127.0.0.1:5000"
    : "https://CAMBIA-ESTO.onrender.com";
