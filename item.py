class Item:
    def __init__(self, id_item: int, nombre: str, precio: int, descripcion: str, tipo: str, slot: str = None, efecto: str = None):
        if precio < 0:
            raise ValueError("El precio no puede ser negativo")
        if tipo == "equipable" and not slot:
            raise ValueError("Los ítems equipables deben tener un slot definido")
        self.id_item = id_item
        self.nombre = nombre
        self.precio = precio
        self.descripcion = descripcion
        self.tipo = tipo
        self.slot = slot  # puede ser None si es consumible
        self.efecto = efecto

    def to_dict(self) -> dict:
        data = {
            "id_item": self.id_item,
            "nombre": self.nombre,
            "precio": self.precio,
            "descripcion": self.descripcion,
            "tipo": self.tipo,
            "efecto": self.efecto
        }
        if self.slot:  # solo incluir slot si existe
            data["slot"] = self.slot
        return data

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id_item=data["id_item"],
            nombre=data["nombre"],
            precio=data["precio"],
            descripcion=data["descripcion"],
            tipo=data["tipo"],
            slot=data.get("slot"),  # puede no estar en consumibles
            efecto=data.get("efecto")
        )

    def __str__(self) -> str:
        if self.slot:
            return f"{self.nombre} ({self.precio} coins) - {self.descripcion} [Slot: {self.slot}]"
        return f"{self.nombre} ({self.precio} coins) - {self.descripcion}"
