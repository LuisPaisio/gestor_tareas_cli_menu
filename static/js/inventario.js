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