import json
import os
from utils_rutas import ruta_json

ARCHIVO_INVENTARIOS = ruta_json("inventarios.json")

class Inventario:
    def __init__(self, id_usuario, items=None):
        self.id_usuario = id_usuario
        self.items = items if items else {}
        self.enumeracion_items = {}

    # --- CRUD ---
    def agregar_item(self, item, cantidad=1):
        id_item = str(item.id_item)
        if id_item in self.items:
            self.items[id_item]["cantidad"] += cantidad
        else:
            self.items[id_item] = {
                "nombre": item.nombre,
                "descripcion": item.descripcion,
                "cantidad": cantidad,
                "tipo": getattr(item, "tipo", None),
                "slot": getattr(item, "slot", None),
                "efecto": getattr(item, "efecto", {}),
                "efecto_temporal": getattr(item, "efecto_temporal", {}),   # nuevo
                "efecto_turnos": getattr(item, "efecto_turnos", 0),        # nuevo
                "imagen": getattr(item, "imagen", "default.png")
            }

    def quitar_item(self, id_item, cantidad=1):
        id_item = str(id_item)
        if id_item in self.items:
            self.items[id_item]["cantidad"] -= cantidad
            if self.items[id_item]["cantidad"] <= 0:
                del self.items[id_item]

    def obtener_items(self):
        return self.items

    def existe_item(self, id_item):
        return str(id_item) in self.items

    def obtener_item(self, id_item):
        return self.items.get(str(id_item))

    # --- Persistencia ---
    def to_dict(self):
        return {"id_usuario": self.id_usuario, "items": self.items}

    @staticmethod
    def from_dict(data):
        return Inventario(data["id_usuario"], data.get("items", {}))

    @staticmethod
    def cargar_inventarios():
        if os.path.exists(ARCHIVO_INVENTARIOS):
            try:
                with open(ARCHIVO_INVENTARIOS, "r", encoding="utf-8") as archivo:
                    contenido = archivo.read().strip()
                    if not contenido:
                        return []
                    data = json.loads(contenido)
                    return [Inventario.from_dict(inv) for inv in data]
            except json.JSONDecodeError:
                return []
        return []

    @staticmethod
    def guardar_inventarios(inventarios):
        with open(ARCHIVO_INVENTARIOS, "w", encoding="utf-8") as archivo:
            json.dump([inv.to_dict() for inv in inventarios], archivo, indent=4, ensure_ascii=False)

    # --- Mostrar para web ---
    def mostrar_web(self):
        """Devuelve lista de items listos para renderizar en HTML."""
        inventario_lista = []
        for id_item, datos in self.items.items():
            inventario_lista.append({
                "id_item": int(id_item),
                "nombre": datos["nombre"],
                "descripcion": datos["descripcion"],
                "cantidad": datos["cantidad"],
                "tipo": datos.get("tipo"),
                "slot": datos.get("slot"),
                "efecto": datos.get("efecto", {}),
                "efecto_temporal": datos.get("efecto_temporal", {}),   # nuevo
                "efecto_turnos": datos.get("efecto_turnos", 0),        # nuevo
                "imagen": datos.get("imagen", "default.png")
            })
        inventario_lista.sort(key=lambda x: x["nombre"])
        return inventario_lista
