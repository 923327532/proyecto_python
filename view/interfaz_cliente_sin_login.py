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

        # --- Estilos suaves BCP ---
        self.setStyleSheet("""
            QWidget {
                background-color: #FAFAFA; /* Fondo muy claro */
                color: #333333; /* Texto gris oscuro */
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 14px;
            }
            QLabel {
                font-weight: 600;
                margin-top: 8px;
                margin-bottom: 4px;
            }
            QLineEdit, QComboBox {
                border: 1.5px solid #CCCCCC;
                border-radius: 6px;
                padding: 6px 8px;
                background-color: white;
                selection-background-color: #FF6600;
                selection-color: white;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #FF6600;
                outline: none;
            }
            QPushButton {
                background-color: #FF6600; /* Naranja BCP suave */
                color: white;
                border: none;
                padding: 10px;
                border-radius: 8px;
                font-weight: bold;
                transition: background-color 0.3s;
            }
            QPushButton:hover {
                background-color: #E65500;
            }
            QPushButton:pressed {
                background-color: #B34700;
            }
        """)

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
