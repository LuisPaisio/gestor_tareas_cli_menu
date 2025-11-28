import os
import json
from recompensa import Recompensa
from colorama import Fore, Style
from utils_rutas import ruta_json

#ARCHIVO_RECOMPENSAS = os.path.join("json", "recompensas.json")
ARCHIVO_RECOMPENSAS = ruta_json("recompensas.json")

class GestorRecompensas:
    def __init__(self):
        self.historial = self.cargar_historial()

    def cargar_historial(self):
        """Carga el historial de recompensas aplicadas desde JSON."""
        if os.path.exists(ARCHIVO_RECOMPENSAS):
            try:
                with open(ARCHIVO_RECOMPENSAS, "r", encoding="utf-8") as archivo:
                    contenido = archivo.read().strip()
                    if not contenido:
                        return []
                    data = json.loads(contenido)
                    return [Recompensa(**r) for r in data]
            except json.JSONDecodeError:
                print(Fore.RED + "⚠️ El archivo de recompensas está corrupto. Se iniciará vacío." + Style.RESET_ALL)
                return []
        return []

    def guardar_historial(self):
        """Guarda el historial de recompensas aplicadas en JSON."""
        with open(ARCHIVO_RECOMPENSAS, "w", encoding="utf-8") as archivo:
            json.dump([r.__dict__ for r in self.historial], archivo, indent=4, ensure_ascii=False)

    def aplicar_recompensas(self, usuario, recompensas: list[Recompensa]):
        if not recompensas:
            return

        print(Fore.LIGHTYELLOW_EX + "\n🎁 ¡Recompensas obtenidas!" + Style.RESET_ALL)

        for recompensa in recompensas:
            resultado = recompensa.aplicar_usuario(usuario)  # dict con base, bonus, total
            self.historial.append(recompensa)

            if recompensa.tipo == "xp":
                if resultado["total"] >= 0:
                    if resultado["base"] > 0:
                        print(Fore.GREEN + f"✨ +{resultado['base']} XP" + Style.RESET_ALL)
                    if resultado["bonus"] > 0:
                        print(Fore.GREEN + f"✨ +{resultado['bonus']} XP (VIP/bonus)" + Style.RESET_ALL)
                else:
                    print(Fore.RED + f"✨ {resultado['total']} XP" + Style.RESET_ALL)

            elif recompensa.tipo == "coins":
                if resultado["total"] >= 0:
                    if resultado["base"] > 0:
                        print(Fore.YELLOW + f"💰 +{resultado['base']} Coins" + Style.RESET_ALL)
                    if resultado["bonus"] > 0:
                        print(Fore.YELLOW + f"💰 +{resultado['bonus']} Coins (VIP/bonus)" + Style.RESET_ALL)
                else:
                    print(Fore.RED + f"💰 {resultado['total']} Coins" + Style.RESET_ALL)

            elif recompensa.tipo == "vida":
                if resultado["total"] < 0:
                    print(Fore.RED + f"❤️ {resultado['total']} Vida" + Style.RESET_ALL)
                else:
                    print(Fore.GREEN + f"❤️ +{resultado['total']} Vida" + Style.RESET_ALL)

            elif recompensa.tipo == "item":
                print(Fore.CYAN + f"🪄 Obtuviste el ítem: {recompensa.nombre}" + Style.RESET_ALL)

            else:
                print(Fore.MAGENTA + f"🔹 {recompensa.nombre} ({recompensa.tipo}: {resultado['total']})" + Style.RESET_ALL)

        self.guardar_historial()

        print(Fore.LIGHTYELLOW_EX + "---------------------------------" + Style.RESET_ALL)
        print(Fore.LIGHTYELLOW_EX + 
            f"📊 Estado actual → Nivel {usuario.nivel_usuario} | XP {usuario.xp_usuario} | Coins {usuario.coin_usuario} | Vida {usuario.vida_usuario}/50" 
            + Style.RESET_ALL)
