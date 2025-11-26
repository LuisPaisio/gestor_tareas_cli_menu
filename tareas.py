import datetime
import constantes_tareas
from colorama import Fore, Style
from recompensa import Recompensa

class Tarea:
    def __init__(self, id, titulo, tipo, id_usuario,
                dias_semana=None, fecha_vencimiento=None,
                xp_reward=0, coin_reward=0, vida_restar=0,
                habito=None, completada=False, fecha_creacion=None, dificultad=None):
        self.id = id
        self.titulo = titulo
        self.tipo = tipo  # 1=Hábito, 2=Diaria, 3=Pendiente
        self.id_usuario = id_usuario
        self.dias_semana = dias_semana or []
        self.fecha_vencimiento = fecha_vencimiento
        self.xp_reward = xp_reward
        self.coin_reward = coin_reward
        self.vida_restar = vida_restar
        self.habito = habito
        self.completada = completada
        self.fecha_creacion = fecha_creacion or datetime.date.today().strftime("%d-%m-%Y")
        self.dificultad = dificultad

    # -------------------------------
    # Métodos de acción sobre la tarea
    # -------------------------------
    def marcar_completada(self):
        if not self.completada:
            self.completada = True
            return True
        return False

    def marcar_incompleta(self):
        if self.completada:
            self.completada = False
            return True
        return False

    def editar_titulo(self, nuevo_titulo):
        self.titulo = nuevo_titulo

    def es_vencida(self):
        if self.tipo == 3 and self.fecha_vencimiento:
            try:
                fecha = datetime.datetime.strptime(self.fecha_vencimiento, "%d-%m-%Y").date()
                return datetime.date.today() > fecha
            except ValueError:
                return False
        return False
    
    def completar(self, retroactivo=False):
        """Genera recompensas al completar la tarea, sin aplicarlas directamente al usuario."""
        mult = constantes_tareas.multi_dificultad().get(self.dificultad, 1)
        recompensas = []

        # --- Hábito positivo ---
        if self.tipo == 1 and self.habito == "+":
            recompensas.append(Recompensa(None, f"XP por hábito {self.titulo}", "xp", int(constantes_tareas.xp_habito() * mult)))
            recompensas.append(Recompensa(None, f"Coins por hábito {self.titulo}", "coins", int(constantes_tareas.coin_habito() * mult)))

        # --- Diaria ---
        elif self.tipo == 2:
            if self.dias_semana and not retroactivo:
                hoy = datetime.date.today().strftime("%A").lower()
                mapa_dias = {
                    "monday": "lunes",
                    "tuesday": "martes",
                    "wednesday": "miercoles",
                    "thursday": "jueves",
                    "friday": "viernes",
                    "saturday": "sabado",
                    "sunday": "domingo"
                }
                hoy_es = mapa_dias[hoy].lower()
                dias_normalizados = [d.lower() for d in self.dias_semana]

                if hoy_es not in dias_normalizados:
                    print(Fore.RED + f"⚠️ La tarea '{self.titulo}' no puede completarse hoy ({hoy_es})." + Style.RESET_ALL)
                    return []

            recompensas.append(Recompensa(None, f"XP diaria {self.titulo}", "xp", int(constantes_tareas.xp_diaria() * mult)))
            recompensas.append(Recompensa(None, f"Coins diaria {self.titulo}", "coins", int(constantes_tareas.coin_diaria() * mult)))

        # --- Pendiente ---
        elif self.tipo == 3:
            xp = int(constantes_tareas.xp_pendiente() * mult)
            coins = int(constantes_tareas.coin_pendiente() * mult)
            if self.es_vencida():
                fecha = datetime.datetime.strptime(self.fecha_vencimiento, "%d-%m-%Y").date()
                dias_tarde = (datetime.date.today() - fecha).days
                xp += dias_tarde * constantes_tareas.xp_bonus_vencida()
                coins += dias_tarde * constantes_tareas.coin_bonus_vencida()
                recompensas.append(Recompensa(None, f"Vida extra por pendiente vencida {self.titulo}", "vida", dias_tarde))

            recompensas.append(Recompensa(None, f"XP pendiente {self.titulo}", "xp", xp))
            recompensas.append(Recompensa(None, f"Coins pendiente {self.titulo}", "coins", coins))

        self.completada = True
        return recompensas

    def fallar(self, por_medianoche=False):
        """Genera penalizaciones al fallar la tarea, sin aplicarlas directamente al usuario."""
        mult = constantes_tareas.multi_dificultad().get(self.dificultad, 1)
        recompensas = []

        if self.tipo == 1 and self.habito == "-":  # Hábito negativo
            vida_perdida = int(constantes_tareas.vida_habito() * mult)
            recompensas.append(Recompensa(None, f"Penalización hábito negativo {self.titulo}", "vida", -vida_perdida))

        elif self.tipo == 2:  # Diaria
            if por_medianoche:
                vida_perdida = int(constantes_tareas.vida_diaria() * mult)
                xp_perdido = int(constantes_tareas.xp_diaria() * mult)
                coins_perdidos = int(constantes_tareas.coin_diaria() * mult)

                recompensas.append(Recompensa(None, f"Vida perdida diaria {self.titulo}", "vida", -vida_perdida))
                recompensas.append(Recompensa(None, f"XP perdida diaria {self.titulo}", "xp", -xp_perdido))
                recompensas.append(Recompensa(None, f"Coins perdidos diaria {self.titulo}", "coins", -coins_perdidos))
            else:
                xp_perdido = int(constantes_tareas.xp_diaria() * 0.5 * mult)
                coins_perdidos = int(constantes_tareas.coin_diaria() * 0.5 * mult)

                recompensas.append(Recompensa(None, f"XP perdida diaria {self.titulo}", "xp", -xp_perdido))
                recompensas.append(Recompensa(None, f"Coins perdidos diaria {self.titulo}", "coins", -coins_perdidos))

        elif self.tipo == 3:  # Pendiente vencida
            vida_perdida = int(constantes_tareas.vida_pendiente() * mult)
            xp_perdido = int(constantes_tareas.xp_pendiente() * mult)
            coins_perdidos = int(constantes_tareas.coin_pendiente() * mult)

            recompensas.append(Recompensa(None, f"Vida perdida pendiente {self.titulo}", "vida", -vida_perdida))
            recompensas.append(Recompensa(None, f"XP perdida pendiente {self.titulo}", "xp", -xp_perdido))
            recompensas.append(Recompensa(None, f"Coins perdidos pendiente {self.titulo}", "coins", -coins_perdidos))

        self.completada = False
        return recompensas

    # -------------------------------
    # Conversión a dict/objeto
    # -------------------------------
    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "tipo": self.tipo,
            "id_usuario": self.id_usuario,
            "dias_semana": self.dias_semana,
            "fecha_vencimiento": self.fecha_vencimiento,
            "xp_reward": self.xp_reward,
            "coin_reward": self.coin_reward,
            "vida_restar": self.vida_restar,
            "habito": self.habito,
            "completada": self.completada,
            "fecha_creacion": self.fecha_creacion,
            "dificultad": self.dificultad
        }

    @staticmethod
    def from_dict(data):
        return Tarea(
            id=data.get("id"),
            titulo=data.get("titulo"),
            tipo=data.get("tipo"),
            id_usuario=data.get("id_usuario"),
            dias_semana=data.get("dias_semana"),
            fecha_vencimiento=data.get("fecha_vencimiento"),
            xp_reward=data.get("xp_reward", 0),
            coin_reward=data.get("coin_reward", 0),
            vida_restar=data.get("vida_restar", 0),
            habito=data.get("habito"),
            completada=data.get("completada", False),
            fecha_creacion=data.get("fecha_creacion"),
            dificultad=data.get("dificultad")
        )
