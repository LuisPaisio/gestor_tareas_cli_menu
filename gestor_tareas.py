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
from flask import session

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

    def actualizar_tarea(self, tarea):
        for i, t in enumerate(self.tareas):
            if t.id == tarea.id:
                self.tareas[i] = tarea
                break
        self.guardar_tareas()

    # -------------------------------
    # Métodos principales
    # -------------------------------
    def crear_tarea_web(self, titulo, tipo_tarea, dificultad, dias_semana=None, fecha_str=None, habito=None):
        dias_semana = dias_semana or []
        fecha_str = fecha_str or None
        
        dificultad_map = {"1": "facil", "2": "intermedia", "3": "dificil"}
        dificultad_tarea = dificultad_map.get(str(dificultad), "facil")

        if tipo_tarea == 1:
            xp_tarea, coin_tarea = xp_habito(), coin_habito()
            life_restar = vida_habito(self.usuario, dificultad_tarea)
            dias_semana.append("todos")
            if habito not in ["+", "-", "+-"]:
                habito = "+-"

        elif tipo_tarea == 2:
            xp_tarea, coin_tarea = xp_diaria(), coin_diaria()
            life_restar = vida_diaria(self.usuario, dificultad_tarea)

        elif tipo_tarea == 3:
            xp_tarea, coin_tarea = xp_pendiente(), coin_pendiente()
            life_restar = vida_pendiente(self.usuario, dificultad_tarea)

            # 🔹 Validar fecha de vencimiento
            if fecha_str:
                try:
                    fecha_obj = datetime.datetime.strptime(fecha_str, "%Y-%m-%d").date()
                    if fecha_obj < datetime.date.today():
                        # Ajustar a hoy si es menor
                        fecha_str = datetime.date.today().strftime("%Y-%m-%d")
                except ValueError:
                    fecha_str = "Sin fecha"
            else:
                fecha_str = "Sin fecha"

        else:
            raise ValueError("Tipo de tarea inválido")

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
        # Filtrar tareas del usuario actual (objetos Tarea)
        tareas_usuario = [t for t in self.tareas if int(t.id_usuario) == int(self.usuario.id_usuario)]

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

        # Normalizar y separar por tipo (solo para renderizado)
        habitos, diarias, pendientes = [], [], []

        for tarea in tareas_usuario:
            fecha = tarea.fecha_vencimiento or "Sin fecha"
            dias = tarea.dias_semana if tarea.dias_semana else ["No aplica"]

            if tarea.tipo == 1:
                habitos.append({
                    "id": tarea.id,
                    "titulo": tarea.titulo,
                    "tipo": tarea.tipo,
                    "habito": tarea.habito,
                    "dificultad": tarea.dificultad,
                    "completada": tarea.completada
                })
            elif tarea.tipo == 2:
                diarias.append({
                    "id": tarea.id,
                    "titulo": tarea.titulo,
                    "tipo": tarea.tipo,
                    "dias": dias,
                    "dificultad": tarea.dificultad,
                    "completada": tarea.completada
                })
            elif tarea.tipo == 3:
                pendientes.append({
                    "id": tarea.id,
                    "titulo": tarea.titulo,
                    "tipo": tarea.tipo,
                    "dias": dias,
                    "fecha_vencimiento": fecha,
                    "dificultad": tarea.dificultad,
                    "completada": tarea.completada
                })

        # Devolver solo los dicts para el template
        return {
            "habitos": habitos,
            "diarias": diarias,
            "pendientes": pendientes
        }

    def editar_tarea(self, tarea_id, nuevo_titulo=None, nueva_fecha=None, nuevos_dias=None, nuevo_habito=None):
        for t in self.tareas:
            if int(t.id) == int(tarea_id) and int(t.id_usuario) == int(self.usuario.id_usuario):
                if nuevo_titulo:
                    t.editar_titulo(nuevo_titulo)

                if nuevo_habito:
                    t.habito = nuevo_habito

                if nuevos_dias:
                    t.dias_semana = nuevos_dias

                if nueva_fecha:
                    try:
                        fecha_obj = datetime.datetime.strptime(nueva_fecha, "%Y-%m-%d").date()
                        # Validar que no sea menor a hoy
                        if fecha_obj < datetime.date.today():
                            # Podés decidir: rechazar o ajustar a hoy
                            return False   # rechaza la edición
                            # o bien:
                            # fecha_obj = datetime.date.today()
                        t.fecha_vencimiento = fecha_obj.strftime("%Y-%m-%d")
                    except ValueError:
                        # Si la fecha no es válida, no actualizar
                        return False

                self.actualizar_tarea(t)
                return True
        return False


    def eliminar_tarea(self, tarea_id):
        self.tareas = [
            t for t in self.tareas
            if not (int(t.id) == int(tarea_id) and int(t.id_usuario) == int(self.usuario.id_usuario))
        ]
        self.guardar_tareas()
        return True

    def verificar_diarias_web(self):
        hoy = datetime.date.today().strftime("%d-%m-%Y")
        dia_actual = datetime.date.today().strftime("%A").lower()  # ejemplo: "tuesday"

        # mapear nombres a español si tus tareas usan "lunes", "martes", etc.
        mapa_dias = {
            "monday": "lunes",
            "tuesday": "martes",
            "wednesday": "miercoles",
            "thursday": "jueves",
            "friday": "viernes",
            "saturday": "sabado",
            "sunday": "domingo"
        }

        diarias_vencidas = []
        pendientes_vencidas = []

        for tarea in self.tareas:
            if int(tarea.id_usuario) != int(self.usuario.id_usuario):
                continue

            if tarea.tipo == 2:  # Diaria
                # 🔹 Solo detectar si está vencida y corresponde al día actual
                if tarea.fecha_creacion != hoy and not tarea.completada:
                    if "todos" in tarea.dias_semana or mapa_dias[dia_actual] in tarea.dias_semana:
                        diarias_vencidas.append(tarea)

            elif tarea.tipo == 3 and tarea.es_vencida() and not tarea.completada:
                pendientes_vencidas.append(tarea)

        # 🔹 Flag en sesión: mostrar modal solo si no se procesó hoy
        ultimo_procesado = session.get("ultimo_procesado")
        if ultimo_procesado == hoy:
            session["mostrar_modal"] = False
        else:
            session["mostrar_modal"] = True

        return {
            "diarias_vencidas": diarias_vencidas,
            "pendientes_vencidas": pendientes_vencidas
        }

    def marcar_tarea_web(self, tarea_id, accion, retroactivo=False, por_medianoche=False):
        tarea = next(
            (t for t in self.tareas if int(t.id) == int(tarea_id) and int(t.id_usuario) == int(self.usuario.id_usuario)),
            None
        )
        if not tarea:
            return {"error": "Tarea no encontrada"}

        recompensas, penalizaciones, mensaje = [], [], ""
        murio = False  # 👈 flag de muerte

        # --- Hábito ---
        if tarea.tipo == 1:
            if accion == "positivo" and tarea.habito in ["+", "+-"]:
                recompensas, error_msg = tarea.completar(self.usuario, retroactivo=retroactivo)
                if error_msg:
                    return {"error": error_msg}
                recompensas, murio = self.gestor_recompensas.aplicar_recompensas(
                    self.usuario, recompensas, es_penalizacion=False
                )
                mensaje = f"Hábito positivo '{tarea.titulo}' completado."
            elif accion == "negativo" and tarea.habito in ["-", "+-"]:
                penalizaciones, error_msg = tarea.fallar(self.usuario)
                if error_msg:
                    return {"error": error_msg}
                penalizaciones, murio = self.gestor_recompensas.aplicar_recompensas(
                    self.usuario, penalizaciones, es_penalizacion=True
                )
                for p in penalizaciones:
                    if p["tipo"] == "vida":
                        base = p["resultado"]["base"]
                        bonus = p["resultado"]["bonus"]
                        total = p["resultado"]["total"]
                        if total == 0:
                            mensaje = f"Hábito negativo '{tarea.titulo}': DEFENSA absorbió todo el daño (bloqueado {abs(base)} HP)."
                        else:
                            mensaje = f"Hábito negativo '{tarea.titulo}': pierdes {abs(total)} HP (daño base {abs(base)} - defensa {bonus})."
                    else:
                        mensaje = f"Hábito negativo '{tarea.titulo}':"
            else:
                return {"error": "Acción inválida para este hábito"}

        # --- Diaria ---
        elif tarea.tipo == 2:
            if accion == "completar" and not tarea.completada:
                recompensas, error_msg = tarea.completar(self.usuario, retroactivo=retroactivo)
                if error_msg:
                    return {"error": error_msg}
                recompensas, murio = self.gestor_recompensas.aplicar_recompensas(
                    self.usuario, recompensas, es_penalizacion=False
                )
                mensaje = f"Diaria '{tarea.titulo}' completada."
            elif accion == "incompleta":
                penalizaciones, error_msg = tarea.fallar(self.usuario, por_medianoche=por_medianoche)
                if error_msg:
                    return {"error": error_msg}
                penalizaciones, murio = self.gestor_recompensas.aplicar_recompensas(
                    self.usuario, penalizaciones, es_penalizacion=True
                )
                tarea.marcar_incompleta()
                for p in penalizaciones:
                    if p["tipo"] == "vida":
                        base = p["resultado"]["base"]
                        bonus = p["resultado"]["bonus"]
                        total = p["resultado"]["total"]
                        if total == 0:
                            mensaje = f"Diaria '{tarea.titulo}' incompleta: DEFENSA absorbió todo el daño (bloqueado {abs(base)} HP)."
                        else:
                            mensaje = f"Diaria '{tarea.titulo}' incompleta: pierdes {abs(total)} HP (daño base {abs(base)} - defensa {bonus})."
                    else:
                        mensaje = f"Diaria '{tarea.titulo}' incompleta:"

        # --- Pendiente ---
        elif tarea.tipo == 3:
            if accion == "completar" and not tarea.completada:
                recompensas, error_msg = tarea.completar(self.usuario, retroactivo=retroactivo)
                if error_msg:
                    return {"error": error_msg}
                recompensas, murio = self.gestor_recompensas.aplicar_recompensas(
                    self.usuario, recompensas, es_penalizacion=False
                )
                mensaje = f"Pendiente '{tarea.titulo}' completada."
            elif accion == "incompleta":
                penalizaciones, error_msg = tarea.fallar(self.usuario)
                if error_msg:
                    return {"error": error_msg}
                penalizaciones, murio = self.gestor_recompensas.aplicar_recompensas(
                    self.usuario, penalizaciones, es_penalizacion=True
                )
                tarea.marcar_incompleta()
                # ajuste de fecha vencida
                if tarea.fecha_vencimiento and tarea.fecha_vencimiento != "Sin fecha":
                    try:
                        fecha = datetime.datetime.strptime(tarea.fecha_vencimiento, "%d-%m-%Y").date()
                    except ValueError:
                        try:
                            fecha = datetime.datetime.strptime(tarea.fecha_vencimiento, "%Y-%m-%d").date()
                        except ValueError:
                            fecha = None
                    if fecha and fecha < datetime.date.today():
                        tarea.fecha_vencimiento = datetime.date.today().strftime("%Y-%m-%d")

                for p in penalizaciones:
                    if p["tipo"] == "vida":
                        base = p["resultado"]["base"]
                        bonus = p["resultado"]["bonus"]
                        total = p["resultado"]["total"]
                        if total == 0:
                            mensaje = f"Pendiente '{tarea.titulo}' incompleta: DEFENSA absorbió todo el daño (bloqueado {abs(base)} HP)."
                        else:
                            mensaje = f"Pendiente '{tarea.titulo}' incompleta: pierdes {abs(total)} HP (daño base {abs(base)} - defensa {bonus})."
                    else:
                        mensaje = f"Pendiente '{tarea.titulo}' incompleta:"

        # Guardar cambios y subir nivel
        eventos = self.usuario.subir_nivel()
        self.guardar_tareas()
        self.gestor_usuarios.actualizar_usuario(self.usuario)

        # 👇 si murió, setear flag en sesión
        if murio:
            from flask import session
            session["mostrar_modal_muerte"] = True

        return {
            "mensaje": mensaje,
            "recompensas": recompensas,
            "penalizaciones": penalizaciones,
            "eventos": eventos
        }

