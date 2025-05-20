
class Cliente:
    def __init__(self, tipo, id_cliente):
        self.tipo = tipo  
        self.id = id_cliente
        self.nombre = None
        self.dni = None
        self.consulta = None

    def __str__(self):
        nombre = self.nombre or "No definido"
        dni = self.dni or "No definido"
        consulta = self.consulta or "No definida"

        return (f"{self.tipo.upper():<13} | "
                f"ID: {self.id:<5} | "
                f"Nombre: {nombre:<20} | "
                f"DNI: {dni:<10} | "
                f"Consulta: {consulta}")
