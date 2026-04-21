import json
import os
import datetime
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
                # En entorno web, el error se maneja en app.py con flash()
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
    def crear_tarea_web(self, titulo, tipo_tarea, dificultad, dias_semana=None, fecha_str=None, habito=None):
        dias_semana = dias_semana or []
        fecha_str = fecha_str or None
        habito = habito or None

        if tipo_tarea == 1:
            xp_tarea, coin_tarea, life_restar = xp_habito(), coin_habito(), vida_habito()
            dias_semana.append("todos")
        elif tipo_tarea == 2:
            xp_tarea, coin_tarea, life_restar = xp_diaria(), coin_diaria(), vida_diaria()
        elif tipo_tarea == 3:
            xp_tarea, coin_tarea, life_restar = xp_pendiente(), coin_pendiente(), vida_pendiente()
            if not fecha_str:
                fecha_str = "Sin fecha"
        else:
            raise ValueError("Tipo de tarea inválido")

        dificultad_map = {"1": "facil", "2": "intermedia", "3": "dificil"}
        dificultad_tarea = dificultad_map.get(str(dificultad), "facil")

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
        return nueva


    def ver_tareas_web(self):
        # Debug inicial
        print("DEBUG usuario logueado:", self.usuario.id_usuario, self.usuario.usuario)
        print("DEBUG tareas cargadas:", [(t.id, t.titulo, t.id_usuario, t.tipo) for t in self.tareas])
        # Filtrar tareas del usuario actual
        tareas_usuario = [t for t in self.tareas if int(t.id_usuario) == int(self.usuario.id_usuario)]
        print("DEBUG tareas filtradas:", [(t.id, t.titulo) for t in tareas_usuario])

        if not tareas_usuario:
            return {"habitos": [], "diarias": [], "pendientes": []}

        # Ordenar por tipo y fecha de vencimiento
        def clave_orden(x):
            if x.tipo == 3 and x.fecha_vencimiento not in (None, "Sin fecha"):
                try:
                    return (x.tipo, datetime.datetime.strptime(x.fecha_vencimiento, "%d-%m-%Y"))
                except ValueError:
                    return (x.tipo, datetime.datetime.max)
            return (x.tipo, datetime.datetime.max)

        tareas_usuario.sort(key=clave_orden)

        # Normalizar y separar por tipo
        habitos, diarias, pendientes = [], [], []

        for tarea in tareas_usuario:
            fecha = tarea.fecha_vencimiento or "Sin fecha"
            dias = tarea.dias_semana if tarea.dias_semana else ["No aplica"]

            if tarea.tipo == 1:
                habitos.append({
                    "id": tarea.id,
                    "titulo": tarea.titulo,
                    "habito": tarea.habito,
                    "dificultad": tarea.dificultad,
                    "completada": tarea.completada
                })
            elif tarea.tipo == 2:
                diarias.append({
                    "id": tarea.id,
                    "titulo": tarea.titulo,
                    "dias": dias,
                    "dificultad": tarea.dificultad,
                    "completada": tarea.completada
                })
            elif tarea.tipo == 3:
                pendientes.append({
                    "id": tarea.id,
                    "titulo": tarea.titulo,
                    "dias": dias,
                    "fecha_vencimiento": fecha,
                    "dificultad": tarea.dificultad,
                    "completada": tarea.completada
                })

        return {
            "habitos": habitos,
            "diarias": diarias,
            "pendientes": pendientes
        }

    def editar_tarea(self):
        while True:  # bucle para repetir hasta que se edite o se cancele
            # Mostrar primero las tareas del usuario
            self.ver_tareas()
            try:
                seleccion = int(input("\nIngresa el ID de la tarea que deseas editar | 0 (cero) cancelar: "))

                # Filtrar tareas del usuario actual
                tareas_usuario = [t for t in self.tareas if int(t.id_usuario) == int(self.usuario.id_usuario)]

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
                tareas_usuario = [t for t in self.tareas if int(t.id_usuario) == int(self.usuario.id_usuario)]

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
                tareas_usuario = [t for t in self.tareas if int(t.id_usuario) == int(self.usuario.id_usuario)]
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
