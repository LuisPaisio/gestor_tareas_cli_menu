document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("toast-container");
    const MAX_TOASTS = 4;

    function addToast(toast) {
        if (container.children.length >= MAX_TOASTS) {
        container.removeChild(container.firstElementChild);
        }
        container.appendChild(toast);

        // cerrar con animación al hacer click
        toast.addEventListener("click", () => {
        toast.classList.add("hide");
        toast.addEventListener("animationend", () => {
            toast.remove();
        }, { once: true });
        });

        // auto-remover al terminar animación fadeInOut
        toast.addEventListener("animationend", () => {
        if (!toast.classList.contains("hide")) {
            toast.remove();
        }
        });
    }

    Array.from(container.children).forEach(toast => {
        addToast(toast);
    });
});

    // Modal de Prestigio
function mostrarModalPrestigio() {
    document.getElementById("modalPrestigio").style.display = "block";
}
function cerrarModalPrestigio() {
    document.getElementById("modalPrestigio").style.display = "none";
}

    // Modal de Perfil
function mostrarModalPerfil() {
    document.getElementById("modalPerfil").style.display = "block";
    // por defecto mostrar vista de perfil
    document.getElementById("vistaVerPerfil").style.display = "block";
    document.getElementById("vistaEditarPerfil").style.display = "none";
}
function cerrarModalPerfil() {
    document.getElementById("modalPerfil").style.display = "none";
}

    // Alternar entre vistas dentro del modalPerfil
function mostrarVistaEditarPerfil() {
    document.getElementById("vistaVerPerfil").style.display = "none";
    document.getElementById("vistaEditarPerfil").style.display = "block";
}
function cancelarEdicionPerfil() {
    document.getElementById("vistaEditarPerfil").style.display = "none";
    document.getElementById("vistaVerPerfil").style.display = "block";
}

// Nuevo: Modal de Credenciales
function mostrarModalCredenciales() {
    document.getElementById("modalCredenciales").style.display = "block";
}
function cerrarModalCredenciales() {
     document.getElementById("modalCredenciales").style.display = "none";
}

function mostrarBloqueEliminar() {
    document.getElementById("bloqueEliminar").style.display = "block";
}

function ocultarBloqueEliminar() {
    document.getElementById("bloqueEliminar").style.display = "none";
}

function confirmarEliminacion() {
    return confirm("⚠️ Este proceso es irreversible. ¿Seguro que deseas eliminar tu cuenta?");
}