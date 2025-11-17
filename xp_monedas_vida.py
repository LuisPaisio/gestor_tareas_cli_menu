#Funciones para la gestión de xp y coins de los usuarios.

# Defino el monto de XP en una función para facilitar futuros cambios, según tareas que sean hábitos, diarias o pendientes.
def xp_habito():
    return 10  #XP por completar un hábito

def xp_diaria():
    return 20  #XP por completar una diaria

def xp_pendiente():
    return 30  #XP por completar una pendiente

#Defino el monto de COINS en una función para facilitar futuros cambios, según tareas que sean hábitos, diarias o pendientes.
def coin_habito():
    return 5

def coin_diaria():
    return 10

def coin_pendiente():
    return 15

#Defino la vida que se resta al usuario por no completar tareas, según sean Hábito, Diaria o Pendiente.
def vida_habito():
    if habito_negativo: #Tengo que definir habito_negativo en la función donde se use. Estará en Tareas.py
        return 5
    else:
        return 0

def vida_diaria():
    return 2

def vida_pendiente():
    return 3


"""Todas las tareas dan XP y monedas al completarse.

Las diarias y pendientes penalizan vida si no se cumplen.

La vida máxima es 50, con penalizaciones pequeñas pero acumulativas (−2 o −3).

Esto genera un balance: el usuario se motiva por las recompensas, pero también siente presión por las penalizaciones."""