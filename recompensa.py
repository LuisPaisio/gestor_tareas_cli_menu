class Recompensa:
    """
    Clase que representa una recompensa o penalización.
    Puede ser de tipo: xp, coins, vida, item.
    """
    def __init__(self, id_recompensa, nombre, tipo, valor):
        self.id_recompensa = id_recompensa
        self.nombre = nombre
        self.tipo = tipo      # "xp", "coins", "vida", "item"
        self.valor = valor    # cantidad o referencia al ítem

    def aplicar_usuario(self, usuario):
        """
        Aplica la recompensa al usuario según su tipo.
        """
        if self.tipo == "xp":
            usuario.xp_usuario += self.valor

        elif self.tipo == "coins":
            usuario.coin_usuario += self.valor

        elif self.tipo == "vida":
            # si el valor es positivo suma vida, si es negativo resta
            if self.valor >= 0:
                usuario.sumar_vida(self.valor)
            else:
                usuario.restar_vida(abs(self.valor))

        elif self.tipo == "item":
            # valor debería ser un objeto Item o un id_item
            inventario = usuario.gestor_inventario.inventario_usuario()
            inventario.agregar_item(self.valor, 1)
            usuario.gestor_inventario.actualizar_inventario(inventario)

        else:
            raise ValueError(f"Tipo de recompensa no válido: {self.tipo}")
