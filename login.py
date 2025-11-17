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

def login():
    user = input("Ingresa tu nombre de usuario: ")
    password = input("Ingresa tu contraseña: ")
    usuarios = cargar_usuarios()
    for usuario in usuarios:
        if usuario["usuario"] == user and usuario["contraseña"] == password:
            print(Fore.GREEN + f"\n¡Inicio de sesión exitoso! Bienvenido de nuevo, {user}." + Style.RESET_ALL)
            return usuario #Devuelvo todo el diccionario del usuario.
    print(Fore.RED + "\nNombre de usuario o contraseña incorrectos. Por favor, intenta de nuevo." + Style.RESET_ALL)
    return None

def register(): 
    user = input("Elige un nombre de usuario: ")
    password = input("Elige una contraseña: ")
    usuarios = cargar_usuarios()
    for usuario in usuarios:
        if usuario["usuario"] == user:
            print(Fore.RED + "\nEl nombre de usuario ya existe. Por favor, elige otro." + Style.RESET_ALL)
            return None
    nuevo_usuario = {"id_usuario":len(usuarios) + 1, "usuario": user, "contraseña": password}
    usuarios.append(nuevo_usuario)
    guardar_usuarios(usuarios)
    print(Fore.GREEN + f"\n¡Registro exitoso! Bienvenido, {user}." + Style.RESET_ALL)
    return usuario #Retorno el diccionario del nuevo usuario.

def eliminar_usuario():
    confirmar = input("\nAdvertencia: Esta acción eliminará tu cuenta permanentemente. Presiona Enter para continuar o N para cancelar.")
    if confirmar != "":
        print(Fore.YELLOW + "\nOperación cancelada." + Style.RESET_ALL)
        return None
    else:
        user = input("Ingresa tu nombre de usuario para eliminar la cuenta: ")
        password = input("Ingresa tu contraseña: ")
        usuarios = cargar_usuarios()
        for usuario in usuarios:
            if usuario["usuario"] == user and usuario["contraseña"] == password:
                usuarios.remove(usuario)
                guardar_usuarios(usuarios)
                print(Fore.GREEN + f"\nCuenta '{user}' eliminada exitosamente." + Style.RESET_ALL)
                return True
        print(Fore.RED + "\nNombre de usuario o contraseña incorrectos. No se pudo eliminar la cuenta." + Style.RESET_ALL)
        return None