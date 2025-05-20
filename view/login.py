from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from view.interfaz_admin import InterfazAdmin

class VentanaLogin(QWidget):
    def __init__(self, gestor_usuarios, gestor_banco, gestor_clientes):
        super().__init__()
        self.gestor_usuarios = gestor_usuarios
        self.gestor_banco = gestor_banco
        self.gestor_clientes = gestor_clientes
        self.interfaz = None  # ventana siguiente (admin)

        self.setWindowTitle("Login Admin")
        self.setGeometry(100, 100, 400, 250)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Usuario:"))
        self.entry_usuario = QLineEdit()
        layout.addWidget(self.entry_usuario)

        layout.addWidget(QLabel("Contraseña:"))
        self.entry_contra = QLineEdit()
        self.entry_contra.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.entry_contra)

        btn_ingresar = QPushButton("Ingresar")
        btn_ingresar.clicked.connect(self.login)
        layout.addWidget(btn_ingresar)

        self.setLayout(layout)

    def login(self):
        usuario = self.entry_usuario.text().strip()
        contra = self.entry_contra.text().strip()

        datos = {"usuario": usuario, "contraseña": contra}
        usuario_autenticado = self.gestor_usuarios.autenticarUsuario(datos)

        if usuario_autenticado and usuario_autenticado.usuario == "admin":
            self.close()
            self.interfaz = InterfazAdmin(self.gestor_banco)
            self.interfaz.show()
        else:
            QMessageBox.critical(self, "Error", "Credenciales incorrectas o no es admin.")
