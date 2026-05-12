import json
import os
from item import Item
from datetime import date, timedelta
from utils_rutas import ruta_json

ARCHIVO_ITEMS = ruta_json("items.json")

NOMBRES_BONITOS = {
    "manoderecha": "Mano derecha",
    "manoizquierda": "Mano izquierda",
    "cabeza": "Cabeza",
    "pecho": "Pecho",
    "pies": "Pies",
    "escudo": "Escudo"
}

class Tienda:
    def __init__(self):
        self.items = self.cargar_items()

    # -------------------------------
    # Persistencia del catálogo
    # -------------------------------
    def cargar_items(self):
        """Carga los ítems disponibles desde JSON."""
        if os.path.exists(ARCHIVO_ITEMS):
            try:
                with open(ARCHIVO_ITEMS, "r", encoding="utf-8") as archivo:
                    contenido = archivo.read().strip()
                    if not contenido:
                        return []
                    data = json.loads(contenido)
                    return [Item(**item_data) for item_data in data]
            except json.JSONDecodeError:
                return []
        return []

    def guardar_items(self):
        """Guarda el catálogo actual de la tienda en JSON."""
        with open(ARCHIVO_ITEMS, "w", encoding="utf-8") as archivo:
            json.dump([item.to_dict() for item in self.items], archivo, indent=4, ensure_ascii=False)

    # -------------------------------
    # Operaciones de la tienda
    # -------------------------------
    def mostrar_items(self):
        """Devuelve directamente los objetos Item para Jinja."""
        return self.items

    def obtener_item(self, id_item):
        """Devuelve un objeto Item por su ID."""
        return next((i for i in self.items if i.id_item == id_item), None)

    def comprar_item(self, usuario, gestor_usuarios, id_item, cantidad=1):
        item_obj = self.obtener_item(id_item)
        if not item_obj:
            return "⚠️ Item no encontrado en la tienda."

        inventario = usuario.gestor_inventario.inventario_usuario()

        # Validar cantidad según tipo
        if item_obj.tipo == "equipable":
            if str(item_obj.id_item) in inventario.items:
                return f"⚠️ Ya tienes '{item_obj.nombre}' en tu inventario. No puedes comprar más de uno."
            if cantidad > 1:
                return f"⚠️ '{item_obj.nombre}' es equipable, solo puedes comprar 1 unidad."
            cantidad = 1

        if item_obj.tipo == "consumible_vip":
            # lógica VIP igual que antes...
            pass

        # Calcular costo
        costo_total = item_obj.precio * cantidad
        if usuario.coin_usuario < costo_total:
            return f"⚠️ No tenés suficientes coins. Necesitás {costo_total}, pero tenés {usuario.coin_usuario}."

        # Caso normal
        usuario.coin_usuario -= costo_total
        inventario.agregar_item(item_obj, cantidad)
        usuario.gestor_inventario.actualizar_inventario(inventario)
        gestor_usuarios.actualizar_usuario(usuario)
        return f"✅ Compraste {cantidad} '{item_obj.nombre}'. Se agregó a tu inventario."

    def vender_item(self, usuario, gestor_usuarios, id_item, cantidad_vender=1):
        """Permite vender ítems del inventario a la tienda desde la web."""
        inventario = usuario.gestor_inventario.inventario_usuario()
        if not inventario.items:
            return "⚠️ Tu inventario está vacío."

        datos_item = inventario.items.get(str(id_item))
        if not datos_item:
            return "⚠️ El ítem seleccionado no está en tu inventario."

        item_obj = self.obtener_item(id_item)
        if not item_obj:
            return "⚠️ Ítem no encontrado en la tienda."

        if item_obj.tipo == "consumible_vip":
            return "⚠️ No puedes vender la membresía VIP."

        cantidad_disp = datos_item["cantidad"]
        if cantidad_vender <= 0 or cantidad_vender > cantidad_disp:
            return "⚠️ Cantidad inválida."

        inventario.quitar_item(item_obj.id_item, cantidad_vender)
        coins_ganados = int(item_obj.precio * 0.5) * cantidad_vender
        usuario.coin_usuario += coins_ganados

        # limpiar slot si estaba equipado
        datos_item = inventario.items.get(str(item_obj.id_item))
        if not datos_item:
            for slot, equipado in usuario.slots.items():
                if str(equipado) == str(item_obj.id_item):
                    usuario.slots[slot] = None
                    nombre_slot = NOMBRES_BONITOS.get(slot, slot)
                    return f"❎ '{item_obj.nombre}' estaba equipado en {nombre_slot} y fue removido al venderlo. Recibiste {coins_ganados} coins."

        usuario.gestor_inventario.actualizar_inventario(inventario)
        gestor_usuarios.actualizar_usuario(usuario)

        return f"✅ Vendiste {cantidad_vender} '{item_obj.nombre}' y recibiste {coins_ganados} coins."
