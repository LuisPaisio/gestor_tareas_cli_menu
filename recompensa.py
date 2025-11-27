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
        Aplica la recompensa al usuario según su tipo,
        considerando atributos RPG y ventajas VIP.
        Devuelve un dict con base, bonus y total en xp/coins.
        """
        if self.tipo == "xp":
            bonus = int(usuario.fuerza * 0.5)
            if usuario.rol == "vip" and usuario.ventajas_vip:
                bonus += int(self.valor * usuario.ventajas_vip.get("bonus_xp", 0))
            total = self.valor + bonus
            usuario.xp_usuario += total
            return {"base": self.valor, "bonus": bonus, "total": total}

        elif self.tipo == "coins":
            bonus = int(usuario.velocidad * 0.3)
            if usuario.rol == "vip" and usuario.ventajas_vip:
                bonus += int(self.valor * usuario.ventajas_vip.get("bonus_coins", 0))
            total = self.valor + bonus
            usuario.coin_usuario += total
            return {"base": self.valor, "bonus": bonus, "total": total}

        elif self.tipo == "vida":
            if self.valor >= 0:
                usuario.sumar_vida(self.valor)
                return {"base": self.valor, "bonus": 0, "total": self.valor}
            else:
                daño_base = abs(self.valor)
                daño_reducido = max(0, daño_base - usuario.defensa)
                usuario.restar_vida(daño_reducido)
                return {"base": -daño_base, "bonus": usuario.defensa, "total": -daño_reducido}

        elif self.tipo == "item":
            inventario = usuario.gestor_inventario.inventario_usuario()
            inventario.agregar_item(self.valor, 1)
            usuario.gestor_inventario.actualizar_inventario(inventario)
            return {"base": 1, "bonus": 0, "total": self.valor}

        else:
            raise ValueError(f"Tipo de recompensa no válido: {self.tipo}")
