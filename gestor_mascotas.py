import os
import json
from mascotas import Mascota
from colorama import Fore, Style
from utils_rutas import ruta_json

# ARCHIVO_CATALOGO = os.path.join("json", "mascotas.json")              # catálogo global
# ARCHIVO_INVENTARIOS = os.path.join("json", "inventarios_mascotas.json")  # inventarios por usuario

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
                print(Fore.RED + "⚠️ El archivo de inventarios de mascotas está corrupto. Se iniciará vacío." + Style.RESET_ALL)
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
            print(Fore.RED + "⚠️ No existe el catálogo de mascotas." + Style.RESET_ALL)
            return

        with open(ARCHIVO_CATALOGO, "r", encoding="utf-8") as archivo:
            catalogo = json.load(archivo)

        mascota_base = next((m for m in catalogo if m["id_mascota"] == id_mascota), None)
        if not mascota_base:
            print(Fore.RED + "⚠️ Mascota no encontrada en catálogo." + Style.RESET_ALL)
            return

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
        print(Fore.CYAN + f"🐾 Nueva mascota añadida: {nueva.nombre}" + Style.RESET_ALL)

    def mostrar_mascotas(self, enumerado=False):
        """Muestra todas las mascotas del usuario, con opción de enumeración.
        Devuelve True si hay mascotas, False si no."""
        if not self.mascotas:
            print(Fore.YELLOW + "No tienes mascotas aún." + Style.RESET_ALL)
            self.enumeracion_mascotas = []
            return False   # 🔹 importante: devuelve False si no hay mascotas

        print(Fore.YELLOW + "\n=== Tus Mascotas ===" + Style.RESET_ALL)
        self.enumeracion_mascotas = []

        for idx, m in enumerate(self.mascotas, start=1):
            if enumerado:
                print(f"{idx}. {m.nombre} | Nivel {m.nivel} | Estado: {m.estado} | Especial: {m.especial}")
                self.enumeracion_mascotas.append(m.id_mascota)
            else:
                print(f"{m.id_mascota} - {m.nombre} | Nivel {m.nivel} | Estado: {m.estado} | Especial: {m.especial}")

        return True   # 🔹 devuelve True si sí hay mascotas


    def alimentar_mascota(self, id_mascota):
        mascota = next((m for m in self.mascotas if m.id_mascota == id_mascota), None)
        if not mascota:
            print(Fore.RED + "⚠️ Mascota no encontrada." + Style.RESET_ALL)
            return

        if not self.gestor_inventario.tiene_item("alimento_basico"):
            print(Fore.RED + "⚠️ No tienes alimento para tus mascotas." + Style.RESET_ALL)
            return

        self.gestor_inventario.consumir_item("alimento_basico", 1)

        mascota.alimentar()
        self.guardar_inventario()

    def eclosionar_mascota(self, id_mascota, nombre):
        mascota = next((m for m in self.mascotas if m.id_mascota == id_mascota and m.estado == "huevo"), None)
        if not mascota:
            print(Fore.RED + "⚠️ Huevo no encontrado o ya eclosionado." + Style.RESET_ALL)
            return

        if not self.gestor_inventario.tiene_item("pocion_eclosion"):
            print(Fore.RED + "⚠️ Necesitas una poción de eclosión para abrir este huevo." + Style.RESET_ALL)
            return

        self.gestor_inventario.consumir_item("pocion_eclosion", 1)

        mascota.eclosionar(nuevo_nombre=nombre)
        self.guardar_inventario()
