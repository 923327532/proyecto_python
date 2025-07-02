from controllers.gestor_clientes import GestorClientes
from controllers.gestor_usuarios import GestorUsuarios
class GestorBanco:
    def __init__(self):
        self.clientes = GestorClientes()
        self.usuarios = GestorUsuarios()

    # ======== CLIENTES ========
    def recibirCliente(self, tipo):
        return self.clientes.recibirCliente(tipo)

    def asignarDatosCliente(self, cliente, datos):
        self.clientes.asignarDatosCliente(cliente, datos)

    def ingresarClientes(self):
        self.clientes.ingresarClientes()

    def atenderClientes(self):
        self.clientes.atenderClientes()

    def finalizarAtencion(self):
        return self.clientes.finalizarAtencion()

    def estadoBanco(self):
        return self.clientes.estadoBanco()

    # ======== USUARIOS (ADMIN / EMPLEADOS) ========
    def registrarUsuario(self, datos):
        return self.usuarios.registrarUsuario(datos)

    def autenticarUsuario(self, datos):
        return self.usuarios.autenticarUsuario(datos)
