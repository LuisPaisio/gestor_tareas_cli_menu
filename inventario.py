import json
import os
from colorama import Fore, Style

ARCHIVO_INVENTARIOS = os.path.join("json", "inventarios.json")

class Inventario:
    def __init__(self, id_usuario, items=None):
        """
        Inventario de un usuario.
        items es un dict con estructura:
        {id_item: {"nombre": str, "descripcion": str, "cantidad": int}}
        """
        self.id_usuario = id_usuario
        self.items = items if items else {}
        self.enumeracion_items = {}  # mapeo índice → id_item

    # --- Métodos CRUD sobre items ---
    def agregar_item(self, item, cantidad=1):
        """Agrega un ítem al inventario."""
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
                "efecto": getattr(item, "efecto", {})
            }

    def quitar_item(self, id_item, cantidad=1):
        """Quita unidades de un ítem del inventario."""
        id_item = str(id_item)
        if id_item in self.items:
            self.items[id_item]["cantidad"] -= cantidad
            if self.items[id_item]["cantidad"] <= 0:
                del self.items[id_item]

    def obtener_items(self):
        """Devuelve el dict crudo de items."""
        return self.items

    def existe_item(self, id_item):
        """Verifica si un ítem existe en el inventario."""
        return str(id_item) in self.items

    def obtener_item(self, id_item):
        """Devuelve los datos de un ítem específico."""
        return self.items.get(str(id_item))

    # --- Persistencia ---
    def to_dict(self):
        """Convierte el inventario a dict para guardar en JSON."""
        return {"id_usuario": self.id_usuario, "items": self.items}

    @staticmethod
    def from_dict(data):
        """Crea un inventario desde un dict cargado de JSON."""
        return Inventario(data["id_usuario"], data.get("items", {}))

    @staticmethod
    def cargar_inventarios():
        """Carga todos los inventarios desde el archivo JSON."""
        if os.path.exists(ARCHIVO_INVENTARIOS):
            try:
                with open(ARCHIVO_INVENTARIOS, "r", encoding="utf-8") as archivo:
                    contenido = archivo.read().strip()
                    if not contenido:
                        return []
                    data = json.loads(contenido)
                    return [Inventario.from_dict(inv) for inv in data]
            except json.JSONDecodeError:
                print(Fore.RED + "⚠️ El archivo de inventarios está corrupto. Se iniciará vacío." + Style.RESET_ALL)
                return []
        return []

    @staticmethod
    def guardar_inventarios(inventarios):
        """Guarda todos los inventarios en el archivo JSON."""
        with open(ARCHIVO_INVENTARIOS, "w", encoding="utf-8") as archivo:
            json.dump([inv.to_dict() for inv in inventarios], archivo, indent=4, ensure_ascii=False)

    # --- Mostrar inventario ---
    def mostrar(self, tienda=None, enumerado=True):
        if not self.items:
            print(Fore.YELLOW + "\nInventario vacío." + Style.RESET_ALL)
            return

        print(Fore.YELLOW + "\n=== Inventario ===" + Style.RESET_ALL)

        self.enumeracion_items = {}

        inventario_lista = []
        for id_item, datos in self.items.items():
            inventario_lista.append((id_item, datos["nombre"], datos["cantidad"], datos["descripcion"]))

        inventario_lista.sort(key=lambda x: x[1])  # ordenar por nombre

        for contador, (id_item, nombre, cantidad, descripcion) in enumerate(inventario_lista, start=1):
            print(f"{contador}. {nombre} - {cantidad} unidades | {descripcion}")
            self.enumeracion_items[str(contador)] = id_item




