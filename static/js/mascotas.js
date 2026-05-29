function accionRapidaMascota(id_mascota) {
    const form = document.createElement("form");
    form.method = "POST";
    form.action = `/mascotas/alimentar/${id_mascota}`;
    document.body.appendChild(form);
    form.submit();
}

function abrirModalMascota(id) {
  const modal = document.getElementById("modal-mascota-" + id);
  if (modal) {
    modal.style.display = "block";
  }
}

function cerrarModalMascota(id) {
  const modal = document.getElementById("modal-mascota-" + id);
  if (modal) {
    modal.style.display = "none";
  }
}

// Cerrar si clickea fuera del modal
window.onclick = function(event) {
  document.querySelectorAll(".modal-mascota").forEach(modal => {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });
};

function sinAcentos(str) {
    return str.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
}

// Filtro de búsqueda
document.getElementById("buscarItem").addEventListener("keyup", function() {
  let filtro = sinAcentos(this.value.toLowerCase());
  const cards = document.querySelectorAll("#mascotasGrid .mascota-card:not(.mensaje-vacio)");
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
  mensaje.style.display = coincidencias === 0 ? "block" : "none";
});