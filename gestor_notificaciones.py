import json
import os
from utils_rutas import ruta_json

ARCHIVO_NOTIFICACIONES = ruta_json("notificaciones.json")

class GestorNotificaciones:
    def __init__(self):
        self.notificaciones = self.cargar_notificaciones()

    def cargar_notificaciones(self):
        if not os.path.exists(ARCHIVO_NOTIFICACIONES):
            return []
        with open(ARCHIVO_NOTIFICACIONES, "r", encoding="utf-8") as f:
            contenido = f.read().strip()
            if not contenido:
                return []
            return json.loads(contenido)

    def guardar_notificaciones(self, data):
        with open(ARCHIVO_NOTIFICACIONES, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def agregar_notificacion(self, id_usuario, notificacion):
        data = self.cargar_notificaciones()
        usuario = next((u for u in data if u["id_usuario"] == id_usuario), None)
        if usuario:
            nuevo_id = str(len(usuario["notificaciones"]) + 1)
            usuario["notificaciones"][nuevo_id] = notificacion.to_dict()
        else:
            data.append({
                "id_usuario": id_usuario,
                "notificaciones": {"1": notificacion.to_dict()}
            })
        self.guardar_notificaciones(data)

    def marcar_leida(self, id_usuario, id_notificacion):
        data = self.cargar_notificaciones()
        usuario = next((u for u in data if u["id_usuario"] == id_usuario), None)
        if usuario and id_notificacion in usuario["notificaciones"]:
            usuario["notificaciones"][id_notificacion]["leido"] = True
            self.guardar_notificaciones(data)

    def eliminar_notificacion(self, id_usuario, id_notificacion):
        data = self.cargar_notificaciones()
        usuario = next((u for u in data if u["id_usuario"] == id_usuario), None)
        if usuario and id_notificacion in usuario["notificaciones"]:
            del usuario["notificaciones"][id_notificacion]
            self.guardar_notificaciones(data)

    def obtener_notificaciones(self, id_usuario):
        data = self.cargar_notificaciones()
        usuario = next((u for u in data if u["id_usuario"] == id_usuario), None)
        if usuario:
            # 🔹 Convertir dict {"1": {...}, "2": {...}} en lista de dicts con id incluido
            return [
                {**notif, "id": int(id_notif)}
                for id_notif, notif in usuario["notificaciones"].items()
            ]
        return []
