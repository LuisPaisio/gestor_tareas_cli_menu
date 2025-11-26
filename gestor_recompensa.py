import os
import json
from recompensa import Recompensa
from colorama import Fore, Style

ARCHIVO_RECOMPENSAS = os.path.join("json", "recompensas.json")

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
        """
        Aplica una lista de recompensas al usuario.
        Cada recompensa se ejecuta y se guarda en el historial.
        """
        if not recompensas:
            return

        print(Fore.LIGHTYELLOW_EX + "\n🎁 ¡Recompensas obtenidas!" + Style.RESET_ALL)

        for recompensa in recompensas:
            recompensa.aplicar_usuario(usuario)
            self.historial.append(recompensa)

            # Feedback bonito según tipo
            if recompensa.tipo == "xp":
                print(Fore.GREEN + f"✨ +{recompensa.valor} XP" + Style.RESET_ALL)
            elif recompensa.tipo == "coins":
                print(Fore.YELLOW + f"💰 +{recompensa.valor} Coins" + Style.RESET_ALL)
            elif recompensa.tipo == "vida":
                if recompensa.valor < 0:
                    print(Fore.RED + f"❤️ -{abs(recompensa.valor)} Vida" + Style.RESET_ALL)
                else:
                    print(Fore.GREEN + f"❤️ +{recompensa.valor} Vida" + Style.RESET_ALL)
            elif recompensa.tipo == "item":
                print(Fore.CYAN + f"🪄 Obtuviste el ítem: {recompensa.nombre}" + Style.RESET_ALL)
            else:
                print(Fore.MAGENTA + f"🔹 {recompensa.nombre} ({recompensa.tipo}: {recompensa.valor})" + Style.RESET_ALL)

        # Guardar historial
        self.guardar_historial()

        # Resumen del estado actual del usuario
        print(Fore.LIGHTYELLOW_EX + "---------------------------------" + Style.RESET_ALL)
        print(Fore.LIGHTYELLOW_EX + f"📊 Estado actual → Nivel {usuario.nivel_usuario} | XP {usuario.xp_usuario} | Coins {usuario.coin_usuario} | Vida {usuario.vida_usuario}/50" + Style.RESET_ALL)
