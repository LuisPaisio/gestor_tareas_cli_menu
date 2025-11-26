from gestor_inventario import GestorInventario
from colorama import Fore,Style

# Diccionario global de nombres bonitos
NOMBRES_BONITOS = {
    "manoizquierda": "Mano izquierda",
    "manoderecha": "Mano derecha",
    "cabeza": "Cabeza",
    "pecho": "Pecho",
    "pies": "Pies",
    "escudo": "Escudo"
}
class Usuario:
    def __init__(self, id_usuario, usuario, contraseña,
                xp_usuario=0, coin_usuario=0, vida_usuario=50,
                nivel_usuario=1, contador_50=0, descripcion=None, nombre_publico=None, foto_perfil=None, slots=None):
        self.id_usuario = id_usuario
        self.usuario = usuario
        self.contraseña = contraseña
        self.xp_usuario = xp_usuario
        self.coin_usuario = coin_usuario
        self.vida_usuario = vida_usuario
        self.nivel_usuario = nivel_usuario
        self.contador_50 = contador_50
        self.descripcion = descripcion
        self.nombre_publico = nombre_publico
        self.foto_perfil = foto_perfil
        
        #Inicializar slots si no se pasan
        self.slots = slots if slots is not None else {
            "Mano izquierda": None,
            "Mano derecha": None,
            "Cabeza": None,
            "Pecho": None,
            "Pies": None,
            "Escudo": None
        }

        self.gestor_inventario = GestorInventario(self)
        #self.item_equipado = None  # nuevo atributo para ítem equipado

    def to_dict(self):
        return {
            "id_usuario": self.id_usuario,
            "usuario": self.usuario,
            "contraseña": self.contraseña,
            "xp_usuario": self.xp_usuario,
            "coin_usuario": self.coin_usuario,
            "vida_usuario": self.vida_usuario,
            "nivel_usuario": self.nivel_usuario,
            "contador_50": self.contador_50,
            "descripcion": self.descripcion,
            "nombre_publico": self.nombre_publico,
            "foto_perfil": self.foto_perfil,
            "slots": self.slots
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id_usuario=data["id_usuario"],
            usuario=data["usuario"],
            contraseña=data["contraseña"],
            xp_usuario=data.get("xp_usuario", 0),
            coin_usuario=data.get("coin_usuario", 0),
            vida_usuario=data.get("vida_usuario", 50),
            nivel_usuario=data.get("nivel_usuario", 1),
            contador_50=data.get("contador_50", 0),
            descripcion=data.get("descripcion"),
            nombre_publico=data.get("nombre_publico"),
            foto_perfil=data.get("foto_perfil"),
            slots=data.get("slots")
        )

    # -------------------------------
    # Perfil
    # -------------------------------
    def ver_perfil(self):
        print(Fore.YELLOW + "\n--- Perfil del Usuario ---" + Style.RESET_ALL)
        print(f"Nombre público: {self.nombre_publico or self.usuario}")
        print(f"Salud: {self.vida_usuario}/50")
        print(f"Nivel: {self.nivel_usuario}")
        print(f"XP: {self.xp_usuario}")
        print(f"Coin: {self.coin_usuario}")
        print(f"Descripción: {self.descripcion or 'Sin Descripción'}")
        print(f"Foto: {self.foto_perfil or 'Sin Foto'}")

    def editar_perfil(self):
        self.ver_perfil()
        opcion = input("\n¿Desea modificar su perfil?(s/n): ")
        if opcion.lower() == "s":
            self.nombre_publico = input("Nombre Público: ").strip() or self.nombre_publico
            self.descripcion = input("Sobre mí: ").strip() or self.descripcion
            self.foto_perfil = input("Ingresa la URL de la imagen: ").strip() or self.foto_perfil
            print("\nPerfil actualizado exitosamente")
        else:
            print("\nOperación cancelada, volviendo al menú...")

    # -------------------------------
    # Inventario
    # -------------------------------
    def ver_inventario(self, tienda=None, enumerado=False):
        inventario = self.gestor_inventario.inventario_usuario()
        print(f"\nInventario de {self.nombre_publico or self.usuario}:")
        inventario.mostrar(tienda=None, enumerado=enumerado)  # fuerza tienda=None para no filtrar
        # ✅ Guardar el mapeo en el usuario
        self.enumeracion_items = inventario.enumeracion_items.copy()

    def equipar(self, indice):
        # ⚠️ Usar el mapeo guardado en Usuario, NO uno nuevo desde GestorInventario
        id_item = (self.enumeracion_items or {}).get(str(indice))
        if not id_item:
            print(Fore.RED + "⚠️ Opción inválida." + Style.RESET_ALL)
            return

        inventario = self.gestor_inventario.inventario_usuario()
        datos_item = inventario.items.get(str(id_item))
        if not datos_item:
            print(Fore.YELLOW + "⚠️ No tienes ese ítem en tu inventario." + Style.RESET_ALL)
            return

        if datos_item.get("tipo") != "equipable":
            print(Fore.YELLOW + "⚠️ Este ítem no se puede equipar, solo usar." + Style.RESET_ALL)
            return

        slot = datos_item.get("slot")
        if slot not in self.slots:
            print(Fore.RED + "⚠️ Slot inválido para este ítem." + Style.RESET_ALL)
            return

        self.slots[slot] = id_item
        print(Fore.GREEN + f"✅ {datos_item['nombre']} equipado en {slot}." + Style.RESET_ALL)
        self.gestor_usuario.actualizar_usuario(self)

    def desequipar(self, slot):
        # Normalizar el slot ingresado por el usuario
        slot_normalizado = slot.lower().replace(" ", "")
        if slot_normalizado not in self.slots:
            print(Fore.RED + "⚠️ Slot inválido." + Style.RESET_ALL)
            return

        id_item = self.slots[slot_normalizado]
        # Obtener nombre bonito para mostrar al usuario
        nombre_slot = NOMBRES_BONITOS.get(slot_normalizado, slot_normalizado)

        if id_item:
            inventario = self.gestor_inventario.inventario_usuario()
            datos_item = inventario.items.get(str(id_item))
            nombre_item = datos_item["nombre"] if datos_item else id_item
            print(Fore.GREEN + f"❎ Ítem {nombre_item} desequipado de {nombre_slot}." + Style.RESET_ALL)
            self.slots[slot_normalizado] = None
            self.gestor_usuario.actualizar_usuario(self)
        else:
            print(Fore.YELLOW + f"⚠️ No tienes ningún ítem equipado en {nombre_slot}." + Style.RESET_ALL)

    def usar_item(self, indice):
        id_item = (self.enumeracion_items or {}).get(str(indice))
        if not id_item:
            print(Fore.RED + "⚠️ Opción inválida." + Style.RESET_ALL)
            return

        inventario = self.gestor_inventario.inventario_usuario()
        datos_item = inventario.items.get(str(id_item))
        if not datos_item:
            print("⚠️ No tienes ese ítem en tu inventario.")
            return

        if datos_item.get("tipo") != "consumible":
            print("⚠️ Este ítem no se puede usar directamente, debes equiparlo.")
            return

        inventario.quitar_item(id_item, 1)
        print(f"💥 Usaste {datos_item['nombre']} → {datos_item['descripcion']}")
        if "vida" in datos_item['nombre'].lower():
            self.sumar_vida(20)
        elif "xp" in datos_item['nombre'].lower():
            self.sumar_xp(10)


    # -------------------------------
    # XP, Coins y Vida (sin prints)
    # -------------------------------
    def sumar_xp(self, xp):
        self.xp_usuario += xp

    def sumar_coins(self, coins):
        self.coin_usuario += coins

    def sumar_vida(self, vida):
        self.vida_usuario = min(50, self.vida_usuario + vida)

    def restar_vida(self, vida):
        self.vida_usuario -= vida
        if self.vida_usuario <= 0:
            self.vida_usuario = 0
            xp_perdido, coins_perdidos = 15, 10
            self.sumar_xp(-xp_perdido)
            self.sumar_coins(-coins_perdidos)
            # limpiar todos los slots en lugar de item_equipado
            for slot in self.slots:
                self.slots[slot] = None
            self.vida_usuario = 50

    def sumar_xp_coins(self, xp, coins):
        self.sumar_xp(xp)
        self.sumar_coins(coins)
