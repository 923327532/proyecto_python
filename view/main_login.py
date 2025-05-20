from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout
from view.login import VentanaLogin
from view.interfaz_cliente import InterfazCliente

class VentanaPrincipal(QWidget):
    def __init__(self, gestor_usuarios, gestor_banco, gestor_clientes):
        super().__init__()
        self.gestor_usuarios = gestor_usuarios
        self.gestor_banco = gestor_banco
        self.gestor_clientes = gestor_clientes
        self.interfaz_actual = None  # para guardar la ventana activa

        self.setWindowTitle("Seleccionar Perfil")
        self.setGeometry(100, 100, 300, 150)

        layout = QVBoxLayout()

        btn_admin = QPushButton("Entrar como Admin")
        btn_admin.clicked.connect(self.abrir_login_admin)
        layout.addWidget(btn_admin)

        btn_cliente = QPushButton("Entrar como Cliente")
        btn_cliente.clicked.connect(self.abrir_interfaz_cliente)
        layout.addWidget(btn_cliente)

        self.setLayout(layout)

    def abrir_login_admin(self):
        self.close()
        self.interfaz_actual = VentanaLogin(self.gestor_usuarios, self.gestor_banco, self.gestor_clientes)
        self.interfaz_actual.show()

    def abrir_interfaz_cliente(self):
        self.close()
        self.interfaz_actual = InterfazCliente(self.gestor_clientes)
        self.interfaz_actual.show()

def ventana_principal(gestor_usuarios, gestor_banco, gestor_clientes):
    ventana = VentanaPrincipal(gestor_usuarios, gestor_banco, gestor_clientes)
    ventana.show()
    return ventana
