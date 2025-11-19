from gestor_tareas import GestorTareas
from colorama import Fore, Style

def menu_tareas(usuario, gestor_usuarios):
    print(Fore.GREEN + f"\n¡Bienvenido al Gestor de Tareas, {usuario.usuario}!" + Style.RESET_ALL)

    # ahora pasamos usuario y gestor_usuarios al constructor
    gestor = GestorTareas(usuario, gestor_usuarios)

    while True:
        try:
            tarea = int(input(
                "\n1. Nueva Tarea\n"
                "2. Ver Tareas\n"
                "3. Editar Tarea\n"
                "4. Eliminar Tarea\n"
                "5. Marcar Tarea\n"
                "6. Salir\n"
                "Ingresa el número de la tarea que deseas realizar: "
            ))

            if tarea == 1:
                print(Fore.YELLOW + "\nHas seleccionado: Nueva Tarea" + Style.RESET_ALL)
                gestor.nueva_tarea()

            elif tarea == 2:
                print(Fore.YELLOW + "\nHas seleccionado: Ver Tareas" + Style.RESET_ALL)
                gestor.ver_tareas()

            elif tarea == 3:
                print(Fore.YELLOW + "\nHas seleccionado: Editar Tarea" + Style.RESET_ALL)
                gestor.editar_tarea()

            elif tarea == 4:
                print(Fore.YELLOW + "\nHas seleccionado: Eliminar Tarea" + Style.RESET_ALL)
                gestor.eliminar_tarea()

            elif tarea == 5:
                print(Fore.YELLOW + "\nHas seleccionado: Marcar Tarea" + Style.RESET_ALL)
                gestor.marcar_tarea()

            elif tarea == 6:
                print(Fore.YELLOW + "\nSaliendo del Gestor de Tareas. ¡Hasta luego!" + Style.RESET_ALL)
                break

            else:
                print(Fore.RED + "\nOpción no válida, por favor intenta de nuevo." + Style.RESET_ALL)

        except ValueError:
            print(Fore.RED + "\nOpción no válida, por favor intenta de nuevo." + Style.RESET_ALL)
