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
            if usuario["notificaciones"]:
                nuevo_id = str(max(int(k) for k in usuario["notificaciones"].keys()) + 1)
            else:
                nuevo_id = "1"
            notif_dict = notificacion.to_dict()
            notif_dict["id"] = int(nuevo_id)
            usuario["notificaciones"][nuevo_id] = notif_dict
        else:
            notif_dict = notificacion.to_dict()
            notif_dict["id"] = 1
            data.append({
                "id_usuario": id_usuario,
                "notificaciones": {"1": notif_dict}
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
