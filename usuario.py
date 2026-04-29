from gestor_inventario import GestorInventario
from colorama import Fore, Style
import datetime
from datetime import date, timedelta
import random
from item import Item
from constantes_tareas import vida_maxima, mana_maximo
from clases import Clase
from notificaciones import Notificacion
from gestor_notificaciones import GestorNotificaciones

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
                nombre_publico=None, foto_perfil=None, slots=None, rol="user",
                ventajas_vip=None, fuerza=0, defensa=0, velocidad=0,
                ultima_fecha_bonus=None, fecha_compra_vip=None, contador_vip=0,
                tags=None, mana_usuario=0, fecha_expiracion_vip=None, clase_nombre=None, cooldown_equipamiento=None):
        
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

        # Buffs temporales para poderes
        self.buff_xp = 1
        self.buff_coins = 1

        # Inicializar slots
        self.slots = slots if slots is not None else {
            "manoizquierda": None,
            "manoderecha": None,
            "cabeza": None,
            "pecho": None,
            "pies": None,
            "escudo": None
        }

        # Inicializar ventajas VIP
        if rol == "vip":
            self.ventajas_vip = ventajas_vip if ventajas_vip is not None else {
                "bonus_xp": 0.2,
                "bonus_coins": 0.2,
                "buff_defensa": 5,
                "buff_velocidad": 5,
                "buff_fuerza": 5,
                "bonus_diario": 15,
                "bonus_mana": 0.8
            }
        else:
            self.ventajas_vip = None

        # Inicializar clase RPG
        self.clase_nombre = clase_nombre
        self.clase = Clase.cargar_clase(clase_nombre, self.rol == "vip") if clase_nombre else None
        
        #Cooldown de 3 minutos cuando el usuario pierde toda su HP, aquí se inicializa.
        self.cooldown_equipamiento = cooldown_equipamiento

        self.gestor_inventario = GestorInventario(self)
        self.gestor_usuarios = None

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
            "fecha_expiracion_vip": self.fecha_expiracion_vip,
            "clase_nombre": self.clase_nombre if self.clase_nombre else None,
            "cooldown_equipamiento": self.cooldown_equipamiento.strftime("%Y-%m-%d %H:%M:%S") 
            if isinstance(self.cooldown_equipamiento, (datetime.date, datetime.datetime)) 
            else self.cooldown_equipamiento
        }

    @staticmethod
    def safe_value(value, default=0):
        # Si es lista anidada, tomar el primer valor válido
        while isinstance(value, list) and value:
            value = value[0]
        return value if value is not None else default

    @classmethod
    def from_dict(cls, data):
        cooldown = data.get("cooldown_equipamiento")
        if cooldown:
            try:
                # convertir string ISO a datetime
                cooldown = datetime.datetime.strptime(cooldown, "%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                cooldown = None

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
            rol=data.get("rol", "user"),
            ventajas_vip=data.get("ventajas_vip"),
            fuerza=int(data.get("fuerza", 0)),
            defensa=int(data.get("defensa", 0)),
            velocidad=int(data.get("velocidad", 0)),
            ultima_fecha_bonus=data.get("ultima_fecha_bonus"),
            fecha_compra_vip=data.get("fecha_compra_vip"),
            contador_vip=data.get("contador_vip", 0),
            tags=data.get("tags", []),
            mana_usuario=data.get("mana_usuario", 0),
            fecha_expiracion_vip=data.get("fecha_expiracion_vip"),
            clase_nombre=data.get("clase_nombre", None),
            cooldown_equipamiento=cooldown
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

        # 🔹 Mostrar clase si nivel >= 10 y ya está asignada
        if self.nivel_usuario >= 10 and self.clase is not None:
            print(f"Clase: {self.clase.nombre}{' (VIP)' if self.rol == 'vip' else ''}")

            # Mostrar poderes de la clase con descripción
            if self.clase.poderes:
                print(Fore.YELLOW + "\n--- Poderes disponibles ---" + Style.RESET_ALL)
                for nombre_poder, datos in self.clase.poderes.items():
                    coste = datos.get("coste", 0)
                    descripcion = datos.get("descripcion", "Sin descripción")
                    print(f"🪄 {nombre_poder} (Coste: {coste} Maná) | " + Fore.CYAN + f"{descripcion}" + Style.RESET_ALL)

        mejoras = self.atributos_totales()

        if mejoras or (self.rol == "vip" and self.ventajas_vip):
            print("\nMejoras activas:")
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
                            extra = f" (+{buff_valor} VIP)"
                    if valor_base != 0 or extra:
                        explicacion = EXPLICACIONES_ATRIBUTOS.get(atributo, "")
                        print(f"  - {atributo}: +{valor_base}{extra} | "
                            + Fore.CYAN + f"{explicacion}" + Style.RESET_ALL)
        else:
            print("Mejoras activas: Ninguna")


    def editar_perfil(self):
        self.ver_perfil()
        opcion = input("\n¿Desea modificar su perfil?(s/n): ")

        if opcion.lower() == "s":
            self.nombre_publico = input("Nombre Público: ").strip() or self.nombre_publico
            self.descripcion = input("Sobre mí: ").strip() or self.descripcion
            self.foto_perfil = input("Ingresa la URL de la imagen: ").strip() or self.foto_perfil

            # Elegir o cambiar clase si nivel >= 10
            if self.nivel_usuario >= 10:
                if self.clase is None:
                    print(Fore.YELLOW + "\n✨ Aún no tienes clase asignada. Debes elegir una." + Style.RESET_ALL)
                    elegir_clase = "s"  # fuerza la elección inicial
                else:
                    elegir_clase = input("¿Deseas cambiar tu clase? (s/n): ")

                if elegir_clase.lower() == "s":
                    print("\nElige tu clase:")
                    opciones = ["Guerrero", "Sanador", "Mago", "Pícaro"]
                    for i, clase_nombre in enumerate(opciones, start=1):
                        clase_temp = Clase.cargar_clase(clase_nombre, self.rol == "vip")
                        print(f"{i}. {clase_nombre} → {clase_temp.descripcion}")

                    try:
                        seleccion = int(input("Ingresa el número de tu clase: "))
                        if 1 <= seleccion <= len(opciones):
                            clase_nombre = opciones[seleccion - 1]
                            self.clase = Clase.cargar_clase(clase_nombre, self.rol == "vip")
                            print(f"✨ Has elegido la clase {clase_nombre}.")
                        else:
                            print(Fore.RED + "⚠️ Selección inválida. No se cambió la clase." + Style.RESET_ALL)
                    except ValueError:
                        print(Fore.RED + "⚠️ Entrada inválida. No se cambió la clase." + Style.RESET_ALL)
            else:
                print(Fore.YELLOW + "ℹ️ Solo puedes elegir o cambiar tu clase a partir del nivel 10." + Style.RESET_ALL)

            print("\nPerfil actualizado exitosamente")
            if self.gestor_usuarios:
                self.gestor_usuarios.actualizar_usuario(self)
        else:
            print("\nOperación cancelada, volviendo al menú...")

            # 🔹 Si es nivel >= 10 y aún no tiene clase, forzar elección aunque no edite
            if self.nivel_usuario >= 10 and self.clase is None:
                print(Fore.YELLOW + "\n✨ Aún no tienes clase asignada. Debes elegir una." + Style.RESET_ALL)

                print("\nElige tu clase:")
                opciones = ["Guerrero", "Sanador", "Mago", "Pícaro"]
                for i, clase_nombre in enumerate(opciones, start=1):
                    clase_temp = Clase.cargar_clase(clase_nombre, self.rol == "vip")
                    print(f"{i}. {clase_nombre} → {clase_temp.descripcion}")

                try:
                    seleccion = int(input("Ingresa el número de tu clase: "))
                    if 1 <= seleccion <= len(opciones):
                        clase_nombre = opciones[seleccion - 1]
                        self.clase = Clase.cargar_clase(clase_nombre, self.rol == "vip")
                        print(f"✨ Has elegido la clase {clase_nombre}.")
                        if self.gestor_usuarios:
                            self.gestor_usuarios.actualizar_usuario(self)
                    else:
                        print(Fore.RED + "⚠️ Selección inválida. No se asignó clase." + Style.RESET_ALL)
                except ValueError:
                    print(Fore.RED + "⚠️ Entrada inválida. No se asignó clase." + Style.RESET_ALL)

        # Lógica de nivel 100
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
    def ver_inventario(self, tienda=None, enumerado=False, modo="todos"):
        inventario = self.gestor_inventario.inventario_usuario()
        print(Fore.YELLOW + f"\nInventario de " + Style.RESET_ALL + f"{self.nombre_con_tags()}"+ Fore.YELLOW + ":" + Style.RESET_ALL)

        # Filtrar según el modo
        if modo == "equipar":
            items_filtrados = {k:v for k,v in inventario.items.items()
                            if v.get("tipo") == "equipable"}
        elif modo == "usar":
            items_filtrados = {k:v for k,v in inventario.items.items()
                            if v.get("tipo") in ["consumible", "consumible_vip"]}
        else:
            items_filtrados = inventario.items  # todos

        # Mostrar ítems filtrados
        for idx, (id_item, datos) in enumerate(items_filtrados.items(), start=1):
            print(f"{idx}. {datos['nombre']} ({datos['tipo']})")

        # Guardar enumeración para equipar/usar
        self.enumeracion_items = {
            str(idx): id_item for idx, (id_item, _) in enumerate(items_filtrados.items(), start=1)
        }


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
        
        # En equipar recordar que debemos agregar el chequeo del cooldown (Recuerda ésto):
        #if self.cooldown_equipamiento and datetime.datetime.now() < self.cooldown_equipamiento:
        #    return {"error": "No puedes equipar objetos hasta que pasen 3 minutos tras tu muerte."}


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
        self.xp_usuario = max(0, self.xp_usuario + xp)

    def sumar_coins(self, coins):
        self.coin_usuario = max(0, self.coin_usuario + coins)

    def sumar_vida(self, vida):
        self.vida_usuario = min(50, self.vida_usuario + vida)

    def restar_vida(self, vida):
        self.vida_usuario -= vida
        if self.vida_usuario <= 0:
            self.vida_usuario = 0

            # Penalización porcentual
            xp_perdido = int(self.xp_usuario * 0.05)
            coins_perdidos = int(self.coin_usuario * 0.10)
            self.sumar_xp(-xp_perdido)
            self.sumar_coins(-coins_perdidos)

            # 🔹 Bajada de nivel automática
            if self.nivel_usuario > 1:
                self.nivel_usuario -= 1
                self.xp_usuario = self.xp_requerida(self.nivel_usuario) // 2

            # Desequipar
            for slot in self.slots:
                self.slots[slot] = None

            # Cooldown
            self.cooldown_equipamiento = datetime.datetime.now() + datetime.timedelta(minutes=3)

            # Reiniciar vida y maná
            self.vida_usuario = vida_maxima()
            self.mana_usuario = mana_maximo()

            if self.gestor_usuarios:
                self.gestor_usuarios.actualizar_usuario(self)

            return True  # 👈 devuelve flag de muerte

        return False

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


    # Bonus diario para VIPS
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

                # En vez de print, devolvemos un dict para usar en flash
                return {
                    "mensaje": f"🎁 ¡Recompensa diaria VIP! 💰 +{bonus_diario} Coins",
                    "categoria": "coins"
                }

        # Si no corresponde aplicar bonus, devolvemos None
        return None

    def activar_vip(self):
        hoy = date.today()
        gestor_notificaciones = GestorNotificaciones()

        base_vip = {
            "bonus_xp": 0.2,
            "bonus_coins": 0.2,
            "buff_defensa": 5,
            "buff_velocidad": 5,
            "buff_fuerza": 5,
            "bonus_diario": 15,
            "bonus_mana": 0.8
        }

        # Primera activación o renovación
        if self.rol != "vip":
            # Primera vez → contador arranca en 0
            self.contador_vip = 0
            # Dar recompensa inicial
            recompensa_inicial = {"accion": "vip_inicial", "mensaje": "🎁 Bienvenido al VIP: recibes 500 coins de regalo"}
            notif = Notificacion(
                id_notificacion=None,
                mensaje="🎁 Bienvenido al VIP: recibes 500 coins de regalo",
                accion="vip_inicial",
                fecha=date.today().isoformat(),
                leido=False
            )
            gestor_notificaciones.agregar_notificacion(self.id_usuario, notif)
            self.coin_usuario += 500
        else:
            recompensa_inicial = None

        # Activar rol y ventajas
        self.rol = "vip"
        self.ventajas_vip = {**base_vip, **self.ventajas_vip} if self.ventajas_vip else base_vip

        self.fuerza = max(self.fuerza, self.ventajas_vip["buff_fuerza"])
        self.defensa = max(self.defensa, self.ventajas_vip["buff_defensa"])
        self.velocidad = max(self.velocidad, self.ventajas_vip["buff_velocidad"])

        self.fecha_compra_vip = hoy.isoformat()
        self.fecha_expiracion_vip = (hoy + timedelta(days=30)).isoformat()

        if self.gestor_usuarios:
            self.gestor_usuarios.actualizar_usuario(self)

        eventos = []
        if recompensa_inicial:
            eventos.append(recompensa_inicial)
        eventos.append({
            "accion": "vip_activado",
            "mensaje": "🌟 ¡Felicitaciones! Ahora eres VIP. Mantén tu membresía activa para obtener recompensas mensuales adicionales."
        })
        notif = Notificacion(
            id_notificacion=None,
            mensaje="🌟 ¡Felicitaciones! Ahora eres VIP. Mantén tu membresía activa para obtener recompensas mensuales adicionales.",
            accion="vip_activado",
            fecha=date.today().isoformat(),
            leido=False
        )
        gestor_notificaciones.agregar_notificacion(self.id_usuario, notif)
        
        return eventos

    def desactivar_vip(self):
        gestor_notificaciones = GestorNotificaciones()
        
        if self.rol != "vip":
            notif = Notificacion(
                id_notificacion=None,
                mensaje="⚠️ El usuario no es VIP, no hay nada que desactivar.",
                accion="vip_info",
                fecha=date.today().isoformat(),
                leido=False
            )
            gestor_notificaciones.agregar_notificacion(self.id_usuario, notif)
            
            return [{"accion": "vip_info", "mensaje": "⚠️ El usuario no es VIP, no hay nada que desactivar."}]

        # Resetear rol y ventajas
        self.rol = "user"
        self.ventajas_vip = None
        self.fecha_compra_vip = None
        self.fecha_expiracion_vip = None

        # Reiniciar atributos a valores base
        self.fuerza = 0
        self.defensa = 0
        self.velocidad = 0

        if self.gestor_usuarios:
            self.gestor_usuarios.actualizar_usuario(self)
            
        notif = Notificacion(
            id_notificacion=None,
            mensaje="🔄 Tu membresía VIP ha expirado. Puedes renovarla desde la Tienda.",
            accion="vip_expirado",
            fecha=date.today().isoformat(),
            leido=False
        )
        gestor_notificaciones.agregar_notificacion(self.id_usuario, notif)

        return [{"accion": "vip_expirado", "mensaje": "🔄 Tu membresía VIP ha expirado. Puedes renovarla desde la Tienda."}]

    def verificar_vip(self):
        if self.rol == "vip" and self.fecha_expiracion_vip:
            fecha_expira = date.fromisoformat(self.fecha_expiracion_vip)
            if date.today() >= fecha_expira:
                return self.desactivar_vip()
        return []

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
        niveles_subidos = 0
        eventos = []  # lista de eventos para mostrar en la web
        gestor_notificaciones = GestorNotificaciones()

        while self.xp_usuario >= xp_req and self.nivel_usuario < 100:
            self.xp_usuario -= xp_req
            self.nivel_usuario += 1
            niveles_subidos += 1
            self.vida_usuario = vida_maxima()
            self.mana_usuario = mana_maximo()

            # Nivel 10 → desbloqueo de maná y elección de clase
            if self.nivel_usuario == 10:
                self.mana_usuario = mana_maximo()
                eventos.append({
                    "accion": "mana_desbloqueado",
                    "mensaje": f"🔮 Has desbloqueado el atributo MANÁ ({self.mana_usuario}/{mana_maximo()} MP)."
                })
                notif = Notificacion(
                    id_notificacion=None,
                    mensaje=f"🔮 Has desbloqueado el atributo MANÁ ({self.mana_usuario}/{mana_maximo()} MP).",
                    accion="mana_desbloqueado",
                    fecha=date.today().isoformat(),
                    leido=False
                )
                gestor_notificaciones.agregar_notificacion(self.id_usuario, notif)
                if not self.clase:
                    eventos.append({
                        "accion": "elegir_clase",
                        "mensaje": "✨ Debes elegir una clase para comenzar a usar poderes."
                    })
                    notif = Notificacion(
                        id_notificacion=None,
                        mensaje="✨ Debes elegir una clase para comenzar a usar poderes.",
                        accion="elegir_clase",
                        fecha=date.today().isoformat(),
                        leido=False
                    )
                    gestor_notificaciones.agregar_notificacion(self.id_usuario, notif)

            # Nivel 100 → prestigio disponible
            if self.nivel_usuario == 100:
                eventos.append({
                    "accion": "prestigio_disponible",
                    "mensaje": "🏆 Has alcanzado el nivel máximo (100). Puedes reiniciar tu nivel a 1 y obtener un tag especial."
                })
                notif = Notificacion(
                    id_notificacion=None,
                    mensaje="🏆 Has alcanzado el nivel máximo (100). Puedes reiniciar tu nivel a 1 y obtener un tag especial.",
                    accion="prestigio_disponible",
                    fecha=date.today().isoformat(),
                    leido=False
                )
                gestor_notificaciones.agregar_notificacion(self.id_usuario, notif)

            xp_req = self.xp_requerida()

        # Resumen si subió niveles
        if niveles_subidos > 0:
            eventos.append({
                "accion": "nivel_subido",
                "mensaje": f"🎉 ¡Has subido {niveles_subidos} niveles! Ahora eres nivel {self.nivel_usuario}."
            })

        # Progreso hacia el siguiente nivel
        if self.nivel_usuario < 100:
            xp_req = self.xp_requerida()
            eventos.append({
                "accion": "progreso",
                "mensaje": f"📊 XP actual: {self.xp_usuario}/{xp_req} (para nivel {self.nivel_usuario + 1})"
            })

        return eventos

    def reiniciar_nivel_100(self):
        eventos = []

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

                nuevo_item = Item.from_dict(item_random)
                inventario.agregar_item(nuevo_item)
                self.gestor_inventario.actualizar_inventario(inventario)

                eventos.append({
                    "accion": "prestigio",
                    "mensaje": f"🎁 Has recibido un objeto especial: {nuevo_item.nombre}. Puedes equiparlo desde tu inventario."
                })
                notif = Notificacion(
                    id_notificacion=None,
                    mensaje=f"🎁 Has recibido un objeto especial: {nuevo_item.nombre}. Puedes equiparlo desde tu inventario.",
                    accion="prestigio",
                    fecha=date.today().isoformat(),
                    leido=False
                )
                gestor_notificaciones.agregar_notificacion(self.id_usuario, notif)
            else:
                # Tercera vez → dar Membresía VIP
                vip_item = next(i for i in catalogo if i["id_item"] == 51)
                nuevo_item = Item.from_dict(vip_item)
                inventario.agregar_item(nuevo_item)
                self.gestor_inventario.actualizar_inventario(inventario)

                self.rol = "vip"
                self.fecha_compra_vip = date.today().isoformat()
                self.fecha_expiracion_vip = (date.today() + timedelta(days=30)).isoformat()

                eventos.append({
                    "accion": "prestigio",
                    "mensaje": "🏆 ¡Has alcanzado el nivel 100 por tercera vez! 🎁 Has recibido la Membresía VIP equipada automáticamente. ✨ Disfrutarás de todas las ventajas VIP durante 30 días."
                })
                notif = Notificacion(
                    id_notificacion=None,
                    mensaje="🏆 ¡Has alcanzado el nivel 100 por tercera vez! 🎁 Has recibido la Membresía VIP equipada automáticamente. ✨ Disfrutarás de todas las ventajas VIP durante 30 días.",
                    accion="prestigio",
                    fecha=date.today().isoformat(),
                    leido=False
                )
                gestor_notificaciones.agregar_notificacion(self.id_usuario, notif)

            eventos.append({
                "accion": "prestigio",
                "mensaje": f"🔄 Reiniciaste tu nivel. Nuevo tag: {self.obtener_tag()}"
            })
            notif = Notificacion(
                id_notificacion=None,
                mensaje=f"🔄 Reiniciaste tu nivel. Nuevo tag: {self.obtener_tag()}",
                accion="prestigio",
                fecha=date.today().isoformat(),
                leido=False
            )
            gestor_notificaciones.agregar_notificacion(self.id_usuario, notif)
        else:
            eventos.append({
                "accion": "prestigio",
                "mensaje": "⚠️ Ya alcanzaste el máximo de reinicios (3)."
            })
            notif = Notificacion(
                id_notificacion=None,
                mensaje="⚠️ Ya alcanzaste el máximo de reinicios (3).",
                accion="prestigio",
                fecha=date.today().isoformat(),
                leido=False
            )
            gestor_notificaciones.agregar_notificacion(self.id_usuario, notif)

        return eventos

    def obtener_tag(self):
        tags = []
        if self.rol == "vip":
            tags.append('<span class="tag vip">[vip]</span>')
        if self.contador_100 == 1:
            tags.append('<span class="tag ascendido">[ascendido]</span>')
        elif self.contador_100 == 2:
            tags.append('<span class="tag legendario">[legendario]</span>')
        elif self.contador_100 == 3:
            tags.append('<span class="tag eterno">[eterno]</span>')
        return "".join(tags)

    def nombre_con_tags(self):
        nombre = self.nombre_publico or self.usuario
        tags = self.obtener_tag()
        return f"{tags}{nombre}" if tags else nombre

    def dar_recompensa_vip(self):
        eventos = []
        hoy = date.today()

        if not self.fecha_compra_vip:
            return eventos

        # Calcular meses transcurridos desde la compra
        fecha_compra = date.fromisoformat(self.fecha_compra_vip)
        meses_transcurridos = (hoy.year - fecha_compra.year) * 12 + (hoy.month - fecha_compra.month)

        # Solo dar recompensa si contador_vip < meses_transcurridos
        if self.contador_vip < meses_transcurridos:
            self.contador_vip += 1

            catalogo = self.gestor_inventario.catalogo_items()
            inventario = self.gestor_inventario.inventario_usuario()
            posibles_items = [i for i in catalogo if i["id_item"] != 51]  # excluir VIP

            item_random = random.choice(posibles_items)
            inventario.agregar_item(Item.from_dict(item_random))
            self.gestor_inventario.actualizar_inventario(inventario)

            # Mensajes según el mes
            if self.contador_vip == 1:
                eventos.append({"accion": "vip_recompensa", "mensaje": f"🎁 Recompensa VIP mes 1: {item_random['nombre']}"})
                notif = Notificacion(
                    id_notificacion=None,
                    mensaje=f"🎁 Recompensa VIP mes 1: {item_random['nombre']}",
                    accion="vip_recompensa",
                    fecha=date.today().isoformat(),
                    leido=False
                )
                gestor_notificaciones.agregar_notificacion(self.id_usuario, notif)
            elif self.contador_vip == 2:
                eventos.append({"accion": "vip_recompensa", "mensaje": f"🎁 Recompensa VIP mes 2: {item_random['nombre']}"})
                notif = Notificacion(
                    id_notificacion=None,
                    mensaje=f"🎁 Recompensa VIP mes 2: {item_random['nombre']}",
                    accion="vip_recompensa",
                    fecha=date.today().isoformat(),
                    leido=False
                )
                gestor_notificaciones.agregar_notificacion(self.id_usuario, notif)
            elif self.contador_vip == 3:
                # Extender VIP 30 días más
                fecha_expira = date.fromisoformat(self.fecha_expiracion_vip) if self.fecha_expiracion_vip else hoy
                nueva_expira = fecha_expira + timedelta(days=30)
                self.fecha_expiracion_vip = nueva_expira.isoformat()
                eventos.append({"accion": "vip_recompensa", "mensaje": f"🎁 Recompensa VIP mes 3: {item_random['nombre']} + 30 días extra de VIP"})
                notif = Notificacion(
                    id_notificacion=None,
                    mensaje=f"🎁 Recompensa VIP mes 3: {item_random['nombre']} + 30 días extra de VIP",
                    accion="vip_recompensa",
                    fecha=date.today().isoformat(),
                    leido=False
                )
                gestor_notificaciones.agregar_notificacion(self.id_usuario, notif)
            elif self.contador_vip % 3 == 0:
                eventos.append({"accion": "vip_recompensa", "mensaje": f"🎁 Recompensa VIP mes {self.contador_vip}: {item_random['nombre']}"})
                notif = Notificacion(
                    id_notificacion=None,
                    mensaje=f"🎁 Recompensa VIP mes {self.contador_vip}: {item_random['nombre']}",
                    accion="vip_recompensa",
                    fecha=date.today().isoformat(),
                    leido=False
                )
                gestor_notificaciones.agregar_notificacion(self.id_usuario, notif)

        return eventos

    # Usa el poder de su clase:
    def usar_poder(self, nombre_poder, tarea=None):
            return self.clase.usar_poder(nombre_poder, self, tarea)