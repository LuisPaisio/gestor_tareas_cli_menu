import datetime
import constantes_tareas
from colorama import Fore, Style

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
    
    def completar(self, usuario):
        mult = constantes_tareas.multi_dificultad().get(self.dificultad, 1)
        xp, coins = 0, 0

        # --- Hábito positivo ---
        if self.tipo == 1 and self.habito == "+":
            xp = int(constantes_tareas.xp_habito() * mult)
            coins = int(constantes_tareas.coin_habito() * mult)

        # --- Diaria ---
        elif self.tipo == 2:
            if self.dias_semana:
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
                    return

            xp = int(constantes_tareas.xp_diaria() * mult)
            coins = int(constantes_tareas.coin_diaria() * mult)

        # --- Pendiente ---
        elif self.tipo == 3:
            xp = int(constantes_tareas.xp_pendiente() * mult)
            coins = int(constantes_tareas.coin_pendiente() * mult)

            if self.es_vencida():
                fecha = datetime.datetime.strptime(self.fecha_vencimiento, "%d-%m-%Y").date()
                dias_tarde = (datetime.date.today() - fecha).days
                xp += dias_tarde * constantes_tareas.xp_bonus_vencida()
                coins += dias_tarde * constantes_tareas.coin_bonus_vencida()
                usuario.vida_usuario = min(constantes_tareas.vida_maxima(), usuario.vida_usuario + dias_tarde)

        usuario.sumar_xp_coins(xp, coins)
        self.completada = True

    
    def fallar(self, usuario, por_medianoche=False):
        mult = constantes_tareas.multi_dificultad().get(self.dificultad, 1)

        if self.tipo == 1 and self.habito == "-":  # Hábito negativo
            vida_perdida = int(constantes_tareas.vida_habito() * mult)
            usuario.restar_vida(vida_perdida)
            print(Fore.RED + f"\nHas perdido {vida_perdida} de vida por hábito negativo." + Style.RESET_ALL)

        elif self.tipo == 2:  # Diaria
            if por_medianoche:
                vida_perdida = int(constantes_tareas.vida_diaria() * mult)
                xp_perdido = int(constantes_tareas.xp_diaria() * mult)
                coins_perdidos = int(constantes_tareas.coin_diaria() * mult)

                usuario.restar_vida(vida_perdida)
                usuario.xp_usuario = max(0, usuario.xp_usuario - xp_perdido)
                usuario.coin_usuario = max(0, usuario.coin_usuario - coins_perdidos)

                print(Fore.RED + f"\nHas perdido {vida_perdida} de vida, {xp_perdido} XP y {coins_perdidos} coins por no completar la diaria." + Style.RESET_ALL)
            else:
                xp_perdido = int(constantes_tareas.xp_diaria() * 0.5 * mult)
                coins_perdidos = int(constantes_tareas.coin_diaria() * 0.5 * mult)

                usuario.xp_usuario = max(0, usuario.xp_usuario - xp_perdido)
                usuario.coin_usuario = max(0, usuario.coin_usuario - coins_perdidos)

                print(Fore.RED + f"\nHas perdido {xp_perdido} XP y {coins_perdidos} coins por marcar la diaria como incompleta." + Style.RESET_ALL)

        elif self.tipo == 3:  # Pendiente vencida
            vida_perdida = int(constantes_tareas.vida_pendiente() * mult)
            xp_perdido = int(constantes_tareas.xp_pendiente() * mult)
            coins_perdidos = int(constantes_tareas.coin_pendiente() * mult)

            usuario.restar_vida(vida_perdida)
            usuario.xp_usuario = max(0, usuario.xp_usuario - xp_perdido)
            usuario.coin_usuario = max(0, usuario.coin_usuario - coins_perdidos)

            print(Fore.RED + f"\nHas perdido {vida_perdida} de vida, {xp_perdido} XP y {coins_perdidos} coins por no completar la pendiente." + Style.RESET_ALL)


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
