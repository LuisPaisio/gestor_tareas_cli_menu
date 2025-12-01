import json
import os
from utils_rutas import ruta_json
from constantes_tareas import vida_maxima, mana_maximo

ARCHIVO_CLASES = ruta_json("clases.json")

class Clase:
    def __init__(self, nombre, vip=False, poderes=None, descripcion="Sin descripción"):
        self.nombre = nombre
        self.vip = vip
        self.poderes = poderes or {}
        self.descripcion = descripcion

    @classmethod
    def cargar_clase(cls, nombre, vip=False):
        """Carga la definición de la clase desde clases.json"""
        if not os.path.exists(ARCHIVO_CLASES):
            print("⚠️ No se encontró clases.json")
            return cls(nombre, vip, {}, "Sin descripción")

        with open(ARCHIVO_CLASES, "r", encoding="utf-8") as f:
            data = json.load(f)

        clave = f"{nombre}{'VIP' if vip else ''}"
        info = data.get(clave, {})
        poderes = info.get("poderes", {})
        descripcion = info.get("descripcion", "Sin descripción")

        return cls(nombre, vip, poderes, descripcion)

    def mostrar_info(self):
        """Muestra nombre, descripción y lista de poderes"""
        print(f"\nClase: {self.nombre}{' (VIP)' if self.vip else ''}")
        print(f"Descripción: {self.descripcion}")
        if self.poderes:
            print("--- Poderes disponibles ---")
            for nombre_poder, datos in self.poderes.items():
                coste = datos.get("coste", 0)
                desc = datos.get("descripcion", "Sin descripción")
                print(f"🪄 {nombre_poder} (Coste: {coste} Maná) → {desc}")

    def usar_poder(self, nombre_poder, usuario, tarea=None):
        """
        Aplica un poder sobre el usuario si tiene maná suficiente.
        - usuario: instancia de Usuario
        - tarea: dict con xp/coins de la tarea actual (para efectos como double, %)
        """
        poder = self.poderes.get(nombre_poder)
        if not poder:
            print(f"⚠️ El poder {nombre_poder} no está disponible para {self.nombre}.")
            return False

        coste = poder.get("coste", 0)
        if usuario.mana_usuario < coste:
            print("⚠️ No tienes suficiente maná.")
            return False

        # Descuento de maná
        usuario.mana_usuario -= coste

        efectos = poder.get("efectos", {})

        print(f"\n✨ {usuario.nombre_con_tags()} usó {nombre_poder}. Efectos aplicados:")

        # Interpretación de efectos
        for atributo, valor in efectos.items():
            if atributo == "xp":
                if valor == "double":
                    usuario.buff_xp *= 2  # se aplicará en la próxima tarea
                    print("✨ La recompensa de XP de la tarea actual será duplicada.")
                elif valor == "double_next":
                    usuario.buff_xp *= 2
                    print("✨ Próxima recompensa de XP será duplicada.")
                elif isinstance(valor, int):
                    usuario.sumar_xp(valor)
                    print(f"✨ +{valor} XP")

            elif atributo == "coins":
                if valor == "double":
                    usuario.buff_coins *= 2  # se aplicará en la próxima tarea
                    print("💰 La recompensa de Coins de la tarea actual será duplicada.")
                elif valor == "double_next":
                    usuario.buff_coins *= 2
                    print("💰 Próxima recompensa de Coins será duplicada.")
                elif isinstance(valor, str) and "%" in valor and tarea:
                    porc = int(valor.replace("%", ""))
                    extra = int(tarea.get("coins", 0) * porc / 100)
                    usuario.sumar_coins(extra)
                    print(f"💰 Bonus {porc}% Coins: +{extra}")
                elif isinstance(valor, str) and "steal_" in valor and tarea:
                    porc = int(valor.replace("steal_", ""))
                    extra = int(tarea.get("coins", 0) * porc / 100)
                    usuario.sumar_coins(extra)
                    print(f"💰 Robaste {porc}% Coins: +{extra}")
                elif isinstance(valor, int):
                    usuario.sumar_coins(valor)
                    print(f"💰 +{valor} Coins")

            elif atributo == "vida":
                if valor == "full":
                    usuario.vida_usuario = vida_maxima()
                    print(f"❤️ Vida restaurada al máximo ({vida_maxima()})")
                elif isinstance(valor, int):
                    usuario.sumar_vida(valor)
                    print(f"❤️ +{valor} Vida")

            elif atributo == "mana":
                usuario.mana_usuario = min(usuario.mana_usuario + valor, mana_maximo())
                print(f"🔮 +{valor} Maná")

            # ❌ Eliminado: otorgar ítem aleatorio

        return True
