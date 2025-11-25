import json
import os
from inventario import Inventario

ARCHIVO_INVENTARIO = os.path.join("json", "inventarios.json")

class GestorInventario:
    def __init__(self, usuario=None):
        self.usuario = usuario
        self.inventarios = self.cargar_inventarios()

        # Si el usuario no tiene inventario, se crea automáticamente
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
                print("⚠️ El archivo de inventarios está corrupto o vacío. Se iniciará una lista nueva.")
                return []
        return []

    def guardar_inventarios(self):
        with open(ARCHIVO_INVENTARIO, "w", encoding="utf-8") as archivo:
            json.dump(self.inventarios, archivo, indent=4, ensure_ascii=False)
        self.inventarios = self.cargar_inventarios()

    # --- Operaciones sobre inventario de usuario ---
    def inventario_usuario(self):
        """Devuelve el Inventario del usuario actual."""
        for inv in self.inventarios:
            if inv["id_usuario"] == self.usuario.id_usuario:
                return Inventario(inv["id_usuario"], inv["items"])
        return Inventario(self.usuario.id_usuario)

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
