#Multiplicadores por dificultad
def multi_dificultad():
    return{
        "facil":1,
        "intermedia":1.5,
        "dificil":2
    }

def xp_bonus_vencida():
    """Devuelve el XP extra por cada día de atraso al completar una tarea Pendiente vencida."""
    return 5  # por ejemplo, 5 XP por día de atraso

def coin_bonus_vencida():
    """Devuelve las coins extra por cada día de atraso al completar una tarea Pendiente vencida."""
    return 2  # por ejemplo, 2 coins por día de atraso

# constante para vida máxima
def vida_maxima():
    """Devuelve la vida máxima de un usuario."""
    return 50

# constante para maná maximo
def mana_maximo():
    """Devuelve el maná máximo de un usuario."""
    return 56

# Valores de XP
def xp_habito(): return 10
def xp_diaria(): return 20
def xp_pendiente(): return 30

# Valores de Coins
def coin_habito(): return 5
def coin_diaria(): return 10
def coin_pendiente(): return 15

# Penalizaciones de Vida
def vida_habito(): return 2
def vida_diaria(): return 3
def vida_pendiente(): return 5
