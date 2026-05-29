import json
import os
from utils_rutas import ruta_json
from constantes_tareas import vida_maxima, mana_maximo

ARCHIVO_CLASES = ruta_json("clases.json")

class Clase:
    def __init__(self, nombre, vip=False, poderes=None, descripcion="Sin descripción", img_clase=None):
        self.nombre = nombre
        self.vip = vip
        self.poderes = poderes or {}
        self.descripcion = descripcion
        self.img_clase = img_clase

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
        img_clase = info.get("img_clase")

        return cls(nombre, vip, poderes, descripcion, img_clase)

    def usar_poder(self, nombre_poder, usuario, tarea=None):
        """
        Aplica un poder sobre el usuario si tiene maná suficiente.
        Retorna (success: bool, mensajes: list[str])
        """
        poder = self.poderes.get(nombre_poder)
        if not poder:
            return (False, [f"⚠️ El poder {nombre_poder} no está disponible para {self.nombre}."])

        coste = poder.get("coste", 0)
        if usuario.mana_usuario < coste:
            return (False, ["⚠️ No tienes suficiente maná."])

        usuario.mana_usuario -= coste
        efectos = poder.get("efectos", {})
        mensajes = [f"✨ {usuario.nombre_con_tags()} usó {nombre_poder}. Efectos aplicados:"]

        for atributo, valor in efectos.items():
            if atributo == "xp":
                if valor == "double":
                    usuario.buff_xp *= 2
                    mensajes.append("✨ La recompensa de XP de la tarea actual será duplicada.")
                elif valor == "double_next":
                    usuario.buff_xp *= 2
                    mensajes.append("✨ Próxima recompensa de XP será duplicada.")
                elif isinstance(valor, int):
                    usuario.sumar_xp(valor)
                    mensajes.append(f"✨ +{valor} XP")

            elif atributo == "coins":
                if valor == "double":
                    usuario.buff_coins *= 2
                    mensajes.append("💰 La recompensa de Coins de la tarea actual será duplicada.")
                elif valor == "double_next":
                    usuario.buff_coins *= 2
                    mensajes.append("💰 Próxima recompensa de Coins será duplicada.")
                elif isinstance(valor, str) and "%" in valor and tarea:
                    porc = int(valor.replace("%", ""))
                    extra = int(tarea.get("coins", 0) * porc / 100)
                    usuario.sumar_coins(extra)
                    mensajes.append(f"💰 Bonus {porc}% Coins: +{extra}")
                elif isinstance(valor, str) and "steal_" in valor and tarea:
                    porc = int(valor.replace("steal_", ""))
                    extra = int(tarea.get("coins", 0) * porc / 100)
                    usuario.sumar_coins(extra)
                    mensajes.append(f"💰 Robaste {porc}% Coins: +{extra}")
                elif isinstance(valor, int):
                    usuario.sumar_coins(valor)
                    mensajes.append(f"💰 +{valor} Coins")

            elif atributo == "vida":
                if valor == "full":
                    usuario.vida_usuario = vida_maxima()
                    mensajes.append(f"❤️ Vida restaurada al máximo ({vida_maxima()})")
                elif isinstance(valor, int):
                    usuario.sumar_vida(valor)
                    mensajes.append(f"❤️ +{valor} Vida")

            elif atributo == "mana":
                usuario.mana_usuario = min(usuario.mana_usuario + valor, mana_maximo())
                mensajes.append(f"🔮 +{valor} Maná")

        return (True, mensajes)
