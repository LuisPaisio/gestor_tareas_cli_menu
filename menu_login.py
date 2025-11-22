from gestor_usuarios import GestorUsuarios
from menu_tareas import menu_tareas
from colorama import Fore, Style
from gestor_tareas import GestorTareas

def main():
    print(Fore.YELLOW + f"\n¡Bienvenido al Gestor de Tareas!" + Style.RESET_ALL)
    print(Fore.YELLOW + "Inicia sesión o regístrate para continuar." + Style.RESET_ALL)

    gestor = GestorUsuarios()  # instanciamos el gestor de usuarios, ya tenemos la lista de usuarios cargados en el JSON
    gestorT = GestorTareas()

    while True:
        try:
            opcion = int(input("\n1. Iniciar Sesión\n""2. Registrarse\n""3. Cancelar\n""4. Eliminar Cuenta\n""Ingresa el número de la opción que deseas realizar: "))

            if opcion == 1:
                print(Fore.YELLOW + "\nHas seleccionado: Iniciar Sesión" + Style.RESET_ALL)
                usuario_actual = gestor.login()
                if usuario_actual:
                    # pasamos usuario_actual y gestor de usuarios
                    menu_tareas(usuario_actual, gestor)

            elif opcion == 2:
                print(Fore.YELLOW + "\nHas seleccionado: Registrarse" + Style.RESET_ALL)
                usuario_actual = gestor.register()
                if usuario_actual:
                    # pasamos usuario_actual y gestor de usuarios
                    menu_tareas(usuario_actual, gestor)

            elif opcion == 3:
                print(Fore.YELLOW + "\nOperación cancelada. Saliendo del Gestor de Tareas. ¡Hasta luego!" + Style.RESET_ALL)
                break

            elif opcion == 4:
                gestor.eliminar_usuario(gestorT)

            else:
                print(Fore.RED + "\nOpción no válida, por favor intenta de nuevo." + Style.RESET_ALL)

        except ValueError:
            print(Fore.RED + "\nOpción no válida, por favor intenta de nuevo." + Style.RESET_ALL)

if __name__ == "__main__":
    main()
