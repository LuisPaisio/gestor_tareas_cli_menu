class Recompensa:
    """
    Clase base para futuras recompensas.
    Aún no implementada.
    """
    def __init__(self, id_recompensa, nombre, tipo, valor):
        self.id_recompensa = id_recompensa
        self.nombre = nombre
        self.tipo = tipo
        self.valor = valor

    def aplicar_usuario(self, usuario):
        """Aplicará la recompensa al usuario (pendiente de implementación)."""
        pass
