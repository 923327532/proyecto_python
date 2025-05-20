class Usuario:
    def __init__(self, id_usuario):
        self.id = id_usuario
        self.nombre = None
        self.usuario = None
        self.contraseña = None

    def __str__(self):
        nombre = self.nombre or "No definido"
        usuario = self.usuario or "No definido"
        return f"USUARIO ADMIN | ID: {self.id:<5} | Nombre: {nombre:<20} | Usuario: {usuario}"
