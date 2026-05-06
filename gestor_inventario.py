import json
import os
from inventario import Inventario
from utils_rutas import ruta_json

ARCHIVO_INVENTARIO = ruta_json("inventarios.json")

class GestorInventario:
    def __init__(self, usuario=None):
        self.usuario = usuario
        self.inventarios = self.cargar_inventarios()

        # Si se pasa un usuario y no tiene inventario, se crea automáticamente
        if self.usuario is not None:
            if not any(inv["id_usuario"] == self.usuario.id_usuario for inv in self.inventarios):
                self.inventarios.append({"id_usuario": self.usuario.id_usuario, "items": {}})
                self.guardar_inventarios()

    # --- Persistencia ---
    def cargar_inventarios(self):
        if os.path.exists(ARCHIVO_INVENTARIO):
            try:
                with open(ARCHIVO_INVENTARIO, "r", encoding="utf-8") as archivo:
                    contenido = archivo.read().strip()
                    if not contenido:
                        return []
                    return json.loads(contenido)
            except json.JSONDecodeError:
                # En web no imprimimos, simplemente devolvemos lista vacía
                return []
        return []

    def guardar_inventarios(self):
        with open(ARCHIVO_INVENTARIO, "w", encoding="utf-8") as archivo:
            json.dump(self.inventarios, archivo, indent=4, ensure_ascii=False)
        self.inventarios = self.cargar_inventarios()

    # --- Operaciones sobre inventario de usuario ---
    def inventario_usuario(self):
        """Devuelve el Inventario del usuario actual como objeto."""
        if not hasattr(self, "_cache_inventario"):
            for inv in self.inventarios:
                if inv["id_usuario"] == self.usuario.id_usuario:
                    self._cache_inventario = Inventario(inv["id_usuario"], inv["items"])
                    break
            else:
                # si no existe, crear vacío
                self._cache_inventario = Inventario(self.usuario.id_usuario)
        return self._cache_inventario

    def actualizar_inventario(self, inventario: Inventario):
        """Actualiza el inventario del usuario en el JSON."""
        for inv in self.inventarios:
            if inv["id_usuario"] == inventario.id_usuario:
                inv["items"] = inventario.items
                self.guardar_inventarios()
                return
        # si no existe, lo agrego
        self.inventarios.append({"id_usuario": inventario.id_usuario, "items": inventario.items})
        self.guardar_inventarios()

    def eliminar_inventario_de_usuario(self, id_usuario):
        """Elimina el inventario de un usuario por id_usuario."""
        if not os.path.exists(ARCHIVO_INVENTARIO):
            return False

        with open(ARCHIVO_INVENTARIO, "r", encoding="utf-8") as f:
            datos = json.load(f)

        nuevo_datos = [inv for inv in datos if inv["id_usuario"] != id_usuario]

        if len(nuevo_datos) != len(datos):
            with open(ARCHIVO_INVENTARIO, "w", encoding="utf-8") as f:
                json.dump(nuevo_datos, f, indent=4, ensure_ascii=False)
            return True
        return False

    # --- Catálogo de ítems ---
    def catalogo_items(self):
        """Carga y devuelve todos los items disponibles desde items.json"""
        ruta_items = os.path.join("json", "items.json")
        if os.path.exists(ruta_items):
            with open(ruta_items, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
