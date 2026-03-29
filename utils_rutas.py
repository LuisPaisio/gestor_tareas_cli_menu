import os
import sys

def ruta_json(nombre_archivo):
    """
    Devuelve la ruta correcta al archivo JSON tanto en desarrollo
    como cuando está empaquetado con PyInstaller.
    """
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS  # carpeta temporal de PyInstaller
    else:
        base_path = os.path.abspath(".")  # carpeta del proyecto

    return os.path.join(base_path, "json", nombre_archivo)
