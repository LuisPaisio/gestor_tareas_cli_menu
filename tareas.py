import datetime

class Tarea:
    def __init__(self, id, titulo, tipo, id_usuario,
                dias_semana=None, fecha_vencimiento=None,
                xp_reward=0, coin_reward=0, vida_restar=0,
                habito=None, completada=False):
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
        self.fecha_creacion = datetime.datetime.now().strftime("%d-%m-%Y")

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
            "completada": self.completada
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
            completada=data.get("completada", False)
        )
