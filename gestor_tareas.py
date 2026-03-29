import json
import os
import datetime
from colorama import Fore, Style
from constantes_tareas import (
    xp_habito, xp_diaria, xp_pendiente,
    coin_habito, coin_diaria, coin_pendiente,
    vida_habito, vida_diaria, vida_pendiente
)
from tareas import Tarea
from gestor_recompensa import GestorRecompensas
from utils_rutas import ruta_json

ARCHIVO_TAREAS = ruta_json("tareas.json")

class GestorTareas:
    def __init__(self, usuario=None, gestor_usuarios=None):
        self.usuario = usuario
        self.gestor_usuarios = gestor_usuarios
        self.tareas = self.cargar_tareas()
        self.gestor_recompensas = GestorRecompensas()

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
                    data = json.loads(contenido)
                    return [Tarea.from_dict(t) for t in data]
            except json.JSONDecodeError:
                print(Fore.RED + "⚠️ El archivo de tareas está corrupto o vacío. Se iniciará una lista nueva." + Style.RESET_ALL)
                return []
        return []

    def guardar_tareas(self):
        with open(ARCHIVO_TAREAS, "w", encoding="utf-8") as archivo:
            json.dump([t.to_dict() for t in self.tareas], archivo, indent=4, ensure_ascii=False)
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
        while True:
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

            dias_semana, fecha_str, habito = [], None, None

            if tipo_tarea == 1:
                tipo_habito = input("¿Es un hábito positivo o negativo? (+/-): ")
                if tipo_habito not in ["+", "-"]:
                    print(Fore.RED + "⚠️ Opción no válida. La tarea no se creará." + Style.RESET_ALL)
                    continue
                habito = tipo_habito
                dias_semana.append("todos")
                xp_tarea, coin_tarea, life_restar = xp_habito(), coin_habito(), vida_habito()

            elif tipo_tarea == 2:
                xp_tarea, coin_tarea, life_restar = xp_diaria(), coin_diaria(), vida_diaria()
                while True:
                    dias_seleccionado = input("Selecciona días (1=Lunes ... 7=Domingo, 0=Listo): ")
                    mapa = {"1":"lunes","2":"martes","3":"miercoles","4":"jueves","5":"viernes","6":"sabado","7":"domingo"}
                    if dias_seleccionado in mapa:
                        dia = mapa[dias_seleccionado]
                        if dia not in dias_semana:
                            dias_semana.append(dia)
                        else:
                            print(Fore.YELLOW + f"⚠️ El día {dia} ya fue seleccionado." + Style.RESET_ALL)
                    elif dias_seleccionado == "0":
                        break
                    else:
                        print(Fore.RED + "⚠️ Día no válido." + Style.RESET_ALL)

            elif tipo_tarea == 3:
                xp_tarea, coin_tarea, life_restar = xp_pendiente(), coin_pendiente(), vida_pendiente()
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
                    fecha_str = "Sin fecha"
                else:
                    print(Fore.RED + "⚠️ Opción no válida." + Style.RESET_ALL)
                    continue
            else:
                print(Fore.RED + "⚠️ Tipo de tarea no válido." + Style.RESET_ALL)
                continue

            # Consultando dificultad de la tarea
            try:
                dificultad = int(input("Seleccione la dificultad de la tarea (1)Facil, (2)Intermedia, (3)Dificil: "))
            except ValueError:
                print(Fore.RED + "⚠️ Tipo de dificultad no válido." + Style.RESET_ALL)
                continue

            if dificultad == 1:
                dificultad_tarea = "facil"
            elif dificultad == 2:
                dificultad_tarea = "intermedia"
            elif dificultad == 3:
                dificultad_tarea = "dificil"
            else:
                print(Fore.RED + "⚠️ Opción no válida." + Style.RESET_ALL)
                continue

            # Crear tarea como objeto
            ultimo_id = max([t.id for t in self.tareas], default=0)
            nueva = Tarea(
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

            self.tareas.append(nueva)
            self.guardar_tareas()
            print(Fore.YELLOW + f"\nTarea '{titulo}' agregada exitosamente con dificultad {dificultad_tarea}." + Style.RESET_ALL)
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

    def verificar_diarias(self):
        hoy = datetime.date.today().strftime("%d-%m-%Y")

        for tarea in self.tareas:
            if tarea.tipo == 2:  # Diaria
                if tarea.fecha_creacion != hoy:
                    if not tarea.completada:
                        print(Fore.YELLOW + f"\nLa diaria '{tarea.titulo}' no fue completada ayer." + Style.RESET_ALL)
                        opcion = input("¿Querés marcarla como completada retroactivamente? (s/n): ")

                        if opcion.lower() == "s":
                            recompensas = tarea.completar(retroactivo=True)
                            self.gestor_recompensas.aplicar_recompensas(self.usuario, recompensas, es_penalizacion=False)
                            self.usuario.subir_nivel()
                            print(Fore.YELLOW + f"'{tarea.titulo}' marcada como completada retroactivamente." + Style.RESET_ALL)
                        else:
                            penalizaciones = tarea.fallar(por_medianoche=True)
                            self.gestor_recompensas.aplicar_recompensas(self.usuario, penalizaciones, es_penalizacion=True)
                            self.usuario.subir_nivel()
                            print(Fore.RED + f"Diaria '{tarea.titulo}' marcada como fallida." + Style.RESET_ALL)

                    tarea.completada = False
                    tarea.fecha_creacion = hoy

        self.guardar_tareas()
        self.gestor_usuarios.actualizar_usuario(self.usuario)

    def marcar_tarea(self):
        while True:
            self.ver_tareas()
            try:
                seleccion = int(input("\nIngresa el ID de la tarea que deseas marcar como completada | 0 cancelar: "))
                tareas_usuario = [t for t in self.tareas if t.id_usuario == self.usuario.id_usuario]
                tareas_usuario.sort(key=lambda x: (
                    x.tipo,
                    datetime.datetime.strptime(x.fecha_vencimiento, "%d-%m-%Y")
                    if x.tipo == 3 and x.fecha_vencimiento not in (None, "Sin fecha") else datetime.datetime.max
                ))

                if seleccion == 0:
                    cancelar = input("¿Deseas cancelar la operación? (s/n): ")
                    if cancelar.lower() == 's':
                        print(Fore.YELLOW + "\nOperación cancelada." + Style.RESET_ALL)
                        return
                    else:
                        continue

                if not (1 <= seleccion <= len(tareas_usuario)):
                    print(Fore.RED + "⚠️ Tarea no encontrada." + Style.RESET_ALL)
                    continue

                tarea_a_marcar = tareas_usuario[seleccion - 1]

                # --- Hábito ---
                if tarea_a_marcar.tipo == 1:
                    if tarea_a_marcar.habito == "+":
                        recompensas = tarea_a_marcar.completar()
                        self.gestor_recompensas.aplicar_recompensas(self.usuario, recompensas, es_penalizacion=False)
                        self.usuario.subir_nivel()
                        print(Fore.YELLOW + f"Hábito '{tarea_a_marcar.titulo}' completado." + Style.RESET_ALL)
                    elif tarea_a_marcar.habito == "-":
                        penalizaciones = tarea_a_marcar.fallar()
                        self.gestor_recompensas.aplicar_recompensas(self.usuario, penalizaciones, es_penalizacion=True)
                        self.usuario.subir_nivel()
                        print(Fore.RED + f"Hábito negativo '{tarea_a_marcar.titulo}' registrado." + Style.RESET_ALL)

                # --- Pendiente ---
                elif tarea_a_marcar.tipo == 3:
                    if not tarea_a_marcar.completada:
                        recompensas = tarea_a_marcar.completar()
                        self.gestor_recompensas.aplicar_recompensas(self.usuario, recompensas, es_penalizacion=False)
                        self.usuario.subir_nivel()
                        print(Fore.YELLOW + f"Pendiente '{tarea_a_marcar.titulo}' completada." + Style.RESET_ALL)
                    else:
                        print(Fore.YELLOW + f"La tarea '{tarea_a_marcar.titulo}' ya está completada." + Style.RESET_ALL)

                # --- Diaria ---
                elif tarea_a_marcar.tipo == 2:
                    if not tarea_a_marcar.completada:
                        recompensas = tarea_a_marcar.completar()
                        self.gestor_recompensas.aplicar_recompensas(self.usuario, recompensas, es_penalizacion=False)
                        self.usuario.subir_nivel()
                        print(Fore.YELLOW + f"Diaria '{tarea_a_marcar.titulo}' completada." + Style.RESET_ALL)
                    else:
                        penalizaciones = tarea_a_marcar.fallar(por_medianoche=False)
                        self.gestor_recompensas.aplicar_recompensas(self.usuario, penalizaciones, es_penalizacion=True)
                        self.usuario.subir_nivel()
                        tarea_a_marcar.marcar_incompleta()
                        print(Fore.RED + f"Diaria '{tarea_a_marcar.titulo}' marcada como incompleta." + Style.RESET_ALL)

                self.guardar_tareas()
                self.gestor_usuarios.actualizar_usuario(self.usuario)
                return

            except ValueError:
                print(Fore.RED + "⚠️ Entrada inválida. Por favor ingresa un número válido." + Style.RESET_ALL)
                continue
