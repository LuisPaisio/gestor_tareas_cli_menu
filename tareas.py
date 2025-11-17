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

#Creo nueva tarea
def nueva_tarea(usuario):
    titulo = input("Ingresa el título de la nueva tarea | 0 (cero) cancelar: ")
    if titulo == "0":
        cancelar = input("¿Deseas cancelar la operación? (s/n): ")
        if cancelar.lower() == 's':
            print(Fore.YELLOW + f"\nOperación cancelada." + Style.RESET_ALL)
            return
    else:
        tareas = cargar_tareas()
        
        ultimo_id = []
        for tarea in tareas: #Busco el último ID usado.
            ultimo_id.append(tarea["id"])
        
        if ultimo_id: #Si la lista no está vacía.
            nueva = {"id": max(ultimo_id)+1, "titulo": titulo, "completada": False, "id_usuario": usuario["id_usuario"]}
            tareas.append(nueva)
            guardar_tareas(tareas)
            print(f"Tarea '{titulo}' agregada exitosamente.")
        else: #Si la lista está vacía.
            nueva = {"id": 1, "titulo": titulo, "completada": False, "id_usuario": usuario["id_usuario"]}
            tareas.append(nueva)
            guardar_tareas(tareas)
            print(f"Tarea '{titulo}' agregada exitosamente.")
    
#Veo tareas
def ver_tareas(usuario):
    tareas = cargar_tareas()
    tareas_usuario = []
    for tarea in tareas[:]:
        if tarea["id_usuario"] == usuario["id_usuario"]:
            tareas_usuario.append(tarea)

    if not tareas_usuario:
        print(f"\nNo hay tareas disponibles.")
        return

    print("\nLista de Tareas:\n")
    for contador, tarea in enumerate(tareas_usuario, start=1): #Muestro solo las tareas del usuario actual y enumero la lista.
        estado = Fore.RED + "Incompleta" + Style.RESET_ALL
        if tarea["completada"]:
            estado = Fore.GREEN + "Completada" + Style.RESET_ALL
        print(f"{contador}. {tarea["titulo"]} - {estado}")

def editar_tarea(usuario):
    ver_tareas(usuario)
    try:
        seleccion = int(input("\nIngresa el ID de la tarea que deseas editar | 0 (cero) cancelar: "))
        tareas = cargar_tareas()
        
        tareas_usuario = [] #Filtro las tareas del usuario actual.
        for tarea in tareas[:]:
            if tarea["id_usuario"] == usuario["id_usuario"]:
                tareas_usuario.append(tarea)
        
        tarea_a_editar = None
        if 1 <= seleccion <= len(tareas_usuario): #Busco la tarea a editar entre las tareas del usuario actual.
            tarea_a_editar = tareas_usuario[seleccion - 1]
        
        if tarea_a_editar:
            nuevo_titulo = input(f"Ingresa el nuevo título para la tarea '{tarea_a_editar['titulo']}': ")
            tarea_a_editar["titulo"] = nuevo_titulo
            guardar_tareas(tareas)
            print(f"Tarea '{tarea_a_editar['titulo']}'" + Fore.YELLOW +  " actualizada exitosamente." + Style.RESET_ALL)
        elif seleccion == 0:
            cancelar = input("¿Deseas cancelar la operación? (s/n): ")
            if cancelar.lower() == 's':
                print(Fore.YELLOW + f"\nOperación cancelada." + Style.RESET_ALL)
                return
        else:
            print(Fore.RED + "⚠️ Tarea no encontrada." + Style.RESET_ALL)
    except ValueError:
        print(Fore.RED + "⚠️ Entrada inválida. Por favor ingresa un número válido." + Style.RESET_ALL)

