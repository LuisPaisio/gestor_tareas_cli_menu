from tareas import nueva_tarea, ver_tareas, editar_tarea, eliminar_tarea, marcar_completada, marcar_incompleta
from colorama import Fore, Style

print("¡Bienvenido al Gestor de Tareas!")

while True:
    try:
        tarea = int(input("\n1. Nueva Tarea\n2. Ver Tareas\n3. Editar Tarea\n4. Eliminar Tarea\n5. Marcar Tarea como Completada\n6. Marcar Tarea como Incompleta\n7. Salir\nIngresa el número de la tarea que deseas realizar: "))
        if tarea == 1:
            print(Fore.YELLOW + "\nHas seleccionado: Nueva Tarea" + Style.RESET_ALL)
            # Lógica para agregar tarea
            nueva_tarea()
        elif tarea == 2:
            print(Fore.YELLOW + "\nHas seleccionado: Ver Tareas" + Style.RESET_ALL)
            # Lógica para ver tareas
            ver_tareas()
        elif tarea == 3:
            print(Fore.YELLOW + "\nHas seleccionado: Editar Tarea" + Style.RESET_ALL)
            # Lógica para editar tarea
            editar_tarea()
        elif tarea == 4:
            print(Fore.YELLOW + "\nHas seleccionado: Eliminar Tarea" + Style.RESET_ALL)
            # Lógica para eliminar tarea
            eliminar_tarea()
        elif tarea == 5:
            print(Fore.YELLOW + "\nHas seleccionado: Marcar Tarea como Completada" + Style.RESET_ALL)
            # Lógica para marcar tarea como completada
            marcar_completada()
        elif tarea == 6:
            print(Fore.YELLOW + "\nHas seleccionado: Marcar Tarea como Incompleta" + Style.RESET_ALL)
            # Lógica para marcar tarea como completada
            marcar_incompleta()
        elif tarea == 7:
            print(Fore.YELLOW + "\nSaliendo del Gestor de Tareas. ¡Hasta luego!" + Style.RESET_ALL)
            break
        else:
            print(Fore.RED + "\nOpción no válida, por favor intenta de nuevo." + Style.RESET_ALL)
    except ValueError:
        print(Fore.RED + "\nOpción no válida, por favor intenta de nuevo." + Style.RESET_ALL)