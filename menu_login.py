from login import login, register, eliminar_usuario
from menu_tareas import menu_tareas
from colorama import Fore, Style

def main():
    print(Fore.YELLOW + f"\n¡Bienvenido al Gestor de Tareas!" + Style.RESET_ALL)
    print(Fore.YELLOW + "Inicia sesión o regístrate para continuar." + Style.RESET_ALL)
    
    while True:
        try:
            opcion = int(input("\n1. Iniciar Sesión\n2. Registrarse\n3. Cancelar\n4. Eliminar Cuenta\nIngresa el número de la opción que deseas realizar: "))
            if opcion == 1:
                print(Fore.YELLOW + "\nHas seleccionado: Iniciar Sesión" + Style.RESET_ALL)
                #Lógica para iniciar sesión
                usuario_actual = login()
                if usuario_actual:
                    menu_tareas(usuario_actual)
            elif opcion == 2:
                print(Fore.YELLOW + "\nHas seleccionado: Registrarse" + Style.RESET_ALL)
                #Lógica para registrarse
                usuario_actual = register()
                if usuario_actual:
                    menu_tareas(usuario_actual)
            elif opcion == 3:
                print(Fore.YELLOW + "\nOperación cancelada. Saliendo del Gestor de Tareas. ¡Hasta luego!" + Style.RESET_ALL)
                break
            elif opcion == 4:
                eliminar_usuario()
            else:
                print(Fore.RED + "\nOpción no válida, por favor intenta de nuevo." + Style.RESET_ALL)
        except ValueError:
            print(Fore.RED + "\nOpción no válida, por favor intenta de nuevo." + Style.RESET_ALL)

if __name__ == "__main__":
    main()