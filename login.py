import json
import os
from colorama import Fore, Style

#cargo documento de usuarios
ARCHIVO_USUARIOS = "usuarios.json"
def cargar_usuarios():
    if os.path.exists(ARCHIVO_USUARIOS):
        try:
            with open(ARCHIVO_USUARIOS, "r") as archivo:
                contenido = archivo.read().strip()
                if not contenido:
                    return []
                return json.loads(contenido)
        except json.JSONDecodeError:
            print(Fore.RED + "⚠️ El archivo de usuarios está corrupto o vacío. Se iniciará una lista nueva." + Style.RESET_ALL)
            return []
    else:
        return []

#guardo documento de usuarios
def guardar_usuarios(usuarios):
    with open(ARCHIVO_USUARIOS, "w") as archivo:
        json.dump(usuarios, archivo, indent=4)

#----------------------------------------------------------------
#cargo documento de tareas
ARCHIVO_TAREAS = "tareas.json"
def cargar_tareas():
    if os.path.exists(ARCHIVO_TAREAS):
        try:
            with open(ARCHIVO_TAREAS, "r") as archivo:
                contenido = archivo.read().strip()
                if not contenido:
                    return []
                return json.loads(contenido)
        except json.JSONDecodeError:
            print(Fore.RED + "⚠️ El archivo de tareas está corrupto o vacío. Se iniciará una lista nueva." + Style.RESET_ALL)
            return []
    else:
        return []

#Guardo documento de tareas 
def guardar_tareas(tareas):
    with open(ARCHIVO_TAREAS, "w") as archivo:
        json.dump(tareas, archivo, indent=4)
#----------------------------------------------------------------

def login():
    user = input("Ingresa tu nombre de usuario: ")
    password = input("Ingresa tu contraseña: ")
    usuarios = cargar_usuarios()
    for usuario in usuarios:
        if usuario["usuario"] == user and usuario["contraseña"] == password:
            print(Fore.GREEN + f"\n¡Inicio de sesión exitoso!" + Style.RESET_ALL)
            return usuario #Devuelvo todo el diccionario del usuario.
    print(Fore.RED + "\nNombre de usuario o contraseña incorrectos. Por favor, intenta de nuevo." + Style.RESET_ALL)
    return None

def register(): 
    user = input("Elige un nombre de usuario: ")
    password = input("Elige una contraseña: ")
    if len(user) < 8 or len(password) < 8 or user == "" or password == "" or user.isspace() or password.isspace():
        print(Fore.RED + "\nEl nombre de usuario y la contraseña no puede contener menos de 8 caracteres o ser vacía. Por favor, intenta de nuevo." + Style.RESET_ALL)
        return None
    else:
        usuarios = cargar_usuarios()
    
        ultimo_id = []
        for usuario in usuarios: #Obtengo el último ID usado.
            ultimo_id.append(usuario["id_usuario"])
    
        for usuario in usuarios:
            if usuario["usuario"] == user:
                print(Fore.RED + "\nEl nombre de usuario ya existe. Por favor, elige otro." + Style.RESET_ALL)
                return None
        nuevo_usuario = {"id_usuario":max(ultimo_id) + 1, "usuario": user, "contraseña": password}
        usuarios.append(nuevo_usuario)
        guardar_usuarios(usuarios)
        print(Fore.GREEN + f"\n¡Registro exitoso!" + Style.RESET_ALL)
        return nuevo_usuario #Retorno el diccionario del nuevo usuario.

def eliminar_usuario():
    confirmar = input("\nAdvertencia: Esta acción eliminará tu cuenta permanentemente. Presiona Enter para continuar o N para cancelar.")
    if confirmar != "":
        print(Fore.YELLOW + "\nOperación cancelada." + Style.RESET_ALL)
        return None
    else:
        user = input("Ingresa tu nombre de usuario para eliminar la cuenta: ")
        password = input("Ingresa tu contraseña: ")
        usuarios = cargar_usuarios()
        tareas = cargar_tareas()
        #Elimino el usuario y sus tareas asociadas
        for usuario in usuarios:
            if usuario["usuario"] == user and usuario["contraseña"] == password:
                #Elimino el usuario
                usuarios.remove(usuario)
                guardar_usuarios(usuarios)
                #Elimino las tareas asociadas al usuario eliminado
                tareas_actualizadas = [tarea for tarea in tareas if tarea["id_usuario"] != usuario["id_usuario"]]
                guardar_tareas(tareas_actualizadas)
                print(Fore.GREEN + f"\nCuenta '{user}' eliminada exitosamente." + Style.RESET_ALL)
                return True
        print(Fore.RED + "\nNombre de usuario o contraseña incorrectos. No se pudo eliminar la cuenta." + Style.RESET_ALL)
        return None
    