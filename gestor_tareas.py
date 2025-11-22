import json
import os
import datetime
from colorama import Fore, Style
from constantes_tareas import (
    xp_habito, xp_diaria, xp_pendiente,
    coin_habito, coin_diaria, coin_pendiente,
    vida_habito, vida_diaria, vida_pendiente
)
from tareas import Tarea   # importamos la clase

ARCHIVO_TAREAS = os.path.join("json", "tareas.json")  # más portable

class GestorTareas:
    def __init__(self, usuario=None, gestor_usuarios=None):
        self.usuario = usuario
        self.gestor_usuarios = gestor_usuarios
        self.tareas = self.cargar_tareas() #Se asigna a self.tareas la lista de objetos Tarea que se obtuvo de return [Tarea.from_dict(t) for t in data] | Cabe resaltar que son todas las tareas y no solo la del usuario logueado.

    # -------------------------------
    # Manejo de archivo JSON
    # -------------------------------
    def cargar_tareas(self):
        if os.path.exists(ARCHIVO_TAREAS):
            try:
                with open(ARCHIVO_TAREAS, "r", encoding="utf-8") as archivo:
                    contenido = archivo.read().strip()
                    if not contenido:
                        return []
                    data = json.loads(contenido) #Convierte el texto del JSON en una lista de diccionarios.
                    return [Tarea.from_dict(t) for t in data]  #list comprehension | Recorro cada elemento t dentro de data. | El metodo Tarea.from_dict(t) convierte el diccionario en un objeto Tarea.
            except json.JSONDecodeError:
                print(Fore.RED + "⚠️ El archivo de tareas está corrupto o vacío. Se iniciará una lista nueva." + Style.RESET_ALL)
                return []
        return []

    def guardar_tareas(self):
        with open(ARCHIVO_TAREAS, "w", encoding="utf-8") as archivo:
            json.dump([t.to_dict() for t in self.tareas], archivo, indent=4, ensure_ascii=False) #convierte cada objeto Tarea en diccionario to_dict(), porque self.tareas tiene todas las tareas.
        self.tareas = self.cargar_tareas()

    def tareas_usuario(self):
        return [t for t in self.tareas if t.id_usuario == self.usuario.id_usuario]

    def eliminar_tareas_de_usuario(self, id_usuario):
        self.tareas = [t for t in self.tareas if t.id_usuario != id_usuario]
        self.guardar_tareas()

    # -------------------------------
    # Métodos principales
    # -------------------------------
    def nueva_tarea(self):
        while True:  # bucle para repetir hasta que se cree o se cancele
            titulo = input("Ingresa el título de la nueva tarea | 0 (cero) cancelar: ")

            if titulo == "0":
                cancelar = input("¿Deseas cancelar la operación? (s/n): ")
                if cancelar.lower() == 's':
                    print(Fore.YELLOW + "\nOperación cancelada." + Style.RESET_ALL)
                    return
                else:
                    print(Fore.YELLOW + "\nVolviendo al menú de creación. Ingresa nuevamente el título." + Style.RESET_ALL)
                    continue

            if not titulo.strip():
                print(Fore.RED + "⚠️ El título de la tarea no puede estar vacío. La tarea no se creará." + Style.RESET_ALL)
                continue

            try:
                tipo_tarea = int(input("Ingresa el tipo de tarea. Hábito(1), Diaria(2), Pendiente(3): "))
            except ValueError:
                print(Fore.RED + "⚠️ Tipo de tarea inválido." + Style.RESET_ALL)
                continue

            dias_semana, fecha_vencimiento, fecha_str, habito = [], None, None, None

            if tipo_tarea == 1:
                tipo_habito = input("¿Es un hábito positivo o negativo? (+/-): ")
                if tipo_habito not in ["+", "-"]:
                    print(Fore.RED + "⚠️ Opción no válida. La tarea no se creará." + Style.RESET_ALL)
                    continue
                habito = tipo_habito
                dias_semana.append("todos")
                xp_tarea, coin_tarea, life_restar = xp_habito(), coin_habito(), vida_habito() #Estas son las funciones que están en constantes_tareas.py

            elif tipo_tarea == 2:
                xp_tarea, coin_tarea, life_restar = xp_diaria(), coin_diaria(), vida_diaria() #Estas son las funciones que están en constantes_tareas.py
                while True:
                    dias_seleccionado = input("Selecciona días (1=Lunes ... 7=Domingo, 0=Listo): ")
                    mapa = {"1":"Lunes","2":"Martes","3":"Miercoles","4":"Jueves","5":"Viernes","6":"Sabado","7":"Domingo"}
                    if dias_seleccionado in mapa:
                        dia = mapa[dias_seleccionado]
                        if dia not in dias_semana:
                            dias_semana.append(mapa[dias_seleccionado]) #Acumula en una lista todos los elegidos hasta que el usuario ponga 0.
                        else:
                            print(Fore.YELLOW + f"⚠️ El día {dia} ya fue seleccionado." + Style.RESET_ALL)
                    elif dias_seleccionado == "0":
                        break
                    else:
                        print(Fore.RED + "⚠️ Día no válido." + Style.RESET_ALL)

            elif tipo_tarea == 3:
                xp_tarea, coin_tarea, life_restar = xp_pendiente(), coin_pendiente(), vida_pendiente() #Estas son las funciones que están en constantes_tareas.py
                poner_fecha = input("¿Deseas poner una fecha de vencimiento? (s/n): ").lower()
                if poner_fecha == "s":
                    fecha_vencimiento = input("Ingresa la fecha (DD-MM-AAAA): ")
                    try:
                        fecha_vencimiento = datetime.datetime.strptime(fecha_vencimiento, "%d-%m-%Y").date()
                        fecha_str = fecha_vencimiento.strftime("%d-%m-%Y")
                    except ValueError:
                        print(Fore.RED + "⚠️ Formato inválido. La tarea no se creará." + Style.RESET_ALL)
                        continue
                elif poner_fecha == "n":
                    fecha_vencimiento = None
                else:
                    print(Fore.RED + "⚠️ Opción no válida." + Style.RESET_ALL)
                    continue
            else:
                print(Fore.RED + "⚠️ Tipo de tarea no válido." + Style.RESET_ALL)
                continue
            
            #Consultando dificultad de la tarea
            dificultad = int(input("Seleccione la dificultad de la tarea (1)Facil, (2)Intermedia, (3)Dificil: "))
            dificultad_tarea = None
            
            try:
                if dificultad == 1:
                    dificultad_tarea = "facil"
                elif dificultad == 2:
                    dificultad_tarea = "intermedia"
                elif dificultad == 3:
                    dificultad_tarea = "dificil"
                else:
                    print(Fore.RED + "⚠️ Opción no válida." + Style.RESET_ALL)
                    continue
            except:
                print(Fore.RED + "⚠️ Tipo de dificultad no válido." + Style.RESET_ALL)
                continue
            
            # Crear tarea como objeto
            ultimo_id = max([t.id for t in self.tareas], default=0) #Crea una lista con todos los ID de esas tareas y devuelve el mayor con max.
            nueva = Tarea( #Se instancia el objeto Tarea con todos sus atributos
                id=ultimo_id + 1,
                titulo=titulo,
                tipo=tipo_tarea,
                id_usuario=self.usuario.id_usuario,
                dias_semana=dias_semana,
                fecha_vencimiento=fecha_str,
                xp_reward=xp_tarea,
                coin_reward=coin_tarea,
                vida_restar=life_restar,
                habito=habito,
                completada=False,
                dificultad=dificultad_tarea
            )

            self.tareas.append(nueva) #En este momento self.tareas contiene todas las tareas anteriores más la nueva.
            self.guardar_tareas()
            print(Fore.YELLOW + f"Tarea '{titulo}' agregada exitosamente." + Style.RESET_ALL)
            return

    def ver_tareas(self):
        # Filtrar tareas del usuario actual
        tareas_usuario = [t for t in self.tareas if t.id_usuario == self.usuario.id_usuario] #Genera una lista con las tareas del usuario logueado.

        if not tareas_usuario:
            print("\nNo hay tareas disponibles.")
            return

        print("\nLista de Tareas:")

        # Ordenar por tipo y fecha de vencimiento (si aplica)
        tareas_usuario.sort(
            key=lambda x: ( #Define la "Clave de ordenamiento" para cada tarea x | En ésta parte también abre un () para indicar que todo lo que se ordene aquí adentro sea una Tupla.
                x.tipo, #Primer criterio de ordenamiento, es un atributo del objeto Tarea (si es tipo 1, 2 o 3)
                datetime.datetime.strptime(x.fecha_vencimiento, "%d-%m-%Y") #Segundo criterio, pero solo se aplica si x.tipo == 3
                if x.tipo == 3 and x.fecha_vencimiento not in (None, "Sin fecha") else datetime.datetime.max #si no se cumple usa datetime.datetime.max que devuelve una fecha 9999 para que las que no tienen fecha se pongan al final.
            )
        ) #Devolvería para la primer tarea = (1, datetime.max) y para la segunda tarea = (3, datetime.datetime(2025,11,20))

        for contador, tarea in enumerate(tareas_usuario, start=1):
            estado = Fore.GREEN + "Completada" + Style.RESET_ALL if tarea.completada else Fore.RED + "Incompleta" + Style.RESET_ALL

            # Normalizar valores para mostrar
            if tarea.fecha_vencimiento is None:
                tarea.fecha_vencimiento = "Sin fecha"
            if not tarea.dias_semana:
                tarea.dias_semana = ["No aplica"]

            tipos = {1: "Hábito", 2: "Tarea Diaria", 3: "Tarea Pendiente"}
            tipo_nombre = tipos.get(tarea.tipo, "Desconocido")

            if tarea.tipo == 1:
                signo = "Positivo" if tarea.habito == "+" else "Negativo"
                print(f"{contador}. {tarea.titulo} | {tipo_nombre} | {signo}")
            elif tarea.tipo == 2:
                print(f"{contador}. {tarea.titulo} - {estado} | {tipo_nombre} | Días: {', '.join(tarea.dias_semana)}")
            else:  # tipo 3
                print(f"{contador}. {tarea.titulo} - {estado} | {tipo_nombre} | Días: {', '.join(tarea.dias_semana)} | Vencimiento: {tarea.fecha_vencimiento}")

    def editar_tarea(self):
        while True:  # bucle para repetir hasta que se edite o se cancele
            # Mostrar primero las tareas del usuario
            self.ver_tareas()
            try:
                seleccion = int(input("\nIngresa el ID de la tarea que deseas editar | 0 (cero) cancelar: "))

                # Filtrar tareas del usuario actual
                tareas_usuario = [t for t in self.tareas if t.id_usuario == self.usuario.id_usuario]

                # Ordenar igual que en ver_tareas()
                tareas_usuario.sort(
                    key=lambda x: (
                        x.tipo,
                        datetime.datetime.strptime(x.fecha_vencimiento, "%d-%m-%Y")
                        if x.tipo == 3 and x.fecha_vencimiento not in (None, "Sin fecha") else datetime.datetime.max
                    )
                )

                if 1 <= seleccion <= len(tareas_usuario):
                    tarea_a_editar = tareas_usuario[seleccion - 1]
                    nuevo_titulo = input(f"Ingresa el nuevo título para la tarea '{tarea_a_editar.titulo}': ")
                    tarea_a_editar.editar_titulo(nuevo_titulo)   # 👈 usamos el método de la clase
                    self.guardar_tareas()
                    print(f"\nTarea '{tarea_a_editar.titulo}'" + Fore.YELLOW + " actualizada exitosamente." + Style.RESET_ALL)
                    return  # salir del bucle después de editar

                elif seleccion == 0:
                    cancelar = input("¿Deseas cancelar la operación? (s/n): ")
                    if cancelar.lower() == 's':
                        print(Fore.YELLOW + "\nOperación cancelada." + Style.RESET_ALL)
                        return  # salir del método
                    else:
                        print(Fore.YELLOW + "\nVolviendo al menú de edición. Ingresa nuevamente el ID." + Style.RESET_ALL)
                        continue  # vuelve al inicio del bucle

                else:
                    print(Fore.RED + "⚠️ Tarea no encontrada." + Style.RESET_ALL)
                    continue  # vuelve a pedir ID

            except ValueError:
                print(Fore.RED + "⚠️ Entrada inválida. Por favor ingresa un número válido." + Style.RESET_ALL)
                continue

    def eliminar_tarea(self):
        while True:  # bucle para repetir hasta que se elimine o se cancele
            # Mostrar primero las tareas del usuario
            self.ver_tareas()
            try:
                seleccion = int(input("\nIngresa el ID de la tarea que deseas eliminar | 0 (cero) cancelar: "))

                # Filtrar tareas del usuario actual
                tareas_usuario = [t for t in self.tareas if t.id_usuario == self.usuario.id_usuario]

                # Ordenar igual que en ver_tareas()
                tareas_usuario.sort(
                    key=lambda x: (
                        x.tipo,
                        datetime.datetime.strptime(x.fecha_vencimiento, "%d-%m-%Y")
                        if x.tipo == 3 and x.fecha_vencimiento not in (None, "Sin fecha") else datetime.datetime.max
                    )
                )

                if 1 <= seleccion <= len(tareas_usuario):
                    tarea_a_eliminar = tareas_usuario[seleccion - 1]
                    self.tareas.remove(tarea_a_eliminar)
                    self.guardar_tareas()
                    print(f"Tarea '{tarea_a_eliminar.titulo}'" + Fore.RED + " eliminada exitosamente." + Style.RESET_ALL)
                    return  # salir del bucle después de eliminar

                elif seleccion == 0:
                    cancelar = input("¿Deseas cancelar la operación? (s/n): ")
                    if cancelar.lower() == 's':
                        print(Fore.YELLOW + "\nOperación cancelada." + Style.RESET_ALL)
                        return  # salir del bucle y terminar
                    else:
                        # simplemente vuelve al inicio del bucle y pide de nuevo el ID
                        print(Fore.YELLOW + "\nVolviendo al menú de eliminación. Ingresa nuevamente el ID." + Style.RESET_ALL)
                        continue

                else:
                    print(Fore.RED + "⚠️ Tarea no encontrada." + Style.RESET_ALL)

            except ValueError:
                print(Fore.RED + "⚠️ Entrada inválida. Por favor ingresa un número válido." + Style.RESET_ALL)

    def marcar_tarea(self):
        while True:  # bucle para repetir hasta que se marque o se cancele
            # Mostrar primero las tareas del usuario
            self.ver_tareas()
            try:
                seleccion = int(input("\nIngresa el ID de la tarea que deseas marcar como completada | 0 (cero) cancelar: "))

                # Filtrar tareas del usuario actual
                tareas_usuario = [t for t in self.tareas if t.id_usuario == self.usuario.id_usuario]

                # Ordenar igual que en ver_tareas()
                tareas_usuario.sort(
                    key=lambda x: (
                        x.tipo,
                        datetime.datetime.strptime(x.fecha_vencimiento, "%d-%m-%Y")
                        if x.tipo == 3 and x.fecha_vencimiento not in (None, "Sin fecha") else datetime.datetime.max
                    )
                )

                tarea_a_marcar = None
                if 1 <= seleccion <= len(tareas_usuario):
                    tarea_a_marcar = tareas_usuario[seleccion - 1]

                if seleccion == 0:
                    cancelar = input("¿Deseas cancelar la operación? (s/n): ")
                    if cancelar.lower() == 's':
                        print(Fore.YELLOW + "\nOperación cancelada." + Style.RESET_ALL)
                        return  # salir del método
                    else:
                        print(Fore.YELLOW + "\nVolviendo al menú de marcado. Ingresa nuevamente el ID." + Style.RESET_ALL)
                        continue  # vuelve al inicio del bucle

                if not tarea_a_marcar:
                    print(Fore.RED + "⚠️ Tarea no encontrada." + Style.RESET_ALL)
                    continue  # vuelve a pedir ID

                # --- Hábito ---
                if tarea_a_marcar.tipo == 1:
                    opcion = tarea_a_marcar.habito
                    if opcion == "+":
                        self.usuario.sumar_xp_coins(tarea_a_marcar.xp_reward, tarea_a_marcar.coin_reward)
                        self.gestor_usuarios.actualizar_usuario(self.usuario)
                        print(Fore.GREEN + "\n¡Hábito positivo registrado!" + Style.RESET_ALL)
                    elif opcion == "-":
                        self.usuario.restar_vida(tarea_a_marcar.vida_restar)
                        self.gestor_usuarios.actualizar_usuario(self.usuario)
                        print(Fore.RED + "\nHábito negativo registrado." + Style.RESET_ALL)
                    else:
                        print(Fore.RED + "⚠️ Opción no válida." + Style.RESET_ALL)
                    return

                # --- Pendiente ---
                if tarea_a_marcar.tipo == 3:
                    if not tarea_a_marcar.completada:
                        tarea_a_marcar.completada = True
                        self.guardar_tareas()
                        print(f"\nTarea {tarea_a_marcar.titulo} marcada como " + Fore.GREEN + "completada." + Style.RESET_ALL)
                        self.usuario.sumar_xp_coins(tarea_a_marcar.xp_reward, tarea_a_marcar.coin_reward)
                        self.gestor_usuarios.actualizar_usuario(self.usuario)
                    else:
                        print(f"\nLa tarea {tarea_a_marcar.titulo} ya está marcada como completada. Seleccione otra.")
                    return

                # --- Diaria ---
                if tarea_a_marcar.tipo == 2:
                    if not tarea_a_marcar.completada:
                        tarea_a_marcar.completada = True
                        self.guardar_tareas()
                        print(f"\nTarea {tarea_a_marcar.titulo} marcada como " + Fore.GREEN + "completada." + Style.RESET_ALL)
                        self.usuario.sumar_xp_coins(tarea_a_marcar.xp_reward, tarea_a_marcar.coin_reward)
                        self.gestor_usuarios.actualizar_usuario(self.usuario)
                    else:
                        tarea_a_marcar.completada = False
                        self.guardar_tareas()
                        print(f"\nTarea {tarea_a_marcar.titulo} marcada como " + Fore.RED + "incompleta." + Style.RESET_ALL)
                        self.usuario.restar_vida(tarea_a_marcar.vida_restar)
                        self.gestor_usuarios.actualizar_usuario(self.usuario)
                    return

            except ValueError:
                print(Fore.RED + "⚠️ Entrada inválida. Por favor ingresa un número válido." + Style.RESET_ALL)
                continue
