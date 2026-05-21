import os
import json
from mascotas import Mascota
from utils_rutas import ruta_json

ARCHIVO_CATALOGO = ruta_json("mascotas.json")              # catálogo global
ARCHIVO_INVENTARIOS = ruta_json("inventarios_mascotas.json")  # inventarios por usuario

class GestorMascotas:
    def __init__(self, id_usuario, gestor_inventario):
        self.id_usuario = id_usuario
        self.gestor_inventario = gestor_inventario
        self.mascotas = self.cargar_inventario()

    def cargar_inventario(self):
        """Carga las mascotas del usuario actual desde inventarios_mascotas.json."""
        if os.path.exists(ARCHIVO_INVENTARIOS):
            try:
                with open(ARCHIVO_INVENTARIOS, "r", encoding="utf-8") as archivo:
                    data = json.load(archivo)
                    usuario_data = next((u for u in data if u["id_usuario"] == self.id_usuario), None)
                    if usuario_data:
                        return [Mascota.from_dict(m) for m in usuario_data["mascotas"].values()]
            except json.JSONDecodeError:
                return []
        return []

    def guardar_inventario(self):
        """Guarda las mascotas del usuario en inventarios_mascotas.json."""
        data = []
        if os.path.exists(ARCHIVO_INVENTARIOS):
            try:
                with open(ARCHIVO_INVENTARIOS, "r", encoding="utf-8") as archivo:
                    data = json.load(archivo)
            except json.JSONDecodeError:
                data = []

        otros = [u for u in data if u["id_usuario"] != self.id_usuario]

        usuario_data = {
            "id_usuario": self.id_usuario,
            "mascotas": {str(m.id_mascota): m.to_dict() for m in self.mascotas}
        }

        nuevas = otros + [usuario_data]

        with open(ARCHIVO_INVENTARIOS, "w", encoding="utf-8") as archivo:
            json.dump(nuevas, archivo, indent=4, ensure_ascii=False)

    def agregar_mascota(self, id_mascota, nombre=None):
        """Agrega una nueva mascota al usuario desde el catálogo."""
        if not os.path.exists(ARCHIVO_CATALOGO):
            return False, "No existe el catálogo de mascotas."

        with open(ARCHIVO_CATALOGO, "r", encoding="utf-8") as archivo:
            catalogo = json.load(archivo)

        mascota_base = next((m for m in catalogo if m["id_mascota"] == id_mascota), None)
        if not mascota_base:
            return False, "Mascota no encontrada en catálogo."

        nueva = Mascota(
            id_mascota=mascota_base["id_mascota"],
            nombre=nombre or mascota_base["nombre"],
            descripcion=mascota_base.get("descripcion", ""),
            id_usuario=self.id_usuario,
            especial=mascota_base.get("especial", False),
            progresion=mascota_base.get("progresion"),
            xp_por_comida=mascota_base.get("xp_por_comida", 10)
        )
        self.mascotas.append(nueva)
        self.guardar_inventario()
        return True, f"🐾 Nueva mascota añadida: {nueva.nombre}"

    def listar_mascotas_web(self):
        """Devuelve las mascotas del usuario en formato lista de dicts para el template web."""
        return [
            {
                "id_mascota": m.id_mascota,
                "nombre": m.nombre,
                "descripcion": m.descripcion,
                "imagen": getattr(m, "imagen", "default.png"),
                "nivel": m.nivel,
                "estado": m.estado,
                "tipo": "huevo" if m.estado == "huevo" else "mascota",
                "especial": m.especial
            }
            for m in self.mascotas
        ]

    def alimentar_mascota(self, id_mascota):
        mascota = next((m for m in self.mascotas if m.id_mascota == id_mascota), None)
        if not mascota:
            return False, "Mascota no encontrada."

        if not self.gestor_inventario.tiene_item("alimento_basico"):
            return False, "No tienes alimento para tus mascotas."

        self.gestor_inventario.consumir_item("alimento_basico", 1)
        mascota.alimentar()
        self.guardar_inventario()
        return True, f"{mascota.nombre} ha sido alimentada."

    def eclosionar_mascota(self, id_mascota, nombre):
        mascota = next((m for m in self.mascotas if m.id_mascota == id_mascota and m.estado == "huevo"), None)
        if not mascota:
            return False, "Huevo no encontrado o ya eclosionado."

        if not self.gestor_inventario.tiene_item("pocion_eclosion"):
            return False, "Necesitas una poción de eclosión para abrir este huevo."

        self.gestor_inventario.consumir_item("pocion_eclosion", 1)
        mascota.eclosionar(nuevo_nombre=nombre)
        self.guardar_inventario()
        return True, f"🐣 El huevo ha eclosionado y nació {mascota.nombre}."
