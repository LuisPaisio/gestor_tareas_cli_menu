import json
import os
from colorama import Fore, Style

#Funciones para la gestión de xp y coins de los usuarios.
#--------------------------------------------------------
#cargo documento de usuarios
ARCHIVO_USUARIOS = "json\\usuarios.json"
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
#--------------------------------------------------------
# Defino el monto de XP en una función para facilitar futuros cambios, según tareas que sean hábitos, diarias o pendientes.
def xp_habito():
    return 10  #XP por completar un hábito

def xp_diaria():
    return 20  #XP por completar una diaria

def xp_pendiente():
    return 30  #XP por completar una pendiente
#--------------------------------------------------------
#Defino el monto de COINS en una función para facilitar futuros cambios, según tareas que sean hábitos, diarias o pendientes.
def coin_habito():
    return 5

def coin_diaria():
    return 10

def coin_pendiente():
    return 15
#--------------------------------------------------------
#Defino la vida que se resta al usuario por no completar tareas, según sean Hábito, Diaria o Pendiente.
def vida_habito(): #Resto vida por no completar un hábito.
    return 2

def vida_diaria(): #Resto vida por no completar una diaria pasada las 00:00hs.
    return 3

def vida_pendiente(): #Resto vida por no completar una pendiente pasada su fecha de vencimiento.
    return 5
#--------------------------------------------------------
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

#Sumo XP y Coins al usuario por hábito positivo
def sumar_xp_coins_habito(usuario, xp, coins):
    usuarios = cargar_usuarios()
    for usr in usuarios:
        if usr["id_usuario"] == usuario["id_usuario"]:
            usr["xp_usuario"] += xp
            usr["coin_usuario"] += coins
            guardar_usuarios(usuarios)
            print(" Has sumado" + Fore.YELLOW + f" {xp} XP" + Style.RESET_ALL +  " y " + Fore.YELLOW + f" {coins} " + Style.RESET_ALL + "coins.")
            break

#Función para restar vida al usuario
def restar_vida(usuario, vida):
    usuarios = cargar_usuarios()
    for usr in usuarios:
        if usr["id_usuario"] == usuario["id_usuario"]:
            usr["vida_usuario"] -= vida
            if usr["vida_usuario"] <= 0:
                usr["vida_usuario"] = 0  #La vida no puede ser negativa.
                print (Fore.RED + f"Tu vida llegó a 0." + Style.RESET_ALL)
                #Penalizaciones.
                xp_perdido = 15
                coins_perdidos = 10
                usr["xp_usuario"] = max(0, usr["xp_usuario"] - xp_perdido)
                usr["coin_usuario"] = max(0, usr["coin_usuario"] - coins_perdidos)
                print (Fore.YELLOW + f"Has perdido {xp_perdido} XP, {coins_perdidos} y todo lo que tenías equipado." + Style.RESET_ALL)
                print (Fore.YELLOW + f"Tu salud ha sido restaurada {usr["vida_usuario"]}" + Style.RESET_ALL)
                #Restauro la vida.
                usr["vida_usuario"] = 50
                return #Retorno para que no siga con el siguiente print.
            guardar_usuarios(usuarios)
            print(Fore.RED + f"\nHas perdido {vida} puntos de vida. Vida actual: {usr['vida_usuario']}/50" + Style.RESET_ALL)
            break

#Función para restar vida al usuario por hábito negativo
def restar_vida_habito(usuario, vida):
    usuarios = cargar_usuarios()
    for usr in usuarios:
        if usr["id_usuario"] == usuario["id_usuario"]:
            usr["vida_usuario"] -= vida
            if usr["vida_usuario"] <= 0:
                usr["vida_usuario"] = 0  #La vida no puede ser negativa.
                print (Fore.RED + f"Tu vida llegó a 0." + Style.RESET_ALL)
                #Penalizaciones.
                xp_perdido = 15
                coins_perdidos = 10
                usr["xp_usuario"] = max(0, usr["xp_usuario"] - xp_perdido)
                usr["coin_usuario"] = max(0, usr["coin_usuario"] - coins_perdidos)
                print (Fore.YELLOW + f"Has perdido {xp_perdido} XP, {coins_perdidos} y todo lo que tenías equipado." + Style.RESET_ALL)
                print (Fore.YELLOW + f"Tu salud ha sido restaurada {usr["vida_usuario"]}" + Style.RESET_ALL)
                #Restauro la vida.
                usr["vida_usuario"] = 50
                return #Retorno para que no siga con el siguiente print.
            guardar_usuarios(usuarios)
            print(Fore.RED + f"\nHas perdido {vida} puntos de vida. Vida actual: {usr['vida_usuario']}/50" + Style.RESET_ALL)
            break

"""Todas las tareas dan XP y monedas al completarse.

Las diarias y pendientes penalizan vida si no se cumplen.

La vida máxima es 50, con penalizaciones pequeñas pero acumulativas (−2 o −3).

Esto genera un balance: el usuario se motiva por las recompensas, pero también siente presión por las penalizaciones."""