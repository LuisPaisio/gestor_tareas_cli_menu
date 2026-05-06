from constantes_tareas import mana_maximo

class Recompensa:
    """
    Clase que representa una recompensa o penalización.
    Puede ser de tipo: xp, coins, vida, mana, item.
    """
    def __init__(self, id_recompensa, nombre, tipo, valor):
        self.id_recompensa = id_recompensa
        self.nombre = nombre
        self.tipo = tipo      # "xp", "coins", "vida", "mana", "item"
        self.valor = valor    # cantidad o referencia al ítem

    def aplicar_usuario(self, usuario):
        """
        Aplica la recompensa al usuario según su tipo,
        considerando atributos RPG, equipamiento, buffs temporales y ventajas VIP.
        Devuelve un dict con base, bonus y total.
        """
        atributos = usuario.atributos_totales()

        if self.tipo == "xp":
            bonus_fuerza = round(atributos.get("fuerza", 0) * 0.5)
            bonus_vip = 0
            if usuario.rol == "vip" and usuario.ventajas_vip:
                bonus_vip = round(self.valor * usuario.ventajas_vip.get("bonus_xp", 0))
            bonus_total = bonus_fuerza + bonus_vip
            total = self.valor + bonus_total

            usuario.sumar_xp(total)

            return {"base": self.valor, "bonus": bonus_total, "total": total}

        elif self.tipo == "coins":
            bonus_velocidad = round(atributos.get("velocidad", 0) * 0.3)
            bonus_vip = 0
            if usuario.rol == "vip" and usuario.ventajas_vip:
                bonus_vip = round(self.valor * usuario.ventajas_vip.get("bonus_coins", 0))
            bonus_total = bonus_velocidad + bonus_vip
            total = self.valor + bonus_total

            usuario.sumar_coins(total)

            return {"base": self.valor, "bonus": bonus_total, "total": total}

        elif self.tipo == "vida":
            if self.valor >= 0:
                usuario.sumar_vida(self.valor)
                return {"base": self.valor, "bonus": 0, "total": self.valor}
            else:
                daño_base = abs(self.valor)
                defensa_total = atributos.get("defensa", 0)
                daño_reducido = max(0, daño_base - defensa_total)
                murio = usuario.restar_vida(daño_reducido)
                return {
                    "base": -daño_base,
                    "bonus": defensa_total,
                    "total": -daño_reducido,
                    "murio": murio
                }

        elif self.tipo == "mana":
            bonus_vip = 0
            if usuario.rol == "vip" and usuario.ventajas_vip:
                bonus_vip = round(self.valor * usuario.ventajas_vip.get("bonus_mana", 0))

            bonus_items = atributos.get("mana", 0)
            bonus_total = bonus_vip + bonus_items
            total = self.valor + bonus_total

            usuario.mana_usuario = min(usuario.mana_usuario + total, mana_maximo())

            return {"base": self.valor, "bonus": bonus_total, "total": total}

        elif self.tipo == "item":
            inventario = usuario.gestor_inventario.inventario_usuario()
            inventario.agregar_item(self.valor, 1)
            usuario.gestor_inventario.actualizar_inventario(inventario)
            return {"base": 1, "bonus": 0, "total": self.valor}

        else:
            raise ValueError(f"Tipo de recompensa no válido: {self.tipo}")
