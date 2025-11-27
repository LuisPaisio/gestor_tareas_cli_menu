import json
import os
from inventario import Inventario
from colorama import Fore, Style

ARCHIVO_INVENTARIO = os.path.join("json", "inventarios.json")

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
                print("⚠️ El archivo de inventarios está corrupto o vacío. Se iniciará una lista nueva.")
                return []
        return []

    def guardar_inventarios(self):
        with open(ARCHIVO_INVENTARIO, "w", encoding="utf-8") as archivo:
            json.dump(self.inventarios, archivo, indent=4, ensure_ascii=False)
        self.inventarios = self.cargar_inventarios()

    # --- Operaciones sobre inventario de usuario ---
    def inventario_usuario(self):
        """Devuelve el Inventario del usuario actual, siempre la misma instancia."""
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
            print(Fore.YELLOW + "⚠️ No se encontró el archivo de inventario." + Style.RESET_ALL)
            return

        with open(ARCHIVO_INVENTARIO, "r", encoding="utf-8") as f:
            datos = json.load(f)

        # datos es una lista de dicts
        nuevo_datos = [inv for inv in datos if inv["id_usuario"] != id_usuario]

        if len(nuevo_datos) != len(datos):
            with open(ARCHIVO_INVENTARIO, "w", encoding="utf-8") as f:
                json.dump(nuevo_datos, f, indent=4, ensure_ascii=False)
            #print(Fore.YELLOW + f"🧹 Inventario del usuario {id_usuario} eliminado correctamente." + Style.RESET_ALL)
        #else:
            #print(Fore.YELLOW + f"⚠️ El usuario {id_usuario} no tenía inventario registrado." + Style.RESET_ALL)
