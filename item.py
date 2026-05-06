class Item:
    def __init__(
        self,
        id_item: int,
        nombre: str,
        precio: int,
        descripcion: str,
        tipo: str,
        slot: str = None,
        efecto: dict = None,
        efecto_temporal: dict = None,   # nuevo atributo
        efecto_turnos: int = 0,         # nuevo atributo
        imagen: str = None
    ):
        if precio < 0:
            raise ValueError("El precio no puede ser negativo")
        if tipo == "equipable" and not slot:
            raise ValueError("Los ítems equipables deben tener un slot definido")

        self.id_item = id_item
        self.nombre = nombre
        self.precio = precio
        self.descripcion = descripcion
        self.tipo = tipo
        self.slot = slot
        self.efecto = efecto or {}
        self.efecto_temporal = efecto_temporal or {}
        self.efecto_turnos = efecto_turnos
        self.imagen = imagen

    def to_dict(self) -> dict:
        data = {
            "id_item": self.id_item,
            "nombre": self.nombre,
            "precio": self.precio,
            "descripcion": self.descripcion,
            "tipo": self.tipo,
            "efecto": self.efecto,
            "efecto_temporal": self.efecto_temporal,
            "efecto_turnos": self.efecto_turnos
        }
        if self.slot:
            data["slot"] = self.slot
        if self.imagen:
            data["imagen"] = self.imagen
        return data

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id_item=data["id_item"],
            nombre=data["nombre"],
            precio=data["precio"],
            descripcion=data["descripcion"],
            tipo=data["tipo"],
            slot=data.get("slot"),
            efecto=data.get("efecto"),
            efecto_temporal=data.get("efecto_temporal"),
            efecto_turnos=data.get("efecto_turnos", 0),
            imagen=data.get("imagen")
        )

    def __str__(self) -> str:
        base = f"{self.nombre} ({self.precio} coins) - {self.descripcion}"
        if self.slot:
            base += f" [Slot: {self.slot}]"
        if self.imagen:
            base += f" [Imagen: {self.imagen}]"
        return base
