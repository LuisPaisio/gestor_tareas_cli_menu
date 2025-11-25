class Item:
    def __init__(self, id_item: int, nombre: str, precio: int, descripcion: str):
        if precio < 0:
            raise ValueError("El precio no puede ser negativo")
        self.id_item = id_item
        self.nombre = nombre
        self.precio = precio
        self.descripcion = descripcion

    def to_dict(self) -> dict:
        return {
            "id_item": self.id_item,
            "nombre": self.nombre,
            "precio": self.precio,
            "descripcion": self.descripcion
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id_item=data["id_item"],
            nombre=data["nombre"],
            precio=data["precio"],
            descripcion=data["descripcion"]
        )

    def __str__(self) -> str:
        return f"{self.nombre} ({self.precio} coins) - {self.descripcion}"
