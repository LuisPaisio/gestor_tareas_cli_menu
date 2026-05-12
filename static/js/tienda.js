// Filtro de búsqueda
document.getElementById("buscarItem").addEventListener("keyup", function() {
  let filtro = this.value.toLowerCase();
  document.querySelectorAll("#catalogoGrid .item-card-tienda").forEach(card => {
    let texto = card.innerText.toLowerCase();
    card.style.display = texto.includes(filtro) ? "flex" : "none";
  });
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
