function accionRapidaInventario(id_item, tipo, slot) {
    let url = "";
    if (tipo === "equipable") {
        if (equipado[slot] == id_item) {
            url = `/inventario/desequipar/${slot}`;
        } else {
            url = `/inventario/equipar/${id_item}`;
        }
    } else if (tipo === "consumible" || tipo === "consumible_vip") {
        url = `/inventario/usar/${id_item}`;
    }

    const form = document.createElement("form");
    form.method = "POST";
    form.action = url;
    document.body.appendChild(form);
    form.submit();
}

// Abrir modal de inventario
function mostrarModalInventario(id) {
  const modal = document.getElementById("modal-inventario-" + id);
  if (modal) {
    modal.style.display = "block";
  }
}

// Cerrar modal de inventario
function cerrarModalInventario(id) {
  const modal = document.getElementById("modal-inventario-" + id);
  if (modal) {
    modal.style.display = "none";
  }
}

// Cerrar si clickea fuera del modal
window.onclick = function(event) {
  document.querySelectorAll(".modal-inventario").forEach(modal => {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });
};
