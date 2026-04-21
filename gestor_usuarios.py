import json
import os
from usuario import Usuario
from utils_rutas import ruta_json

ARCHIVO_USUARIOS = ruta_json("usuarios.json")
ARCHIVO_TAREAS = ruta_json("tareas.json")

class GestorUsuarios:
    def __init__(self):
        self.usuarios = self.cargar_usuarios()

    # -------------------------------
    # Manejo de usuarios
    # -------------------------------
    def cargar_usuarios(self):
        if os.path.exists(ARCHIVO_USUARIOS):
            try:
                with open(ARCHIVO_USUARIOS, "r", encoding="utf-8") as archivo:
                    contenido = archivo.read().strip()
                    if not contenido:
                        return []
                    data = json.loads(contenido)
                    return [Usuario.from_dict(u) for u in data]
            except json.JSONDecodeError:
                return []
        return []

    def guardar_usuarios(self):
        with open(ARCHIVO_USUARIOS, "w", encoding="utf-8") as archivo:
            json.dump([u.to_dict() for u in self.usuarios], archivo, indent=4, ensure_ascii=False)
        self.usuarios = self.cargar_usuarios()

    def actualizar_usuario(self, usuario):
        for i, u in enumerate(self.usuarios):
            if u.id_usuario == usuario.id_usuario:
                self.usuarios[i] = usuario
                break
        self.guardar_usuarios()

    # -------------------------------
    # Métodos para la web
    # -------------------------------
    def login_web(self, username, password):
        """Login para Flask: recibe username y password desde formulario"""
        for usuario in self.usuarios:
            if usuario.usuario == username and usuario.contraseña == password:
                usuario.gestor_usuarios = self
                return usuario
        return None

    def register_web(self, username, password):
        """Registro para Flask: recibe username y password desde formulario"""
        if len(username) < 8 or len(password) < 8 or username.strip() == "" or password.strip() == "":
            return None

        for usuario in self.usuarios:
            if usuario.usuario == username:
                return None

        ultimo_id = max([u.id_usuario for u in self.usuarios], default=0)
        nuevo_usuario = Usuario(id_usuario=ultimo_id + 1, usuario=username, contraseña=password)
        nuevo_usuario.gestor_usuarios = self

        self.usuarios.append(nuevo_usuario)
        self.guardar_usuarios()
        return nuevo_usuario

    def eliminar_usuario_web(self, username, password, gestor_tareas, gestor_inventario):
        """Eliminar usuario desde la web, validando credenciales"""
        for usuario in self.usuarios:
            if usuario.usuario == username and usuario.contraseña == password:
                gestor_tareas.eliminar_tareas_de_usuario(usuario.id_usuario)
                gestor_inventario.eliminar_inventario_de_usuario(usuario.id_usuario)
                self.usuarios.remove(usuario)
                self.guardar_usuarios()
                return True
        return False
    
    def get_usuario_por_id(self, id_usuario):
        """Devuelve el objeto Usuario con el id_usuario indicado"""
        for usuario in self.usuarios:
            if int(usuario.id_usuario) == int(id_usuario):
                usuario.gestor_usuarios = self
                return usuario
        return None

    def get_usuario_por_nombre(self, nombre_usuario):
        """Devuelve el objeto Usuario con el nombre indicado"""
        for usuario in self.usuarios:
            if usuario.usuario == nombre_usuario:
                usuario.gestor_usuarios = self
                return usuario
        return None