#Eliminar tarea
def eliminar_tarea(usuario):
    ver_tareas(usuario)
    try:
        seleccion = int(input("\nIngresa el ID de la tarea que deseas eliminar | 0 (cero) cancelar: "))
        tareas = cargar_tareas()
        #tarea_a_eliminar = next((tarea for tarea in tareas if tarea["id"] == id_tarea), None) #Es una forma de evitar escribir un bucle for con break.
        
        tareas_usuario = [] 
        for tarea in tareas[:]: #Filtro las tareas del usuario actual.
            if tarea["id_usuario"] == usuario["id_usuario"]:
                tareas_usuario.append(tarea)
                
        tarea_a_eliminar = None 
        if 1 <= seleccion <= len(tareas_usuario): #Busco la tarea a eliminar entre las tareas del usuario actual.
            tarea_a_eliminar = tareas_usuario[seleccion - 1]

        if tarea_a_eliminar:
            tareas.remove(tarea_a_eliminar)
            guardar_tareas(tareas)
            print(f"Tarea '{tarea_a_eliminar['titulo']}'" + Fore.RED +  " eliminada exitosamente." + Style.RESET_ALL)
        elif seleccion == 0:
            cancelar = input("¿Deseas cancelar la operación? (s/n): ")
            if cancelar.lower() == 's':
                print(Fore.YELLOW + f"\nOperación cancelada." + Style.RESET_ALL)
                return
        else:
            print(Fore.RED + "⚠️ Tarea no encontrada." + Style.RESET_ALL)
    except ValueError:
        print(Fore.RED + "⚠️ Entrada inválida. Por favor ingresa un número válido." + Style.RESET_ALL)
        
#Marcar tarea como completada
def marcar_completada(usuario):
    ver_tareas(usuario)
    try:
        seleccion = int(input("\nIngresa el ID de la tarea que deseas marcar como completada | 0 (cero) cancelar: "))
        tareas = cargar_tareas()
        
        tareas_usuario = [] 
        for tarea in tareas[:]: #Filtro las tareas del usuario actual.
            if tarea["id_usuario"] == usuario["id_usuario"]:
                tareas_usuario.append(tarea)
        
        tarea_a_marcar = None
        if 1 <= seleccion <= len(tareas_usuario): #Busco la tarea a marcar entre las tareas del usuario actual.
            tarea_a_marcar = tareas_usuario[seleccion - 1]
        
        if tarea_a_marcar:
            tarea_a_marcar["completada"] = True
            guardar_tareas(tareas)
            print(f"Tarea" + Fore.YELLOW + f" {tarea_a_marcar['titulo']} " + Style.RESET_ALL + "marcada como " + Fore.GREEN + "completada." + Style.RESET_ALL)
        elif seleccion == 0:
            cancelar = input("¿Deseas cancelar la operación? (s/n): ")
            if cancelar.lower() == 's':
                print(Fore.YELLOW + f"\nOperación cancelada." + Style.RESET_ALL)
                return
        else:
            print(Fore.RED + "⚠️ Tarea no encontrada." + Style.RESET_ALL)
    except ValueError:
        print(Fore.RED + "⚠️ Entrada inválida. Por favor ingresa un número válido." + Style.RESET_ALL)

#Marcar tarea como incompleta
def marcar_incompleta(usuario):
    ver_tareas(usuario)
    try:
        seleccion = int(input("\nIngresa el ID de la tarea que deseas marcar como incompleta | 0 (cero) cancelar: "))
        tareas = cargar_tareas()
        
        tareas_usuario = [] 
        for tarea in tareas[:]: #Filtro las tareas del usuario actual.
            if tarea["id_usuario"] == usuario["id_usuario"]:
                tareas_usuario.append(tarea)
        
        tarea_a_marcar = None
        if 1 <= seleccion <= len(tareas_usuario):
            tarea_a_marcar = tareas_usuario[seleccion - 1]
            
        if tarea_a_marcar:
            tarea_a_marcar["completada"] = False
            guardar_tareas(tareas)
            print(f"Tarea" + Fore.YELLOW + f" {tarea_a_marcar['titulo']} " + Style.RESET_ALL + "marcada como " + Fore.RED + "incompleta." + Style.RESET_ALL)
        elif seleccion == 0:
            cancelar = input("¿Deseas cancelar la operación? (s/n): ")
            if cancelar.lower() == 's':
                print(Fore.YELLOW + f"\nOperación cancelada." + Style.RESET_ALL)
                return
        else:
            print(Fore.RED + "⚠️ Tarea no encontrada." + Style.RESET_ALL)
    except ValueError:
        print(Fore.RED + "⚠️ Entrada inválida. Por favor ingresa un número válido." + Style.RESET_ALL)
