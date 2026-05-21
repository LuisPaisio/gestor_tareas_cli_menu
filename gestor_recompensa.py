import os
import json
import random
from recompensa import Recompensa
from utils_rutas import ruta_json

ARCHIVO_RECOMPENSAS = ruta_json("recompensas.json")

class GestorRecompensas:
    def __init__(self):
        self.historial = self.cargar_historial()

    def cargar_historial(self):
        """Carga el historial de recompensas desde JSON."""
        if os.path.exists(ARCHIVO_RECOMPENSAS):
            try:
                with open(ARCHIVO_RECOMPENSAS, "r", encoding="utf-8") as archivo:
                    contenido = archivo.read().strip()
                    if not contenido:
                        return []
                    data = json.loads(contenido)
                    return [Recompensa(**r) for r in data]
            except json.JSONDecodeError:
                return []
        return []

    def guardar_historial(self):
        """Guarda el historial de recompensas en JSON."""
        with open(ARCHIVO_RECOMPENSAS, "w", encoding="utf-8") as archivo:
            json.dump([r.__dict__ for r in self.historial], archivo, indent=4, ensure_ascii=False)

    def aplicar_recompensas(self, usuario, recompensas: list[Recompensa], es_penalizacion=False):
        """
        Aplica recompensas o penalizaciones y devuelve:
        - resultados en formato dict para la web
        - flag murio (True si el usuario murió durante la aplicación)
        """
        if not recompensas:
            return [], False

        resultados = []
        murio = False

        for recompensa in recompensas:
            resultado = recompensa.aplicar_usuario(usuario)  # dict con base, bonus, total (+ murio en caso de vida)

            # 👇 capturamos el flag de muerte si viene en el resultado
            if resultado.get("murio"):
                murio = True

            self.historial.append(recompensa)
            resultados.append({
                "id": recompensa.id_recompensa,
                "nombre": recompensa.nombre,
                "tipo": recompensa.tipo,
                "valor": recompensa.valor,
                "resultado": resultado,
                "penalizacion": es_penalizacion
            })

        self.guardar_historial()
        return resultados, murio

    def generar_recompensas_extra(self):
            """Genera recompensas aleatorias (drops de ítems)."""
            drops = []
            if random.randint(1, 100) <= 10:  # 10% chance huevo
                drops.append(Recompensa(999, "Huevo Básico", "aleatorio", "Huevo Básico"))
            if random.randint(1, 100) <= 5:   # 5% chance poción
                drops.append(Recompensa(1000, "Poción de Eclosión", "aleatorio", "Poción de Eclosión"))
            if random.randint(1, 100) <= 15:  # 15% chance alimento
                drops.append(Recompensa(1001, "Alimento Básico", "aleatorio", "Alimento Básico"))
            return drops