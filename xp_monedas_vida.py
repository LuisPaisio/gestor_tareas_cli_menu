import json
import os
from colorama import Fore, Style

#Funciones para la gestión de xp y coins de los usuarios.
#----------------------------------------------------------------
#cargo documento de usuarios
ARCHIVO_USUARIOS = "usuarios.json"
def cargar_usuarios():
    if os.path.exists(ARCHIVO_USUARIOS):
        try:
            with open(ARCHIVO_USUARIOS, "r") as archivo_usuarios:
                contenido = archivo_usuarios.read().strip()
                if not contenido:
                    return []
                return json.loads(contenido)
        except json.JSONDecodeError:
            print(Fore.RED + "⚠️ El archivo de usuarios está corrupto o vacío. Se iniciará una lista nueva." + Style.RESET_ALL)
            return []
    else:
        return []

#Guardo documento de usuarios
def guardar_usuarios(usuarios):
    with open(ARCHIVO_USUARIOS, "w") as archivo_usuarios:
        json.dump(usuarios, archivo_usuarios, indent=4)
#----------------------------------------------------------------
# Defino el monto de XP en una función para facilitar futuros cambios, según tareas que sean hábitos, diarias o pendientes.
def xp_habito():
    return 10  #XP por completar un hábito

def xp_diaria():
    return 20  #XP por completar una diaria

def xp_pendiente():
    return 30  #XP por completar una pendiente
#----------------------------------------------------------------
#Defino el monto de COINS en una función para facilitar futuros cambios, según tareas que sean hábitos, diarias o pendientes.
def coin_habito():
    return 5

def coin_diaria():
    return 10

def coin_pendiente():
    return 15
#----------------------------------------------------------------
def vida_diaria(): #Resto vida por no completar una diaria pasada las 00:00hs. | Ésto debería ser una función programada que pasadas las 00:00hs revise las diarias no completadas y reste la vida correspondiente de la tarea segun sea habito, diaria o pendiente.
    return 2

def vida_pendiente(): #Resto vida por no completar una pendiente pasada su fecha de vencimiento.
    return 3

#Sumo XP y Coins al usuario
def sumar_xp_coins(usuario, xp, coins):
    usuarios = cargar_usuarios()
    for usr in usuarios:
        if usr["id_usuario"] == usuario["id_usuario"]:
            usr["xp_usuario"] += xp
            usr["coin_usuario"] += coins
            guardar_usuarios(usuarios)
            print(Fore.GREEN + f"\n¡Felicidades! Has ganado {xp} XP y {coins} coins." + Style.RESET_ALL)
            break

#Función para restar vida al usuario
def restar_vida(usuario, vida):
    usuarios = cargar_usuarios()
    for usr in usuarios:
        if usr["id_usuario"] == usuario["id_usuario"]:
            usr["vida_usuario"] -= vida
            if usr["vida_usuario"] < 0:
                usr["vida_usuario"] = 0  #La vida no puede ser negativa.
            guardar_usuarios(usuarios)
            print(Fore.RED + f"\nHas perdido {vida} puntos de vida. Vida actual: {usr['vida_usuario']}/50" + Style.RESET_ALL)
            break

"""Todas las tareas dan XP y monedas al completarse.

Las diarias y pendientes penalizan vida si no se cumplen.

La vida máxima es 50, con penalizaciones pequeñas pero acumulativas (−2 o −3).

Esto genera un balance: el usuario se motiva por las recompensas, pero también siente presión por las penalizaciones."""