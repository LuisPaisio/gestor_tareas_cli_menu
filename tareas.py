import datetime
import constantes_tareas

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
            # Validar si corresponde el día
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
                hoy_es = mapa_dias[hoy]
                if hoy_es not in self.dias_semana:
                    print(f"⚠️ La tarea '{self.titulo}' no puede completarse hoy ({hoy_es}).")
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
                xp += dias_tarde * 2
                coins += dias_tarde * 1
                usuario.vida_usuario = min(50, usuario.vida_usuario + dias_tarde)

        usuario.sumar_xp_coins(xp, coins)
        self.completada = True
    
    def fallar(self, usuario, por_medianoche=False):
        mult = constantes_tareas.multi_dificultad().get(self.dificultad, 1)

        if self.tipo == 1 and self.habito == "-":  # Hábito negativo
            usuario.restar_vida(int(constantes_tareas.vida_habito() * mult))

        elif self.tipo == 2:  # Diaria
            if por_medianoche:
                # Penalización fuerte al pasar las 00:00
                usuario.restar_vida(int(constantes_tareas.vida_diaria() * mult))
                usuario.xp_usuario = max(0, usuario.xp_usuario - int(constantes_tareas.xp_diaria() * mult))
                usuario.coin_usuario = max(0, usuario.coin_usuario - int(constantes_tareas.coin_diaria() * mult))
            else:
                # Penalización leve al desmarcar manualmente
                usuario.xp_usuario = max(0, usuario.xp_usuario - int(constantes_tareas.xp_diaria() * 0.5 * mult))
                usuario.coin_usuario = max(0, usuario.coin_usuario - int(constantes_tareas.coin_diaria() * 0.5 * mult))

        elif self.tipo == 3:  # Pendiente vencida
            usuario.restar_vida(int(constantes_tareas.vida_pendiente() * mult))
            usuario.xp_usuario = max(0, usuario.xp_usuario - int(constantes_tareas.xp_pendiente() * mult))
            usuario.coin_usuario = max(0, usuario.coin_usuario - int(constantes_tareas.coin_pendiente() * mult))

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
