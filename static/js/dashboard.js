const modal = document.getElementById("modal");
const btn = document.getElementById("openModal");
const span = document.querySelector("#modal .close");
const form = document.getElementById("taskForm");
const tipoSelect = document.getElementById("tipo");
const habitoOptions = document.getElementById("habito-options");
const diasOptions = document.getElementById("dias-options");
const fechaOptions = document.getElementById("fecha-options");
// --- Lógica de filtrado ---
const searchInput = document.querySelector(".search-bar input[type='text']");
const searchSelect = document.querySelector(".search-bar select");
const searchForm = document.querySelector(".search-bar");

// función de filtrado
function filtrarTareas() {
    const texto = searchInput.value.toLowerCase();
    const tipo = searchSelect.value;

    document.querySelectorAll(".card").forEach(card => {
      const cardTitulo = card.querySelector("h3")?.textContent.toLowerCase() || "";

      // 👇 nunca ocultar la card de recompensas
      if (cardTitulo.includes("tienda") || cardTitulo.includes("recompensa")) {
        card.querySelectorAll(".tarea-item").forEach(item => {
          item.style.display = "flex"; // siempre visible
        });
        return;
      }

      card.querySelectorAll(".tarea-item").forEach(item => {
        const titulo = item.querySelector(".titulo")?.textContent.toLowerCase() || "";

        let coincideTexto = !texto || titulo.includes(texto);
        let coincideTipo = !tipo || cardTitulo.includes(tipo);

        if (coincideTexto && coincideTipo) {
          item.style.display = "flex";
        } else {
          item.style.display = "none";
        }
      });
    });
}

// filtrar al cambiar el select
searchSelect.addEventListener("change", filtrarTareas);

// filtrar mientras escribe
searchInput.addEventListener("keyup", filtrarTareas);

// abrir modal de creación
btn.onclick = () => {
    modal.style.display = "block";
    form.reset();
    tipoSelect.dispatchEvent(new Event("change"));
};

// cerrar modal de creación
span.onclick = () => {
    modal.style.display = "none";
    form.reset();
};

// interceptar submit con validaciones
form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const tipo = form.querySelector("select[name='tipo']").value;
    let valido = true;
    let mensajeError = "";

    if (tipo === "1") { // hábito
      const habito = form.querySelector("input[name='habito']:checked");
      if (!habito) {
        valido = false;
        mensajeError = "Debes seleccionar si el hábito es positivo, negativo o ambos.";
      }
    }

    if (tipo === "2") { // diaria
      const dias = form.querySelectorAll("input[name='dias']:checked");
      if (dias.length === 0) {
        valido = false;
        mensajeError = "Debes seleccionar al menos un día para la tarea diaria.";
      }
    }

    if (tipo === "3") { // pendiente
      const fecha = form.querySelector("input[name='fecha_vencimiento']").value;
      if (!fecha) {
        valido = false;
        mensajeError = "Debes ingresar una fecha de vencimiento para la tarea pendiente.";
      }
    }

    if (!valido) {
      alert(mensajeError);
      return;
    }

    // si todo está bien, enviar al backend
    const formData = new FormData(form);
    const response = await fetch(form.action, {
      method: "POST",
      body: formData
    });

    if (response.ok) {
      modal.style.display = "none";
      form.reset();
      location.reload();
    } else {
      alert("Error al guardar la tarea");
    }
});

// Mostrar/ocultar según tipo
tipoSelect.addEventListener("change", () => {
    habitoOptions.style.display = "none";
    diasOptions.style.display = "none";
    fechaOptions.style.display = "none";

    if (tipoSelect.value === "1") {
      habitoOptions.style.display = "block";
    } else if (tipoSelect.value === "2") {
      diasOptions.style.display = "block";
    } else if (tipoSelect.value === "3") {
      fechaOptions.style.display = "block";
    }
});

// Inputs rápidos en cada card
document.querySelectorAll(".card input[type='text']").forEach(input => {
    input.addEventListener("keypress", async (e) => {
      if (e.key === "Enter" && input.value.trim() !== "") {
        const titulo = input.value.trim();
        let tipo, extra = {};

        if (input.placeholder.includes("hábito")) {
          tipo = 1;
          extra = { habito: "+-", dificultad: 1 };
        } else if (input.placeholder.includes("diaria")) {
          tipo = 2;
          extra = { dias: ["lunes","martes","miercoles","jueves","viernes","sabado","domingo"], dificultad: 1 };
        } else if (input.placeholder.includes("pendiente")) {
          tipo = 3;
          const fecha = new Date();
          fecha.setDate(fecha.getDate() + 7);
          extra = { fecha_vencimiento: fecha.toISOString().split("T")[0], dificultad: 1 };
        }

        const data = new FormData();
        data.append("titulo", titulo);
        data.append("tipo", tipo);
        for (const [k,v] of Object.entries(extra)) {
          if (Array.isArray(v)) {
            v.forEach(d => data.append(k, d));
          } else {
            data.append(k, v);
          }
        }

        const response = await fetch("/nueva_tarea", { method: "POST", body: data });
        if (response.ok) {
          input.value = "";
          location.reload();
        } else {
          alert("Error al crear la tarea");
        }
      }
    });
});

