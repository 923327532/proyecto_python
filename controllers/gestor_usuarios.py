from model import db  
from model.cola import Cola
from model.usuario import Usuario

class GestorUsuarios:
    def __init__(self):
        self.colaUsuarios = Cola(10)
        self.contador_usuarios = 1
        usuario_default = Usuario(f"{self.contador_usuarios:03d}")
        usuario_default.nombre = "Admin General"
        usuario_default.usuario = "admin"
        usuario_default.contraseña = "1234"
        self.colaUsuarios.encolar(usuario_default)
        self.contador_usuarios += 1

    def registrarUsuario(self, datos):
        id_usuario = f"{self.contador_usuarios:03d}"
        self.contador_usuarios += 1

        usuario = Usuario(id_usuario)
        usuario.nombre = datos["nombre"]
        usuario.usuario = datos["usuario"]
        usuario.contraseña = datos["contraseña"]

        self.colaUsuarios.encolar(usuario)

        conexion = db.conectar()
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nombre, usuario, contraseña) VALUES (%s, %s, %s)", 
            (usuario.nombre, usuario.usuario, usuario.contraseña)
        )
        conexion.commit()
        cursor.close()
        conexion.close()

        return usuario

    def autenticarUsuario(self, datos):
        user = datos["usuario"]
        password = datos["contraseña"]
        actual = self.colaUsuarios.frente
        while actual:
            u = actual.dato
            if u.usuario == user and u.contraseña == password:
                return u
            actual = actual.siguiente
        conexion = db.conectar()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s AND contraseña = %s", (user, password))
        result = cursor.fetchone()
        cursor.close()
        conexion.close()

        if result:
            u = Usuario(result["id"])
            u.nombre = result["nombre"]
            u.usuario = result["usuario"]
            u.contraseña = result["contraseña"]
            return u

        return None
