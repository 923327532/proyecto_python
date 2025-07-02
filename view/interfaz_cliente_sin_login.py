from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QComboBox,
    QLineEdit, QMessageBox, QGroupBox
)
from PyQt5.QtGui import QFont, QIntValidator
from PyQt5.QtCore import Qt

class InterfazClienteSinLogin(QWidget):
    def __init__(self, gestor_clientes):
        super().__init__()
        self.gestor_clientes = gestor_clientes

        self.setWindowTitle("Cliente sin Login - Generar Ticket")
        self.setGeometry(100, 100, 400, 350)

        layout_principal = QVBoxLayout(self)

        # === CONTENEDOR PRINCIPAL ===
        grupo = QGroupBox()
        grupo_layout = QVBoxLayout()
        grupo.setLayout(grupo_layout)

        # === DNI ===
        label_dni = QLabel("Ingrese su DNI:")
        grupo_layout.addWidget(label_dni)

        self.entry_dni = QLineEdit()
        self.entry_dni.setValidator(QIntValidator(0, 99999999))
        grupo_layout.addWidget(self.entry_dni)

        # === TRÁMITE ===
        label_tramite = QLabel("Seleccione trámite:")
        grupo_layout.addWidget(label_tramite)

        self.combo_tramite = QComboBox()
        self.combo_tramite.addItems(["Consulta", "Trámite", "Pago", "Otros"])
        grupo_layout.addWidget(self.combo_tramite)

        # === BOTÓN GENERAR TICKET ===
        self.btn_generar = QPushButton("Generar Ticket")
        self.btn_generar.clicked.connect(self.generar_ticket)
        grupo_layout.addWidget(self.btn_generar)

        # === ETIQUETAS DE RESPUESTA ===
        self.label_ticket = QLabel("")
        self.label_ventanilla = QLabel("")
        self.label_espera = QLabel("")
        for lbl in [self.label_ticket, self.label_ventanilla, self.label_espera]:
            lbl.setFont(QFont("Arial", 10))
            grupo_layout.addWidget(lbl)

        layout_principal.addWidget(grupo)

    def generar_ticket(self):
        dni = self.entry_dni.text().strip()
        tramite = self.combo_tramite.currentText()

        # Validación final del DNI
        if len(dni) != 8 or not dni.isdigit():
            QMessageBox.critical(self, "Error", "El DNI debe tener exactamente 8 dígitos.")
            return

        ticket = self.gestor_clientes.generar_ticket(dni, tramite)

        if ticket is None:
            QMessageBox.critical(self, "Error", "Hubo un problema al generar el ticket.")
            return

        self.label_ticket.setText(f"Ticket generado: {ticket['codigo']}")
        self.label_ventanilla.setText(f"Ventanilla asignada: {ticket['ventanilla']}")
        self.label_espera.setText(f"Tiempo estimado de espera: {ticket['espera']} minutos")
