from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QComboBox, QPushButton,
    QVBoxLayout, QMessageBox
)
from PyQt5.QtGui import QFont, QIntValidator
from PyQt5.QtCore import Qt

class InterfazCliente(QWidget):
    def __init__(self, controlador):
        super().__init__()
        self.controlador = controlador

        self.setWindowTitle("Atención al Cliente")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout(self)

        # Título
        label_titulo = QLabel("Bienvenido al Banco")
        label_titulo.setFont(QFont("Arial", 18, QFont.Bold))
        label_titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_titulo)

        # Campo: Nombre
        layout.addWidget(QLabel("Nombre:"))
        self.entry_nombre = QLineEdit()
        layout.addWidget(self.entry_nombre)

        # Campo: DNI
        layout.addWidget(QLabel("DNI:"))
        self.entry_dni = QLineEdit()
        self.entry_dni.setValidator(QIntValidator(0, 99999999))
        layout.addWidget(self.entry_dni)

        # Campo: Consulta (ComboBox)
        layout.addWidget(QLabel("Consulta:"))
        self.combo_consulta = QComboBox()
        self.combo_consulta.addItems(["Transferencia", "Retiro", "Trámite", "Préstamo", "Otros"])
        layout.addWidget(self.combo_consulta)

        # Botón: Generar Consulta
        btn_generar = QPushButton("Generar Consulta")
        btn_generar.clicked.connect(self.enviarConsulta)
        layout.addWidget(btn_generar)

    def enviarConsulta(self):
        nombre = self.entry_nombre.text().strip()
        dni = self.entry_dni.text().strip()
        consulta = self.combo_consulta.currentText()

        if not nombre or not dni or not consulta:
            QMessageBox.critical(self, "Error", "Por favor, completa todos los campos.")
            return

        if len(dni) != 8 or not dni.isdigit():
            QMessageBox.critical(self, "Error", "El DNI debe tener exactamente 8 dígitos.")
            return

        cliente = self.controlador.recibirCliente("normal")
        self.controlador.asignarDatosCliente(cliente, {
            "nombre": nombre,
            "dni": dni,
            "consulta": consulta
        })

        QMessageBox.information(self, "Consulta Generada", f"Cliente {cliente} registrado.")
        self.close()
