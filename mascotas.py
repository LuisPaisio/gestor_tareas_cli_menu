from colorama import Fore, Style

class Mascota:
    def __init__(self, id_mascota, nombre, id_usuario,
                nivel=1, xp=0, estado="huevo",
                especial=False, descripcion="",
                progresion=None, xp_por_comida=10):
        self.id_mascota = id_mascota
        self.nombre = nombre
        self.descripcion = descripcion   # viene del catálogo global
        self.id_usuario = id_usuario     # vínculo con el dueño
        self.nivel = nivel
        self.xp = xp
        self.estado = estado             # soporta "huevo", "bebé", "adulto", "montura"
        self.especial = especial
        self.progresion = progresion or {
            "huevo": "bebé",
            "bebé": "adulto",
            "adulto": "montura"
        }
        self.xp_por_comida = xp_por_comida

    def to_dict(self):
        """Convierte la mascota a dict para guardar en inventarios_mascotas.json"""
        return {
            "id_mascota": self.id_mascota,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "id_usuario": self.id_usuario,
            "nivel": self.nivel,
            "xp": self.xp,
            "estado": self.estado,
            "especial": self.especial,
            "progresion": self.progresion,
            "xp_por_comida": self.xp_por_comida
        }

    @classmethod
    def from_dict(cls, data):
        """Reconstruye una mascota desde inventarios_mascotas.json"""
        return cls(
            id_mascota=data["id_mascota"],
            nombre=data["nombre"],
            descripcion=data.get("descripcion", ""),
            id_usuario=data["id_usuario"],
            nivel=data.get("nivel", 1),
            xp=data.get("xp", 0),
            estado=data.get("estado", "huevo"),
            especial=data.get("especial", False),
            progresion=data.get("progresion", None),
            xp_por_comida=data.get("xp_por_comida", 10)
        )

    def alimentar(self):
        if self.estado == "huevo":
            print(Fore.YELLOW + f"⚠️ {self.nombre} aún es un huevo, primero debe eclosionar." + Style.RESET_ALL)
            return

        # XP otorgada según catálogo
        self.xp += self.xp_por_comida
        umbral = 30 * self.nivel

        if self.xp >= umbral:
            self.nivel += 1
            self.xp -= umbral

            # evolución automática según progresión
            if self.nivel >= 3 and self.estado == "bebé":
                self.estado = self.progresion.get("bebé", "adulto")
                print(Fore.GREEN + f"✨ {self.nombre} evolucionó a {self.estado}!" + Style.RESET_ALL)
            elif self.nivel >= 5 and self.estado == "adulto":
                self.estado = self.progresion.get("adulto", "montura")
                print(Fore.GREEN + f"✨ {self.nombre} evolucionó a {self.estado}!" + Style.RESET_ALL)
            else:
                print(Fore.GREEN + f"🎉 {self.nombre} subió a nivel {self.nivel} → Estado: {self.estado}" + Style.RESET_ALL)

    def eclosionar(self, nuevo_nombre=None):
        """Convierte un huevo en mascota bebé."""
        if self.estado != "huevo":
            print(Fore.YELLOW + f"⚠️ {self.nombre} ya ha eclosionado." + Style.RESET_ALL)
            return
        if nuevo_nombre:
            self.nombre = nuevo_nombre
        self.estado = self.progresion.get("huevo", "bebé")
        self.nivel = 1
        self.xp = 0
        print(Fore.GREEN + f"🥚 El huevo ha eclosionado en {self.nombre}!" + Style.RESET_ALL)
