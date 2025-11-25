from colorama import Fore, Style

class Inventario:
    def __init__(self, id_usuario, items=None):
        # items puede ser dict {id_item: cantidad} o {id_item: {nombre, descripcion, cantidad}}
        self.id_usuario = id_usuario
        self.items = items if items else {}

    # --- Métodos CRUD sobre items ---
    def agregar_item(self, item, cantidad=1):
        """Agrega un ítem al inventario."""
        id_item = str(item.id_item)
        if id_item in self.items:
            datos = self.items[id_item]
            if isinstance(datos, dict):
                datos["cantidad"] += cantidad
            else:
                self.items[id_item] += cantidad
        else:
            # siempre guardamos como dict enriquecido
            self.items[id_item] = {
                "nombre": item.nombre,
                "descripcion": item.descripcion,
                "cantidad": cantidad
            }

    def quitar_item(self, id_item, cantidad=1):
        """Quita unidades de un ítem del inventario."""
        id_item = str(id_item)
        if id_item in self.items:
            datos = self.items[id_item]
            if isinstance(datos, dict):
                datos["cantidad"] -= cantidad
                if datos["cantidad"] <= 0:
                    del self.items[id_item]
            else:
                self.items[id_item] -= cantidad
                if self.items[id_item] <= 0:
                    del self.items[id_item]

    def obtener_items(self):
        """Devuelve el dict crudo de items."""
        return self.items

    # --- Mostrar inventario ---
    def mostrar(self, tienda=None, enumerado=True):
        """Muestra el inventario con estilo similar a ver_tareas."""
        if not self.items:
            print(Fore.YELLOW + "\nInventario vacío." + Style.RESET_ALL)
            return

        print(Fore.YELLOW + "\n=== Inventario ===" + Style.RESET_ALL)

        inventario_lista = []
        for id_item, datos in self.items.items():
            cantidad = datos["cantidad"] if isinstance(datos, dict) else datos

            if tienda:
                item = next((i for i in tienda.items if i.id_item == int(id_item)), None)
                if item:
                    inventario_lista.append((item, cantidad))
            else:
                inventario_lista.append((id_item, cantidad))

        inventario_lista.sort(key=lambda x: x[0].nombre if tienda else str(x[0]))

        for contador, datos in enumerate(inventario_lista, start=1):
            if tienda:
                item, cantidad = datos
                print(f"{contador}. {item.nombre} - {cantidad} unidades | {item.descripcion}")
            else:
                id_item, cantidad = datos
                print(f"{contador}. Item {id_item} - {cantidad} unidades")
