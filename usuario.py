from colorama import Fore, Style

class Usuario:
    def __init__(self, id_usuario, usuario, contraseña,
                xp_usuario=0, coin_usuario=0, vida_usuario=50,
                nivel_usuario=1, contador_50=0, descripcion=None, nombre_publico=None, foto_perfil=None):
        self.id_usuario = id_usuario
        self.usuario = usuario
        self.contraseña = contraseña
        self.xp_usuario = xp_usuario
        self.coin_usuario = coin_usuario
        self.vida_usuario = vida_usuario
        self.nivel_usuario = nivel_usuario
        self.contador_50 = contador_50
        self.descripcion = descripcion
        self.nombre_publico = nombre_publico
        self.foto_perfil = foto_perfil
        

    def to_dict(self):
        return {
            "id_usuario": self.id_usuario,
            "usuario": self.usuario,
            "contraseña": self.contraseña,
            "xp_usuario": self.xp_usuario,
            "coin_usuario": self.coin_usuario,
            "vida_usuario": self.vida_usuario,
            "nivel_usuario": self.nivel_usuario,
            "contador_50": self.contador_50,
            "descripcion": self.descripcion,
            "nombre_publico": self.nombre_publico,
            "foto_perfil": self.foto_perfil
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
            contador_50=data.get("contador_50", 0),
            descripcion=data.get("descripcion"),
            nombre_publico=data.get("nombre_publico"),
            foto_perfil=data.get("foto_perfil")
        )

    #metodo para ver perfil
    def ver_perfil(self):
        print(Fore.LIGHTYELLOW_EX + "\n--- Perfil del Usuario ---" + Style.RESET_ALL)
        print(Fore.LIGHTYELLOW_EX + f"Nombre público: {self.nombre_publico or self.usuario}" + Style.RESET_ALL)
        print(Fore.LIGHTYELLOW_EX + f"Salud: {self.vida_usuario}" + Style.RESET_ALL)
        print(Fore.LIGHTYELLOW_EX + f"Nivel: {self.nivel_usuario}" + Style.RESET_ALL)
        print(Fore.LIGHTYELLOW_EX + f"XP: {self.xp_usuario}" + Style.RESET_ALL)
        print(Fore.LIGHTYELLOW_EX + f"Coin: {self.coin_usuario}" + Style.RESET_ALL)
        print(Fore.LIGHTYELLOW_EX + f"Descripción: {self.descripcion or 'Sin Descripción'}" + Style.RESET_ALL)
        print(Fore.LIGHTYELLOW_EX + f"Foto: {self.foto_perfil or 'Sin Foto'}" + Style.RESET_ALL)
        
    def editar_perfil(self):
        self.ver_perfil()
        opcion = input("\n¿Desea modificar su perfil?(s/n): ")
        
        while True:
            try:
                if opcion == "s":
                    nombre_publico = input("Nombre Público: ")
                    descripcion = input("Sobre mí: ")
                    foto = input("Ingresa la URL de la imagen: ")
        
                    if nombre_publico.strip():
                        self.nombre_publico = nombre_publico
                    if descripcion.strip():
                        self.descripcion = descripcion
                    if foto.strip():
                        self.foto_perfil = foto
        
                    print(Fore.GREEN + "\nPerfil actualizado exitosamente" + Style.RESET_ALL)
                    return
                elif opcion == "n":
                    print(Fore.YELLOW + "\nOperación cancelada, volviendo al menú..." + Style.RESET_ALL)
                    return
                else:
                    print(Fore.RED + "\n⚠️ Seleccione una opción válida" + Style.RESET_ALL)
                    return
            except:
                print(Fore.RED + "⚠️ Seleccione una Opción válida" + Style.RESET_ALL)
    
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
    
