from PyQt5.QtWidgets import QApplication
from controllers.gestor_banco import GestorBanco
from controllers.gestor_clientes import GestorClientes
from controllers.gestor_usuarios import GestorUsuarios
from view.main_login import ventana_principal

if __name__ == "__main__":
    app = QApplication([])

    gestor_usuarios = GestorUsuarios()
    gestor_banco = GestorBanco()
    gestor_clientes = GestorClientes()

    ventana = ventana_principal(gestor_usuarios, gestor_banco, gestor_clientes)

    app.exec_()