function mostrarModalClase() {
    document.getElementById("modalClase").style.display = "block";
}
function cerrarModalClase() {
    document.getElementById("modalClase").style.display = "none";
}

function cerrarModalMuerte() {
    document.getElementById("modalMuerte").style.display = "none";
}

// Mostrar automáticamente el modal de tareas vencidas si el flag lo permite
window.onload = function() {
// Lógica para el modal de muerte
var muerteModal = document.getElementById("modalMuerte");
if (muerteModal && muerteModal.dataset.mostrar === "true") {
    muerteModal.style.display = "block";

    var closeBtn = muerteModal.querySelector(".close");
    if (closeBtn) {
      closeBtn.onclick = function() {
        cerrarModalMuerte();
      };
    }
}
// Lógica de tareas vencidas
var vencidasModal = document.getElementById("tareasVencidasModal");
if (vencidasModal && vencidasModal.dataset.mostrar === "true") {
    vencidasModal.style.display = "block";

    var closeBtn = vencidasModal.querySelector(".close");
    if (closeBtn) {
        closeBtn.onclick = async function() {
            vencidasModal.style.display = "none";
            const formVencidas = document.getElementById("formVencidas");
            const formData = new FormData(formVencidas);
            const response = await fetch(formVencidas.action, { method: "POST", body: formData });
            if (response.ok) location.reload();
        };
      }
    }
  };

// cierre con clic fuera del modal vencidas
window.onclick = function(event) {
    //Función para modal muerte.
    var muerteModal = document.getElementById("modalMuerte");
        if (event.target == muerteModal) {
          cerrarModalMuerte();
        }
      //Función para modal de tareas vencidas.
    var vencidasModal = document.getElementById("tareasVencidasModal");
    if (event.target == vencidasModal) {
      vencidasModal.style.display = "none";
      const formVencidas = document.getElementById("formVencidas");
      const formData = new FormData(formVencidas);
      fetch(formVencidas.action, { method: "POST", body: formData })
        .then(response => { if (response.ok) location.reload(); });
    }
    var modalEdicion = document.getElementById("modalEdicion");
    if (event.target == modalEdicion) {
      cerrarModalEdicion();
    }
};

// --- Modal de edición ---
function abrirModalEdicion(tarea) {
    const modalEdicion = document.getElementById("modalEdicion");
    if (!modalEdicion) return;   // seguridad por si no existe
    modalEdicion.style.display = "block";

    // Cargar datos en el formulario
    document.getElementById("edit-id").value = tarea.id;
    document.getElementById("edit-titulo").value = tarea.titulo;
    document.getElementById("formEditarTarea").action = `/editar_tarea/${tarea.id}`;

    // Resetear campos
    document.querySelectorAll("#edit-habito-options input[type=radio]").forEach(r => r.checked = false);
    document.querySelectorAll("#edit-dias-options input[type=checkbox]").forEach(c => c.checked = false);
    document.getElementById("edit-fecha").value = "";

    // Mostrar y rellenar campos según tipo
    if (tarea.tipo == 1) { // hábito
      document.getElementById("edit-habito-options").style.display = "block";
      const radio = document.querySelector(`#edit-habito-options input[value="${tarea.habito}"]`);
      if (radio) radio.checked = true;
    } else {
      document.getElementById("edit-habito-options").style.display = "none";
    }

    if (tarea.tipo == 2) { // diaria
      document.getElementById("edit-dias-options").style.display = "block";
      if (tarea.dias) {
        tarea.dias.forEach(dia => {
          const checkbox = document.querySelector(`#edit-dias-options input[value="${dia}"]`);
          if (checkbox) checkbox.checked = true;
        });
      }
    } else {
      document.getElementById("edit-dias-options").style.display = "none";
    }

    if (tarea.tipo == 3) { // pendiente
      document.getElementById("edit-fecha-options").style.display = "block";
      if (tarea.fecha_vencimiento && tarea.fecha_vencimiento !== "Sin fecha") {
        document.getElementById("edit-fecha").value = tarea.fecha_vencimiento;
      }
    } else {
      document.getElementById("edit-fecha-options").style.display = "none";
    }
}

function cerrarModalEdicion() {
    const modalEdicion = document.getElementById("modalEdicion");
    if (modalEdicion) modalEdicion.style.display = "none";
}

async function eliminarTarea() {
    const id = document.getElementById("edit-id").value;
    if (!confirm("¿Seguro que deseas eliminar esta tarea?")) return;
    const response = await fetch(`/eliminar_tarea/${id}`, { method: "POST" });
    if (response.ok) {
      location.reload();
    } else {
      alert("Error al eliminar la tarea");
    }
}
