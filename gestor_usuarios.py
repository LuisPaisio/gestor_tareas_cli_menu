import json
import os
from colorama import Fore, Style
from usuario import Usuario

ARCHIVO_USUARIOS = "json\\usuarios.json"
ARCHIVO_TAREAS = "json\\tareas.json"

class GestorUsuarios:
    def __init__(self):
        # Carga inicial de usuarios
        self.usuarios = self.cargar_usuarios() #Se asigna a self.usuarios la lista de objetos Usuarios que se obtuvo de return [Usuario.from_dict(u) for u in data]

    # -------------------------------
    # Manejo de usuarios
    # -------------------------------
    def cargar_usuarios(self):
        if os.path.exists(ARCHIVO_USUARIOS):
            try:
                with open(ARCHIVO_USUARIOS, "r", encoding="utf-8") as archivo:
                    contenido = archivo.read().strip()
                    if not contenido:
                        return []
                    data = json.loads(contenido) #Convierte el texto del JSON en una lista de diccionarios.
                    return [Usuario.from_dict(u) for u in data] #list comprehension | Recorro cada elemento u dentro de data. | El metodo Usuario.from_dict(u) convierte el diccionario en un objeto Usuario.
            except json.JSONDecodeError:
                print(Fore.RED + "⚠️ El archivo de usuarios está corrupto o vacío. Se iniciará una lista nueva." + Style.RESET_ALL)
                return []
        return []

    def guardar_usuarios(self):
        with open(ARCHIVO_USUARIOS, "w", encoding="utf-8") as archivo:
            json.dump([u.to_dict() for u in self.usuarios], archivo, indent=4, ensure_ascii=False)
        # Refresco la lista para mantener consistencia
        self.usuarios = self.cargar_usuarios()

    def actualizar_usuario(self, usuario):
        for i, u in enumerate(self.usuarios):
            if u.id_usuario == usuario.id_usuario:
                self.usuarios[i] = usuario
                break
        self.guardar_usuarios()

    # -------------------------------
    # Métodos principales
    # -------------------------------
    def login(self):
        user = input("Ingresa tu nombre de usuario: ")
        password = input("Ingresa tu contraseña: ")
        for usuario in self.usuarios:
            if usuario.usuario == user and usuario.contraseña == password:
                print(Fore.GREEN + f"\n¡Inicio de sesión exitoso!" + Style.RESET_ALL)
                return usuario #De ésta forma se devuelve toda la información del usuario, pero ya no como lista, sino como objeto Usuario.
        print(Fore.RED + "\nNombre de usuario o contraseña incorrectos." + Style.RESET_ALL)
        return None

    def register(self):
        user = input("Elige un nombre de usuario: ")
        password = input("Elige una contraseña: ")

        if len(user) < 8 or len(password) < 8 or user.strip() == "" or password.strip() == "":
            print(Fore.RED + "\nEl nombre de usuario y la contraseña no puede contener menos de 8 caracteres o ser vacía." + Style.RESET_ALL)
            return None

        for usuario in self.usuarios:
            if usuario.usuario == user:
                print(Fore.RED + "\nEl nombre de usuario ya existe." + Style.RESET_ALL)
                return None

        ultimo_id = max([u.id_usuario for u in self.usuarios], default=0)
        nuevo_usuario = Usuario(id_usuario=ultimo_id + 1, usuario=user, contraseña=password)

        self.usuarios.append(nuevo_usuario)
        self.guardar_usuarios()

        print(Fore.GREEN + f"\n¡Registro exitoso!" + Style.RESET_ALL)
        return nuevo_usuario

    def eliminar_usuario(self):
        confirmar = input(
            "\nAdvertencia: Esta acción eliminará tu cuenta permanentemente. "
            "Presiona Enter para continuar o N para cancelar: "
        )
        if confirmar.lower() == "n":
            print(Fore.YELLOW + "\nOperación cancelada." + Style.RESET_ALL)
            return None

        user = input("Ingresa tu nombre de usuario para eliminar la cuenta: ")
        password = input("Ingresa tu contraseña: ")

        for usuario in self.usuarios:
            if usuario.usuario == user and usuario.contraseña == password:
                # Elimino usuario
                self.usuarios.remove(usuario)
                self.guardar_usuarios()

                print(Fore.GREEN + f"\nCuenta '{user}' eliminada exitosamente." + Style.RESET_ALL)
                return True

        print(Fore.RED + "\nNombre de usuario o contraseña incorrectos." + Style.RESET_ALL)
        return None

