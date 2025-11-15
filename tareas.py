import json
import os
from colorama import Fore, Style

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

#Creo nueva tarea
def nueva_tarea():
    titulo = input("Ingresa el título de la nueva tarea | 0 (cero) cancelar: ")
    if titulo == "0":
        cancelar = input("¿Deseas cancelar la operación? (s/n): ")
        if cancelar.lower() == 's':
            print(Fore.YELLOW + f"\nOperación cancelada." + Style.RESET_ALL)
            return
    else:
        tareas = cargar_tareas()
        nueva = {"id": len(tareas) + 1, "titulo": titulo, "completada": False}
        tareas.append(nueva)
        guardar_tareas(tareas)
        print(f"Tarea '{titulo}' agregada exitosamente.")
    
#Veo tareas
def ver_tareas():
    tareas = cargar_tareas()
    if not tareas:
        print(f"\nNo hay tareas disponibles.")
        return
    print("\nLista de Tareas:\n")
    for tarea in tareas:
        estado = Fore.RED + "Incompleta" + Style.RESET_ALL
        if tarea["completada"]:
            estado = Fore.GREEN + "Completada" + Style.RESET_ALL
        print(f"{tarea["id"]}. {tarea["titulo"]} - {estado}")

def editar_tarea():
    ver_tareas()
    try:
        id_tarea = int(input("\nIngresa el ID de la tarea que deseas editar | 0 (cero) cancelar: "))
        tareas = cargar_tareas()
        tarea_a_editar = None
        for tarea in tareas:
            if tarea["id"] == id_tarea:
                tarea_a_editar = tarea
                break
        if tarea_a_editar:
            nuevo_titulo = input(f"Ingresa el nuevo título para la tarea '{tarea_a_editar['titulo']}': ")
            tarea_a_editar["titulo"] = nuevo_titulo
            guardar_tareas(tareas)
            print(f"Tarea ID {id_tarea}" + Fore.YELLOW +  " actualizada exitosamente." + Style.RESET_ALL)
        elif id_tarea == 0:
            cancelar = input("¿Deseas cancelar la operación? (s/n): ")
            if cancelar.lower() == 's':
                print(Fore.YELLOW + f"\nOperación cancelada." + Style.RESET_ALL)
                return
        else:
            print(Fore.RED + "⚠️ Tarea no encontrada." + Style.RESET_ALL)
    except ValueError:
        print(Fore.RED + "⚠️ Entrada inválida. Por favor ingresa un número válido." + Style.RESET_ALL)

#Eliminar tarea
def eliminar_tarea():
    ver_tareas()
    try:
        id_tarea = int(input("\nIngresa el ID de la tarea que deseas eliminar | 0 (cero) cancelar: "))
        tareas = cargar_tareas()
        #tarea_a_eliminar = next((tarea for tarea in tareas if tarea["id"] == id_tarea), None) #Es una forma de evitar escribir un bucle for con break.
        tarea_a_eliminar = None
        for tarea in tareas:
            if tarea["id"] == id_tarea:
                tarea_a_eliminar = tarea
                break
        if tarea_a_eliminar:
            tareas.remove(tarea_a_eliminar)
            guardar_tareas(tareas)
            print(f"Tarea '{tarea_a_eliminar['titulo']}'" + Fore.RED +  " eliminada exitosamente." + Style.RESET_ALL)
        elif id_tarea == 0:
            cancelar = input("¿Deseas cancelar la operación? (s/n): ")
            if cancelar.lower() == 's':
                print(Fore.YELLOW + f"\nOperación cancelada." + Style.RESET_ALL)
                return
        else:
            print(Fore.RED + "⚠️ Tarea no encontrada." + Style.RESET_ALL)
    except ValueError:
        print(Fore.RED + "⚠️ Entrada inválida. Por favor ingresa un número válido." + Style.RESET_ALL)
        
#Marcar tarea como completada
def marcar_completada():
    ver_tareas()
    try:
        id_tarea = int(input("\nIngresa el ID de la tarea que deseas marcar como completada | 0 (cero) cancelar: "))
        tareas = cargar_tareas()
        tarea_a_marcar = None
        for tarea in tareas:
            if tarea["id"] == id_tarea:
                tarea_a_marcar = tarea
                break
        if tarea_a_marcar:
            tarea_a_marcar["completada"] = True
            guardar_tareas(tareas)
            print(f"Tarea" + Fore.YELLOW + f" {tarea_a_marcar['titulo']} " + Style.RESET_ALL + "marcada como " + Fore.GREEN + "completada." + Style.RESET_ALL)
        elif id_tarea == 0:
            cancelar = input("¿Deseas cancelar la operación? (s/n): ")
            if cancelar.lower() == 's':
                print(Fore.YELLOW + f"\nOperación cancelada." + Style.RESET_ALL)
                return
        else:
            print(Fore.RED + "⚠️ Tarea no encontrada." + Style.RESET_ALL)
    except ValueError:
        print(Fore.RED + "⚠️ Entrada inválida. Por favor ingresa un número válido." + Style.RESET_ALL)

#Marcar tarea como incompleta
def marcar_incompleta():
    ver_tareas()
    try:
        id_tarea = int(input("\nIngresa el ID de la tarea que deseas marcar como incompleta | 0 (cero) cancelar: "))
        tareas = cargar_tareas()
        tarea_a_marcar = None
        for tarea in tareas:
            if tarea["id"] == id_tarea:
                tarea_a_marcar = tarea
                break
        if tarea_a_marcar:
            tarea_a_marcar["completada"] = False
            guardar_tareas(tareas)
            print(f"Tarea" + Fore.YELLOW + f" {tarea_a_marcar['titulo']} " + Style.RESET_ALL + "marcada como " + Fore.RED + "incompleta." + Style.RESET_ALL)
        elif id_tarea == 0:
            cancelar = input("¿Deseas cancelar la operación? (s/n): ")
            if cancelar.lower() == 's':
                print(Fore.YELLOW + f"\nOperación cancelada." + Style.RESET_ALL)
                return
        else:
            print(Fore.RED + "⚠️ Tarea no encontrada." + Style.RESET_ALL)
    except ValueError:
        print(Fore.RED + "⚠️ Entrada inválida. Por favor ingresa un número válido." + Style.RESET_ALL)
