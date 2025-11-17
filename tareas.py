import json
import os
from colorama import Fore, Style
import datetime
from xp_monedas_vida import xp_habito, xp_diaria, xp_pendiente, coin_habito, coin_diaria, coin_pendiente, vida_habito, vida_diaria, vida_pendiente, sumar_xp_coins, restar_vida

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
        elif cancelar.lower() == 'n':
            nueva_tarea(usuario) #Vuelvo a llamar a la función para que el usuario pueda ingresar un título.
        else:
            print(Fore.RED + "⚠️ Opción no válida. La tarea no se creará." + Style.RESET_ALL)
            return
    elif titulo == "":
        print(Fore.RED + "⚠️ El título de la tarea no puede estar vacío. La tarea no se creará." + Style.RESET_ALL)
        return
    elif titulo.isspace():
        print(Fore.RED + "⚠️ El título de la tarea no puede estar vacío. La tarea no se creará." + Style.RESET_ALL)
        return
    else:
        tareas = cargar_tareas()
        
        tipo_tarea = int(input("Ingresa el tipo de tarea. Hábito(1), Diaria(2), Pendiente(3): "))
        dias_semana = []
        fecha_vencimiento = None
        fecha_str = None
        
        if tipo_tarea == 1: 
            dias_semana.append("todos") #Los hábitos se repiten todos los días.
            xp_tarea = xp_habito()
            coin_tarea = coin_habito()
            life_restar = vida_habito()
        
        elif tipo_tarea == 2: #Las diarias se repiten ciertos días de la semana.
            xp_tarea = xp_diaria()
            coin_tarea = coin_diaria()
            life_restar = vida_diaria()
            while True:
                try:
                    dias_seleccionado = input("selecciona los días de la semana (Lunes(1), Martes(2), Miércoles(3), Jueves(4), Viernes(5), Sábado(6), Domingo(7), Listo(0)): ")
                    if dias_seleccionado == "1":
                        dias_semana.append("Lunes")
                    elif dias_seleccionado == "2":
                        dias_semana.append("Martes")
                    elif dias_seleccionado == "3":
                        dias_semana.append("Miercoles")
                    elif dias_seleccionado == "4":
                        dias_semana.append("Jueves")
                    elif dias_seleccionado == "5":
                        dias_semana.append("Viernes")
                    elif dias_seleccionado == "6":
                        dias_semana.append("Sabado")
                    elif dias_seleccionado == "7":
                        dias_semana.append("Domingo")
                    elif dias_seleccionado == "0":
                        break
                    else:
                        print(Fore.RED + "⚠️ Día no válido. La tarea no se creará." + Style.RESET_ALL)
                        return
                except ValueError:
                    print(Fore.RED + "⚠️ Entrada inválida. Por favor ingresa un número válido." + Style.RESET_ALL)
        
        
        elif tipo_tarea == 3: #Las pendientes tienen una fecha de vencimiento o no.
            poner_fecha = input("¿Deseas poner una fecha de vencimiento? (s/n): ").lower() #Si no se pone, queda como tarea pendiente sin fecha.
            xp_tarea = xp_pendiente()
            coin_tarea = coin_pendiente()
            life_restar = vida_pendiente()
            try:
                if poner_fecha == "n": #No pongo fecha de vencimiento.
                    fecha_vencimiento = None
                elif poner_fecha == "s":#Pongo fecha de vencimiento.
                    fecha_vencimiento = input("Ingresa la fecha de vencimiento (DD-MM-AAAA): ")
                    try:
                        fecha_vencimiento = datetime.datetime.strptime(fecha_vencimiento, "%d-%m-%Y").date() #Valido formato de fecha.
                        fecha_str = fecha_vencimiento.strftime("%d-%m-%Y") #Vuelvo a convertir la fecha a string para guardarla en el JSON.
                    except ValueError:
                        print(Fore.RED + "⚠️ Formato de fecha inválido. La tarea no se creará." + Style.RESET_ALL)
                        return
                else:
                    print(Fore.RED + "⚠️ Opción no válida. La tarea no se creará." + Style.RESET_ALL)
                    return
            except ValueError:
                print(Fore.RED + "⚠️ Entrada inválida. La tarea no se creará." + Style.RESET_ALL)
                return
        else:
            print(Fore.RED + "⚠️ Tipo de tarea no válido. La tarea no se creará." + Style.RESET_ALL)
            return
        
        ultimo_id = []
        for tarea in tareas: #Obtengo el último ID usado.
            ultimo_id.append(tarea["id"])
        
        if ultimo_id: #Si la lista no está vacía.
            nueva = {"id": max(ultimo_id)+1, "titulo": titulo, "completada": False, "tipo": tipo_tarea, "dias_semana":dias_semana, "fecha_vencimiento": fecha_str, "xp_reward": xp_tarea, "coin_reward": coin_tarea, "vida_restar": life_restar, "id_usuario": usuario["id_usuario"]}
            tareas.append(nueva)
            guardar_tareas(tareas)
            print(Fore.YELLOW + f"Tarea '{titulo}' agregada exitosamente." + Style.RESET_ALL)
        else: #Si la lista está vacía.
            nueva = {"id": 1, "titulo": titulo, "completada": False, "tipo":"", "dias_semana":"", "fecha_vencimiento": None, "xp_reward": 0, "coin_reward": 0, "id_usuario": usuario["id_usuario"]}
            tareas.append(nueva)
            guardar_tareas(tareas)
            print(Fore.YELLOW + f"Tarea '{titulo}' agregada exitosamente." + Style.RESET_ALL)
    
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

    print("\nLista de Tareas:")
    
    tareas_usuario.sort(
        key=lambda x: (
            x['tipo'],
            datetime.datetime.strptime(x['fecha_vencimiento'], "%d-%m-%Y")
            if x['tipo'] == 3 and x['fecha_vencimiento'] not in (None, "Sin fecha") else datetime.datetime.max
        )
    )
    
    
    for contador, tarea in enumerate(tareas_usuario, start=1): #Muestro solo las tareas del usuario actual y enumero la lista.
        estado = Fore.RED + "Incompleta" + Style.RESET_ALL
        if tarea["completada"]:
            estado = Fore.GREEN + "Completada" + Style.RESET_ALL
        if tarea["fecha_vencimiento"] is None:
            tarea["fecha_vencimiento"] = "Sin fecha"
        if tarea["dias_semana"] == []:
            tarea["dias_semana"] = ["No aplica"]
        #identifico el nombre del tipo de tarea
        tipos = {1: "Hábito", 2: "Tarea Diaria", 3: "Tarea Pendiente"}
        tipo_nombre = tipos.get(tarea["tipo"], "Desconocido")
        print(f"{contador}. {tarea["titulo"]} - {estado} | {tipo_nombre} | Días: {', '.join(tarea['dias_semana'])} | Vencimiento: {tarea['fecha_vencimiento']}")

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
            print(f"\nTarea" + Fore.YELLOW + f" {tarea_a_marcar['titulo']} " + Style.RESET_ALL + "marcada como " + Fore.GREEN + "completada." + Style.RESET_ALL)
            sumar_xp_coins(usuario, tarea_a_marcar['xp_reward'], tarea_a_marcar['coin_reward']) #Sumo XP y coins al usuario según la tarea completada.
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
            restar_vida(usuario, tarea_a_marcar['vida_restar']) #Resto vida al usuario según la tarea incompleta.
        elif seleccion == 0:
            cancelar = input("¿Deseas cancelar la operación? (s/n): ")
            if cancelar.lower() == 's':
                print(Fore.YELLOW + f"\nOperación cancelada." + Style.RESET_ALL)
                return
        else:
            print(Fore.RED + "⚠️ Tarea no encontrada." + Style.RESET_ALL)
    except ValueError:
        print(Fore.RED + "⚠️ Entrada inválida. Por favor ingresa un número válido." + Style.RESET_ALL)
