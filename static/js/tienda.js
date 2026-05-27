// Filtro de búsqueda
function sinAcentos(str) {
    return str.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
}

document.getElementById("buscarItem").addEventListener("keyup", function() {
  let filtro = sinAcentos(this.value.toLowerCase());
  const cards = document.querySelectorAll("#catalogoGrid .item-card-tienda:not(.mensaje-vacio)");
  let coincidencias = 0;

  cards.forEach(card => {
    let texto = sinAcentos(card.innerText.toLowerCase());
    if (texto.includes(filtro)) {
      card.style.display = "flex";
      coincidencias++;
    } else {
      card.style.display = "none";
    }
  });

  const mensaje = document.getElementById("mensajeNoResultados");
  mensaje.style.display = coincidencias === 0 ? "flex" : "none";
});

// Abrir modal (catálogo o inventario)
function abrirModalTienda(id) {
  const modal = document.getElementById("modal-tienda-" + id) || document.getElementById("modal-tienda-vender-" + id);
  if (modal) {
    modal.style.display = "block";
  }
}

// Cerrar modal
function cerrarModalTienda(id) {
  const modal = document.getElementById("modal-tienda-" + id) || document.getElementById("modal-tienda-vender-" + id);
  if (modal) {
    modal.style.display = "none";
  }
}

// Cerrar si clickea fuera del modal
window.onclick = function(event) {
  document.querySelectorAll(".modal-tienda").forEach(modal => {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });
};
