from gestor_inventario import GestorInventario
from colorama import Fore, Style
from datetime import date, timedelta
import random
from item import Item
from constantes_tareas import vida_maxima, mana_maximo

# Diccionario global de nombres bonitos
NOMBRES_BONITOS = {
    "manoizquierda": "Mano izquierda",
    "manoderecha": "Mano derecha",
    "cabeza": "Cabeza",
    "pecho": "Pecho",
    "pies": "Pies",
    "escudo": "Escudo"
}

EXPLICACIONES_ATRIBUTOS = {
    "fuerza": "Aumenta la XP obtenida al completar tareas.",
    "defensa": "Reduce el daño recibido al marcar tareas como incompletas.",
    "velocidad": "Incrementa las Coins obtenidas al completar tareas."
}

class Usuario:
    def __init__(self, id_usuario, usuario, contraseña,
                xp_usuario=0, coin_usuario=0, vida_usuario=vida_maxima(),
                nivel_usuario=1, contador_100=0, descripcion=None,
                nombre_publico=None, foto_perfil=None, slots=None, rol="user", ventajas_vip = None, fuerza=0, defensa=0, velocidad=0, ultima_fecha_bonus = None, fecha_compra_vip=None, contador_vip = 0, tags=None, mana_usuario=0,
                fecha_expiracion_vip=None):
        self.id_usuario = id_usuario
        self.usuario = usuario
        self.contraseña = contraseña
        self.xp_usuario = xp_usuario
        self.coin_usuario = coin_usuario
        self.vida_usuario = vida_usuario
        self.nivel_usuario = nivel_usuario
        self.contador_100 = contador_100
        self.descripcion = descripcion
        self.nombre_publico = nombre_publico
        self.foto_perfil = foto_perfil
        self.rol = rol
        self.fuerza = int(fuerza or 0)
        self.defensa = int(defensa or 0)
        self.velocidad = int(velocidad or 0)
        self.ultima_fecha_bonus = ultima_fecha_bonus or None
        self.fecha_compra_vip = fecha_compra_vip or None
        self.contador_vip = contador_vip
        self.tags = tags if tags is not None else []
        self.mana_usuario = mana_usuario
        self.fecha_expiracion_vip = fecha_expiracion_vip or None

        # Inicializar slots normalizados si no se pasan
        self.slots = slots if slots is not None else {
            "manoizquierda": None,
            "manoderecha": None,
            "cabeza": None,
            "pecho": None,
            "pies": None,
            "escudo": None
        }

        # Inicializar ventajas VIP solo si el rol es vip
        if rol == "vip":
            self.ventajas_vip = ventajas_vip if ventajas_vip is not None else {
                "bonus_xp": 0.2,
                "bonus_coins": 0.2,
                "buff_defensa": 5,
                "buff_velocidad": 5,
                "buff_fuerza": 5,
                "bonus_diario": 15
            }
        else:
            self.ventajas_vip = None
        
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
            "contador_100": self.contador_100,
            "descripcion": self.descripcion,
            "nombre_publico": self.nombre_publico,
            "foto_perfil": self.foto_perfil,
            "slots": self.slots,
            "rol": self.rol,
            "ventajas_vip": self.ventajas_vip,
            "fuerza": self.fuerza,
            "defensa": self.defensa,
            "velocidad": self.velocidad,
            "ultima_fecha_bonus": self.ultima_fecha_bonus,
            "fecha_compra_vip": self.fecha_compra_vip,
            "contador_vip": self.contador_vip,
            "tags": self.tags,
            "mana_usuario": self.mana_usuario,
            "fecha_expiracion_vip": self.fecha_expiracion_vip
        }

    @staticmethod
    def safe_value(value, default=0):
        # Si es lista anidada, tomar el primer valor válido
        while isinstance(value, list) and value:
            value = value[0]
        return value if value is not None else default

    @classmethod
    def from_dict(cls, data):
        return cls(
            id_usuario=data["id_usuario"],
            usuario=data["usuario"],
            contraseña=data["contraseña"],
            xp_usuario=data.get("xp_usuario", 0),
            coin_usuario=data.get("coin_usuario", 0),
            vida_usuario=data.get("vida_usuario", vida_maxima()),
            nivel_usuario=data.get("nivel_usuario", 1),
            contador_100=data.get("contador_100", 0),
            descripcion=data.get("descripcion"),
            nombre_publico=data.get("nombre_publico"),
            foto_perfil=data.get("foto_perfil"),
            slots=data.get("slots"),
            rol=data.get("rol", "user"), # Default User si no está en JSON
            ventajas_vip=data.get("ventajas_vip"),
            fuerza=int(data.get("fuerza", 0)),
            defensa=int(data.get("defensa", 0)),
            velocidad=int(data.get("velocidad", 0)),
            ultima_fecha_bonus=str(data.get("ultima_fecha_bonus")) if data.get("ultima_fecha_bonus") else None,
            fecha_compra_vip=data.get("fecha_compra_vip"),
            contador_vip=data.get("contador_vip", 0),
            tags=data.get("tags", []),
            mana_usuario=data.get("mana_usuario", 0),
            fecha_expiracion_vip=data.get("fecha_expiracion_vip")
        )

    # -------------------------------
    # Perfil
    # -------------------------------
    def ver_perfil(self):
        print(Fore.YELLOW + "\n--- Perfil del Usuario ---" + Style.RESET_ALL)
        print(f"Nombre público: {self.nombre_con_tags()}")
        print(f"Salud: {self.vida_usuario}/50")
        print(f"Nivel: {self.nivel_usuario}")
        print(f"XP: {self.xp_usuario}")
        print(f"Coin: {self.coin_usuario}")
        print(f"Descripción: {self.descripcion or 'Sin Descripción'}")
        print(f"Foto: {self.foto_perfil or 'Sin Foto'}")
        
        mejoras = self.atributos_totales()

        if mejoras or (self.rol == "vip" and self.ventajas_vip):
            print("Mejoras activas:")
            atributos_mostrar = set(mejoras.keys())

            if self.rol == "vip" and self.ventajas_vip:
                for buff_key in self.ventajas_vip:
                    if buff_key.startswith("buff_"):
                        atributo = buff_key.replace("buff_", "")
                        atributos_mostrar.add(atributo)

            orden = ["fuerza", "defensa", "velocidad"]
            for atributo in orden:
                if atributo in atributos_mostrar:
                    valor_base = mejoras.get(atributo, 0)
                    extra = ""
                    if self.rol == "vip" and self.ventajas_vip:
                        buff_key = f"buff_{atributo}"
                        if buff_key in self.ventajas_vip:
                            buff_valor = self.ventajas_vip[buff_key]
                            if valor_base > 0:
                                extra = f" (+{buff_valor} VIP)"
                            else:
                                extra = f" (+{buff_valor} VIP)"
                    if valor_base != 0 or extra:
                        explicacion = EXPLICACIONES_ATRIBUTOS.get(atributo, "")
                        print(f"  - {atributo}: +{valor_base}{extra} | " + Fore.CYAN + f"{explicacion}" + Style.RESET_ALL)
        else:
            print("Mejoras activas: Ninguna")




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
            
        if self.nivel_usuario == 100:
            print("🏆 Has alcanzado el nivel máximo (100).")
            opcion_lvl = input("🔄 ¿Deseas reiniciar tu nivel a 1 y obtener un tag especial? (s/n): ")
            if opcion_lvl.lower() == "s":
                self.reiniciar_nivel_100()
            elif opcion_lvl.lower() == "n":
                print("ℹ️ Puedes reiniciar tu nivel cuando lo desees desde tu perfil.")
            else:
                print(Fore.RED + "⚠️ Opción inválida." + Style.RESET_ALL)


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
        atributos = {}
        inventario = self.gestor_inventario.inventario_usuario()
        for slot, id_item in self.slots.items():
            if id_item is not None:
                datos_item = inventario.items.get(str(id_item))
                if datos_item and "efecto" in datos_item:
                    for clave, valor in datos_item["efecto"].items():
                        atributos[clave] = atributos.get(clave, 0) + valor
        return atributos


    #Bonus diario para VIPS
    def aplicar_bonus_diario(self):
        if self.rol == "vip" and self.ventajas_vip:
            bonus_diario = self.ventajas_vip.get("bonus_diario", 0)
            hoy = str(date.today())  # siempre string

            if bonus_diario > 0 and self.ultima_fecha_bonus != hoy:
                self.coin_usuario += bonus_diario
                self.ultima_fecha_bonus = hoy

                # Persistir el cambio en JSON
                if self.gestor_usuarios:
                    self.gestor_usuarios.actualizar_usuario(self)

                print(Fore.LIGHTYELLOW_EX + "\n🎁 ¡Recompensa diaria VIP!" + Style.RESET_ALL)
                print(Fore.YELLOW + f"💰 +{bonus_diario} Coins (Bonus Diario)" + Style.RESET_ALL)
                print(Fore.LIGHTYELLOW_EX + "---------------------------------" + Style.RESET_ALL)
                print(Fore.LIGHTYELLOW_EX + f"📊 Estado actual → Nivel {self.nivel_usuario} | XP {self.xp_usuario} | Coins {self.coin_usuario} | Vida {self.vida_usuario}/50" + Style.RESET_ALL)

    #activo rango VIP
    def activar_vip(self):
        hoy = date.today()

        # Base de ventajas VIP
        base_vip = {
            "bonus_xp": 0.2,
            "bonus_coins": 0.2,
            "buff_defensa": 5,
            "buff_velocidad": 5,
            "buff_fuerza": 5,
            "bonus_diario": 15
        }

        # Si ya era VIP, verificamos continuidad
        if self.rol == "vip" and self.fecha_compra_vip:
            fecha_compra = date.fromisoformat(self.fecha_compra_vip)
            fecha_expira = fecha_compra + timedelta(days=30)
            dias_restantes = (fecha_expira - hoy).days

            if dias_restantes > 5:
                print(Fore.YELLOW + f"⚠️ Todavía faltan {dias_restantes} días para que expire tu VIP. Solo puedes renovarlo cuando falten 5 días o menos." + Style.RESET_ALL)
                return

            # Renovación dentro de la ventana → cadena continua
            self.contador_vip = getattr(self, "contador_vip", 0) + 1
        else:
            # Primera activación o cadena cortada
            self.contador_vip = 1

        # Activar rol y ventajas
        self.rol = "vip"
        if not self.ventajas_vip:
            self.ventajas_vip = base_vip
        else:
            for k, v in base_vip.items():
                self.ventajas_vip.setdefault(k, v)

        # Ajustar atributos base
        self.fuerza = max(self.fuerza, self.ventajas_vip["buff_fuerza"])
        self.defensa = max(self.defensa, self.ventajas_vip["buff_defensa"])
        self.velocidad = max(self.velocidad, self.ventajas_vip["buff_velocidad"])

        # Actualizar fechas
        self.fecha_compra_vip = hoy.isoformat()
        self.fecha_expiracion_vip = (hoy + timedelta(days=30)).isoformat()

        # --- Recompensas VIP según mes consecutivo ---
        self.dar_recompensa_vip()

        # Persistir cambios
        if self.gestor_usuarios:
            self.gestor_usuarios.actualizar_usuario(self)

        print(Fore.GREEN + f"🌟 ¡Felicitaciones! Ahora eres VIP (Mes {self.contador_vip} consecutivo)." + Style.RESET_ALL)

    #Desactivo rango VIP

    def desactivar_vip(self):
        if self.rol != "vip":
            print(Fore.YELLOW + "⚠️ El usuario no es VIP, no hay nada que desactivar." + Style.RESET_ALL)
            return

        # Resetear rol y ventajas
        self.rol = "user"
        self.ventajas_vip = None
        self.fecha_compra_vip = None
        self.fecha_expiracion_vip = None   # 🔹 limpiar también

        # Reiniciar atributos a valores base
        self.fuerza = 0
        self.defensa = 0
        self.velocidad = 0

        if self.gestor_usuarios:
            self.gestor_usuarios.actualizar_usuario(self)

        print(Fore.CYAN + "🔄 Tu membresía VIP ha expirado. Puedes renovarla desde la Tienda." + Style.RESET_ALL)

    def verificar_vip(self):
        if self.rol == "vip" and self.fecha_expiracion_vip:
            fecha_expira = date.fromisoformat(self.fecha_expiracion_vip)
            if date.today() >= fecha_expira:
                self.desactivar_vip()

    #---------------------------------
    # Sistema de niveles - progresión
    #---------------------------------

    def xp_requerida(self, nivel=None):
        """
        Calcula la XP requerida para subir al siguiente nivel.
        Curva suavizada inspirada en Habitica:
        - Niveles 1–20: progresión más accesible (mitad de la fórmula base).
        - Niveles 21–50: progresión media (75% de la fórmula base).
        - Niveles 51–100: progresión completa (fórmula base).
        """
        if nivel is None:
            nivel = self.nivel_usuario

        base = 2 * (nivel ** 2) + 10 * nivel

        if nivel <= 20:
            return base // 2
        elif nivel <= 50:
            return int(base * 0.75)
        else:
            return base


    def subir_nivel(self):
        xp_req = self.xp_requerida()
        niveles_subidos = 0  # contador de niveles ganados en esta acción

        while self.xp_usuario >= xp_req and self.nivel_usuario < 100:
            self.xp_usuario -= xp_req
            self.nivel_usuario += 1
            niveles_subidos += 1
            self.vida_usuario = vida_maxima()  # función global

            # Desbloqueo de maná en nivel 10
            if self.nivel_usuario == 10:
                self.mana_usuario = mana_maximo()
                print(f"🔮 Has desbloqueado el atributo MANÁ ({self.mana_usuario}/{mana_maximo()}).")

            # Nivel máximo alcanzado
            if self.nivel_usuario == 100:
                print("🏆 Has alcanzado el nivel máximo (100).")
                opcion = input("🔄 ¿Deseas reiniciar tu nivel a 1 y obtener un tag especial? (s/n): ")
                if opcion.lower() == "s":
                    self.reiniciar_nivel_100()
                    # Mostrar nombre con tags después del reinicio
                    print(f"✨ Nuevo estado: {self.nombre_con_tags()}")
                else:
                    print("ℹ️ Puedes reiniciar tu nivel cuando lo desees desde tu perfil en el menú principal.")


            xp_req = self.xp_requerida()

        # Mostrar resumen si subió niveles
        if niveles_subidos > 0:
            print(f"🎉 ¡Has subido {niveles_subidos} niveles! Ahora eres nivel {self.nivel_usuario}.")
            print(f"✨ Vida restaurada: {self.vida_usuario}/{vida_maxima()}")

        # Mostrar progreso hacia el siguiente nivel
        if self.nivel_usuario < 100:
            xp_req = self.xp_requerida()
            print(f"📊 XP actual: {self.xp_usuario}/{xp_req} (para nivel {self.nivel_usuario + 1})")

    def reiniciar_nivel_100(self):
        if self.contador_100 < 3:
            self.nivel_usuario = 1
            self.xp_usuario = 0
            self.vida_usuario = vida_maxima()
            self.mana_usuario = 0
            self.contador_100 += 1

            inventario = self.gestor_inventario.inventario_usuario()
            catalogo = self.gestor_inventario.catalogo_items()

            if self.contador_100 < 3:
                # Elegir objeto aleatorio excluyendo el VIP
                posibles_items = [i for i in catalogo if i["id_item"] != 51]
                item_random = random.choice(posibles_items)

                # Crear instancia Item y agregar al inventario
                nuevo_item = Item.from_dict(item_random)
                inventario.agregar_item(nuevo_item)
                self.gestor_inventario.actualizar_inventario(inventario)

                print(f"🎁 Has recibido un objeto especial: {nuevo_item.nombre}")
                print("✨ Puedes equiparlo desde tu inventario si lo deseas.")

            else:
                # Tercera vez → dar Membresía VIP
                vip_item = next(i for i in catalogo if i["id_item"] == 51)
                nuevo_item = Item.from_dict(vip_item)
                inventario.agregar_item(nuevo_item)
                self.gestor_inventario.actualizar_inventario(inventario)

                # Activar rol VIP y fecha de expiración
                self.rol = "vip"
                self.fecha_compra_vip = date.today().isoformat()
                self.fecha_expiracion_vip = (date.today() + timedelta(days=30)).isoformat()

                print("🏆 ¡Has alcanzado el nivel 100 por tercera vez!")
                print("🎁 Has recibido la Membresía VIP equipada automáticamente.")
                print("✨ Disfrutarás de todas las ventajas VIP durante 30 días.")

            print(f"🔄 Reiniciaste tu nivel. Nuevo tag: {self.obtener_tag()}")
        else:
            print("⚠️ Ya alcanzaste el máximo de reinicios (3).")


    def obtener_tag(self):
        tags = []
        if self.rol == "vip":
            tags.append("[vip]")
        if self.contador_100 == 1:
            tags.append("[ascendido]")
        elif self.contador_100 == 2:
            tags.append("[legendario]")
        elif self.contador_100 == 3:
            tags.append("[eterno]")
        return "".join(tags)

    def nombre_con_tags(self):
        """
        Devuelve el nombre público (o usuario) acompañado de los tags acumulados.
        Ejemplo: [vip][ascendido]Luis
        """
        tags = self.obtener_tag()
        nombre = self.nombre_publico or self.usuario
        return Fore.YELLOW + f"{tags}" + Style.RESET_ALL + f"{nombre}" if tags else nombre


    # Recompensa VIP por meses de membresía.
    def dar_recompensa_vip(self):
        catalogo = self.gestor_inventario.catalogo_items()
        inventario = self.gestor_inventario.inventario_usuario()
        posibles_items = [i for i in catalogo if i["id_item"] != 51]  # excluir VIP

        # Seleccionar un item random (≠ VIP)
        item_random = random.choice(posibles_items)
        inventario.agregar_item(Item.from_dict(item_random))
        self.gestor_inventario.actualizar_inventario(inventario)

        if self.contador_vip == 1:
            print(Fore.MAGENTA + f"🎁 Recompensa VIP mes 1: {item_random['nombre']}" + Style.RESET_ALL)

        elif self.contador_vip == 2:
            print(Fore.MAGENTA + f"🎁 Recompensa VIP mes 2: {item_random['nombre']}" + Style.RESET_ALL)

        elif self.contador_vip == 3:
            # Extender VIP 30 días más (protegido)
            if self.fecha_expiracion_vip:
                fecha_expira = date.fromisoformat(self.fecha_expiracion_vip)
            else:
                fecha_expira = date.today()
            nueva_expira = fecha_expira + timedelta(days=30)
            self.fecha_expiracion_vip = nueva_expira.isoformat()

            print(Fore.MAGENTA + f"🎁 Recompensa VIP mes 3: {item_random['nombre']} + 30 días extra de VIP" + Style.RESET_ALL)

        elif self.contador_vip % 3 == 0:
            print(Fore.MAGENTA + f"🎁 Recompensa VIP mes {self.contador_vip}: {item_random['nombre']}" + Style.RESET_ALL)


