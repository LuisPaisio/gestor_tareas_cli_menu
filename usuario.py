from colorama import Fore, Style

class Usuario:
    def __init__(self, id_usuario, usuario, contraseña,
                xp_usuario=0, coin_usuario=0, vida_usuario=50,
                nivel_usuario=1, contador_50=0):
        self.id_usuario = id_usuario
        self.usuario = usuario
        self.contraseña = contraseña
        self.xp_usuario = xp_usuario
        self.coin_usuario = coin_usuario
        self.vida_usuario = vida_usuario
        self.nivel_usuario = nivel_usuario
        self.contador_50 = contador_50

    def to_dict(self):
        return {
            "id_usuario": self.id_usuario,
            "usuario": self.usuario,
            "contraseña": self.contraseña,
            "xp_usuario": self.xp_usuario,
            "coin_usuario": self.coin_usuario,
            "vida_usuario": self.vida_usuario,
            "nivel_usuario": self.nivel_usuario,
            "contador_50": self.contador_50
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id_usuario=data["id_usuario"],
            usuario=data["usuario"],
            contraseña=data["contraseña"],
            xp_usuario=data.get("xp_usuario", 0),
            coin_usuario=data.get("coin_usuario", 0),
            vida_usuario=data.get("vida_usuario", 50),
            nivel_usuario=data.get("nivel_usuario", 1),
            contador_50=data.get("contador_50", 0)
        )

    # Métodos de XP, Coins y Vida
    def sumar_xp_coins(self, xp, coins):
        self.xp_usuario += xp
        self.coin_usuario += coins
        print(Fore.GREEN + f"\n¡Felicidades! Has ganado {xp} XP y {coins} coins." + Style.RESET_ALL)

    def restar_vida(self, vida):
        self.vida_usuario -= vida
        if self.vida_usuario <= 0:
            self.vida_usuario = 0
            print(Fore.RED + "Tu vida llegó a 0." + Style.RESET_ALL)
            xp_perdido, coins_perdidos = 15, 10
            self.xp_usuario = max(0, self.xp_usuario - xp_perdido)
            self.coin_usuario = max(0, self.coin_usuario - coins_perdidos)
            print(Fore.YELLOW + f"Has perdido {xp_perdido} XP, {coins_perdidos} coins y todo lo que tenías equipado." + Style.RESET_ALL)
            self.vida_usuario = 50
            print(Fore.YELLOW + f"Tu salud ha sido restaurada a {self.vida_usuario}" + Style.RESET_ALL)
        else:
            print(Fore.RED + f"\nHas perdido {vida} puntos de vida. Vida actual: {self.vida_usuario}/50" + Style.RESET_ALL)

    def ganar_recompensas(self,tarea):
        pass
    
    def calcular_xp(self, tarea):
        pass
    
    def calcular_coins(self, tarea):
        pass
    
