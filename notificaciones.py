class Notificacion:
    def __init__(self, id_notificacion, mensaje, accion, fecha, leido=False):
        self.id_notificacion = id_notificacion
        self.mensaje = mensaje
        self.accion = accion
        self.fecha = fecha
        self.leido = leido

    def marcar_leida(self):
        self.leido = True

    def to_dict(self):
        return {
            "id": self.id_notificacion,   # 🔹 incluir el ID
            "mensaje": self.mensaje,
            "accion": self.accion,
            "leido": self.leido,
            "fecha": self.fecha
        }
