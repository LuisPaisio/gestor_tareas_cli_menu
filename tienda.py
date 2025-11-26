import json
import os
from item import Item
from colorama import Fore, Style

ARCHIVO_ITEMS = os.path.join("json", "items.json")

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
                print(Fore.RED + "⚠️ El archivo de items está corrupto. Se iniciará vacío." + Style.RESET_ALL)
                return []
        return []

    def guardar_items(self):
        """Guarda el catálogo actual de la tienda en JSON."""
        with open(ARCHIVO_ITEMS, "w", encoding="utf-8") as archivo:
            json.dump([item.__dict__ for item in self.items], archivo, indent=4, ensure_ascii=False)

    # -------------------------------
    # Operaciones de la tienda
    # -------------------------------
    def mostrar_items(self):
        """Muestra el catálogo de la tienda."""
        if not self.items:
            print(Fore.YELLOW + "La tienda está vacía." + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + "\n=== Catálogo de la Tienda ===" + Style.RESET_ALL)
            for item in self.items:
                print(f"{item.id_item} - {item.nombre} ({item.precio} coins) | {item.descripcion}")

    def obtener_item(self, id_item):
        """Devuelve un ítem por su ID."""
        return next((i for i in self.items if i.id_item == id_item), None)

    def comprar_item(self, usuario, gestor_usuarios, id_item, cantidad=1):
        """Permite comprar un ítem de la tienda."""
        item = self.obtener_item(id_item)
        if not item:
            print(Fore.RED + "⚠️ Item no encontrado en la tienda." + Style.RESET_ALL)
            return

        inventario = usuario.gestor_inventario.inventario_usuario()

        # 🔹 Validar cantidad según tipo
        if getattr(item, "tipo", None) == "equipable":
            # Si ya existe en inventario, no permitir otra compra
            if str(item.id_item) in inventario.items:
                print(Fore.YELLOW + f"⚠️ Ya tienes '{item.nombre}' en tu inventario. No puedes comprar más de uno." + Style.RESET_ALL)
                return
            # Forzar cantidad a 1
            if cantidad > 1:
                print(Fore.YELLOW + f"⚠️ '{item.nombre}' es equipable, solo puedes comprar 1 unidad." + Style.RESET_ALL)
            cantidad = 1

        costo_total = item.precio * cantidad
        if usuario.coin_usuario < costo_total:
            print(Fore.RED + f"⚠️ No tenés suficientes coins. Necesitás {costo_total}, pero tenés {usuario.coin_usuario}." + Style.RESET_ALL)
            return

        # Actualizar coins e inventario
        usuario.coin_usuario -= costo_total
        inventario.agregar_item(item, cantidad)

        # Persistir cambios
        usuario.gestor_inventario.actualizar_inventario(inventario)
        gestor_usuarios.actualizar_usuario(usuario)

        print(Fore.GREEN + f"✅ Compraste {cantidad} '{item.nombre}'. Se agregó a tu inventario." + Style.RESET_ALL)

    def vender_item(self, usuario, gestor_usuarios):
        """Permite vender ítems del inventario a la tienda."""
        inventario = usuario.gestor_inventario.inventario_usuario()
        if not inventario.items:
            print(Fore.YELLOW + "Tu inventario está vacío." + Style.RESET_ALL)
            return

        # Construir lista ordenada de ítems (por nombre para consistencia)
        inventario_lista = []
        for id_item, datos_item in inventario.items.items():
            item = self.obtener_item(int(id_item))
            if item:
                cantidad_disp = datos_item["cantidad"]
                inventario_lista.append((id_item, item, cantidad_disp))

        inventario_lista.sort(key=lambda x: x[1].nombre)

        # Mostrar inventario enumerado
        print(Fore.YELLOW + "\n=== Inventario para vender ===" + Style.RESET_ALL)
        for idx, (_, item, cantidad_disp) in enumerate(inventario_lista, start=1):
            print(f"{idx}. {item.nombre} - {cantidad_disp} unidades | {item.descripcion}")

        try:
            seleccion = int(input("\nSelecciona el número del ítem a vender | 0 cancelar: "))
            if seleccion == 0:
                print(Fore.YELLOW + "Operación cancelada." + Style.RESET_ALL)
                return

            if 1 <= seleccion <= len(inventario_lista):
                id_item, item, cantidad_disp = inventario_lista[seleccion - 1]
                cantidad_vender = int(input(f"¿Cuántas unidades de '{item.nombre}' deseas vender?: "))

                if cantidad_vender <= 0 or cantidad_vender > cantidad_disp:
                    print(Fore.RED + "⚠️ Cantidad inválida." + Style.RESET_ALL)
                    return

                # Actualizar inventario y coins
                inventario.quitar_item(item.id_item, cantidad_vender)
                coins_ganados = int(item.precio * 0.5) * cantidad_vender
                usuario.coin_usuario += coins_ganados

                # 🔹 Si ya no queda ninguna unidad, limpiar slot si estaba equipado
                datos_item = inventario.items.get(str(item.id_item))
                if not datos_item:  # ítem ya no existe en inventario
                    for slot, equipado in usuario.slots.items():
                        if equipado == item.id_item:
                            usuario.slots[slot] = None
                            nombre_slot = NOMBRES_BONITOS.get(slot, slot)
                            print(Fore.YELLOW + f"❎ '{item.nombre}' estaba equipado en {nombre_slot} y fue removido al venderlo." + Style.RESET_ALL)

                # Persistir cambios
                usuario.gestor_inventario.actualizar_inventario(inventario)
                gestor_usuarios.actualizar_usuario(usuario)

                print(Fore.GREEN + f"✅ Vendiste {cantidad_vender} '{item.nombre}' y recibiste {coins_ganados} coins." + Style.RESET_ALL)
            else:
                print(Fore.RED + "⚠️ Selección inválida." + Style.RESET_ALL)

        except ValueError:
            print(Fore.RED + "⚠️ Entrada inválida. Por favor ingresa un número válido." + Style.RESET_ALL)


