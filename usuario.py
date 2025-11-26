from gestor_inventario import GestorInventario
from colorama import Fore, Style

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
                nivel_usuario=1, contador_50=0, descripcion=None,
                nombre_publico=None, foto_perfil=None, slots=None):
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

        # Inicializar slots normalizados si no se pasan
        self.slots = slots if slots is not None else {
            "manoizquierda": None,
            "manoderecha": None,
            "cabeza": None,
            "pecho": None,
            "pies": None,
            "escudo": None
        }

        self.gestor_inventario = GestorInventario(self)
        self.gestor_usuarios = None  # se asigna en register/login

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
        
        mejoras = self.atributos_totales()
        print("Mejoras activas:")
        for atributo, valor in mejoras.items():
            if valor != 0:
                print(f"  - {atributo}: +{valor}")
        print("Ninguna")


    def editar_perfil(self):
        self.ver_perfil()
        opcion = input("\n¿Desea modificar su perfil?(s/n): ")
        if opcion.lower() == "s":
            self.nombre_publico = input("Nombre Público: ").strip() or self.nombre_publico
            self.descripcion = input("Sobre mí: ").strip() or self.descripcion
            self.foto_perfil = input("Ingresa la URL de la imagen: ").strip() or self.foto_perfil
            print("\nPerfil actualizado exitosamente")
            if self.gestor_usuarios:
                self.gestor_usuarios.actualizar_usuario(self)
        else:
            print("\nOperación cancelada, volviendo al menú...")

    # -------------------------------
    # Inventario
    # -------------------------------
    def ver_inventario(self, tienda=None, enumerado=False):
        inventario = self.gestor_inventario.inventario_usuario()
        print(f"\nInventario de {self.nombre_publico or self.usuario}:")
        inventario.mostrar(tienda=None, enumerado=enumerado)
        self.enumeracion_items = inventario.enumeracion_items.copy()

    def equipar(self, indice):
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
        nombre_slot = NOMBRES_BONITOS.get(slot, slot)
        print(Fore.GREEN + f"✅ {datos_item['nombre']} equipado en {nombre_slot}." + Style.RESET_ALL)

        if self.gestor_usuarios:
            self.gestor_usuarios.actualizar_usuario(self)

    def desequipar(self, slot):
        slot_normalizado = slot.lower().replace(" ", "")
        if slot_normalizado not in self.slots:
            print(Fore.RED + "⚠️ Slot inválido." + Style.RESET_ALL)
            return

        id_item = self.slots[slot_normalizado]
        nombre_slot = NOMBRES_BONITOS.get(slot_normalizado, slot_normalizado)

        if id_item:
            inventario = self.gestor_inventario.inventario_usuario()
            datos_item = inventario.items.get(str(id_item))
            nombre_item = datos_item["nombre"] if datos_item else id_item

            print(Fore.GREEN + f"❎ Ítem {nombre_item} desequipado de {nombre_slot}." + Style.RESET_ALL)
            self.slots[slot_normalizado] = None

            if self.gestor_usuarios:
                self.gestor_usuarios.actualizar_usuario(self)
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
            print(Fore.YELLOW + "⚠️ No tienes ese ítem en tu inventario." + Style.RESET_ALL)
            return

        if datos_item.get("tipo") != "consumible":
            print(Fore.YELLOW + "⚠️ Este ítem no se puede usar directamente, debes equiparlo." + Style.RESET_ALL)
            return

        inventario.quitar_item(id_item, 1)
        print(Fore.GREEN + f"💥 Usaste {datos_item['nombre']} → {datos_item['descripcion']}" + Style.RESET_ALL)

        if "efecto" in datos_item:
            for clave, valor in datos_item["efecto"].items():
                if clave == "vida":
                    inicial = self.vida_usuario
                    self.sumar_vida(valor)
                    print(Fore.CYAN + f"❤️ HP: {inicial} → {self.vida_usuario}" + Style.RESET_ALL)
                elif clave == "xp":
                    inicial = self.xp_usuario
                    self.sumar_xp(valor)
                    print(Fore.CYAN + f"⭐ XP: {inicial} → {self.xp_usuario}" + Style.RESET_ALL)
                elif clave == "mana":
                    inicial = getattr(self, "mana_usuario", 0)
                    setattr(self, "mana_usuario", inicial + valor)
                    print(Fore.CYAN + f"🔮 Maná: {inicial} → {self.mana_usuario}" + Style.RESET_ALL)
                elif clave == "velocidad":
                    inicial = getattr(self, "velocidad_temporal", 0)
                    setattr(self, "velocidad_temporal", inicial + valor)
                    print(Fore.CYAN + f"⚡ Velocidad: {inicial} → {self.velocidad_temporal}" + Style.RESET_ALL)
                elif clave == "defensa_temporal":
                    inicial = getattr(self, "defensa_temporal", 0)
                    setattr(self, "defensa_temporal", inicial + valor)
                    print(Fore.CYAN + f"🛡️ Defensa temporal: {inicial} → {self.defensa_temporal}" + Style.RESET_ALL)

        if self.gestor_usuarios:
            self.gestor_usuarios.actualizar_usuario(self)


    # -------------------------------
    # XP, Coins y Vida
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
            # limpiar todos los slots
            for slot in self.slots:
                self.slots[slot] = None
            # reiniciar vida
            self.vida_usuario = 50

            # 🔹 Persistir cambios en usuarios.json
            if self.gestor_usuarios:
                self.gestor_usuarios.actualizar_usuario(self)

    def sumar_xp_coins(self, xp, coins):
        self.sumar_xp(xp)
        self.sumar_coins(coins)

        # 🔹 Persistir cambios en usuarios.json
        if self.gestor_usuarios:
            self.gestor_usuarios.actualizar_usuario(self)

    #--------------------------------
    # Atributos_totales, se calculan las mejoras activas
    #--------------------------------
    
    def atributos_totales(self):
        atributos = {"fuerza": 0, "defensa": 0, "mana": 0, "velocidad": 0, "vida": 0, "xp": 0}
        inventario = self.gestor_inventario.inventario_usuario()
        for slot, id_item in self.slots.items():
            if id_item:
                datos_item = inventario.items.get(str(id_item))
                if datos_item and "efecto" in datos_item:
                    for clave, valor in datos_item["efecto"].items():
                        atributos[clave] += valor
        return atributos
