from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton, QTextEdit, QVBoxLayout,
    QHBoxLayout, QComboBox, QDialog, QLineEdit, QMessageBox, QFormLayout, QGroupBox
)
from PyQt5.QtGui import QFont, QIntValidator
from PyQt5.QtCore import Qt

class InterfazAdmin(QMainWindow):
    def __init__(self, controlador):
        super().__init__()
        self.setWindowTitle("Gestión de Colas del Banco - Admin")
        self.setGeometry(100, 100, 750, 600)
        self.controlador = controlador
        self.tipoCliente = "normal"

        # === CONTENEDOR PRINCIPAL ===
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # === TÍTULO ===
        titulo = QLabel("Sistema de Gestión de Colas - Banco (Admin)")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(titulo)

        # === SECCIÓN: OPCIONES DE CLIENTES ===
        grupo_formulario = QGroupBox("Opciones del Administrador")
        grupo_formulario.setFont(QFont("Arial", 14, QFont.Bold))
        grupo_formulario.setStyleSheet("QGroupBox { margin-top: 20px; }")
        layout_form = QVBoxLayout(grupo_formulario)

        # Tipo de cliente
        layout_tipo = QHBoxLayout()
        label_tipo = QLabel("Tipo de Cliente:")
        label_tipo.setFont(QFont("Arial", 13))
        self.comboTipo = QComboBox()
        self.comboTipo.setFont(QFont("Arial", 12))
        self.comboTipo.addItems(["discapacitado", "vip", "normal"])
        self.comboTipo.setCurrentText(self.tipoCliente)
        self.comboTipo.currentTextChanged.connect(self.setTipoCliente)
        layout_tipo.addWidget(label_tipo)
        layout_tipo.addWidget(self.comboTipo)
        layout_form.addLayout(layout_tipo)

        # Botones
        botones = [
            ("Agregar Cliente", self.agregarCliente),
            ("Ingresar Clientes al Banco", self.ingresarClientes),
            ("Enviar a Ventanilla", self.atenderClientes),
            ("Finalizar Atención", self.finalizarAtencion)
        ]
        for texto, funcion in botones:
            btn = QPushButton(texto)
            btn.setMinimumHeight(35)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2E86C1;
                    color: white;
                    border-radius: 10px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #1A5276;
                }
            """)
            btn.clicked.connect(funcion)
            layout_form.addWidget(btn)

        main_layout.addWidget(grupo_formulario)

        # === SECCIÓN: ESTADO ACTUAL ===
        grupo_estado = QGroupBox("Estado Actual del Banco")
        grupo_estado.setFont(QFont("Arial", 14, QFont.Bold))
        layout_estado = QVBoxLayout(grupo_estado)

        self.estado = QTextEdit()
        self.estado.setFont(QFont("Courier New", 12))
        self.estado.setReadOnly(True)
        layout_estado.addWidget(self.estado)

        main_layout.addWidget(grupo_estado)

        self.actualizarEstado()

        # === ESTILO MODERNO GENERAL ===
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F4F6F7;
            }

            QGroupBox {
                border: 1px solid #D5D8DC;
                border-radius: 8px;
                margin-top: 20px;
                padding: 10px;
                background-color: #FBFCFC;
            }

            QLabel {
                color: #2C3E50;
            }

            QComboBox {
                background-color: white;
                border: 1px solid #BFC9CA;
                border-radius: 5px;
                padding: 5px;
            }

            QTextEdit {
                background-color: white;
                border: 1px solid #D5D8DC;
                border-radius: 5px;
                padding: 10px;
            }

            QPushButton {
                background-color: #3498DB;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 10px;
                margin-bottom: 8px;
            }

            QPushButton:hover {
                background-color: #2980B9;
            }

            QDialog {
                background-color: #FBFCFC;
            }

            QLineEdit {
                background-color: white;
                border: 1px solid #D5D8DC;
                border-radius: 5px;
                padding: 5px;
            }

            QFormLayout {
                padding: 10px;
            }
        """)

    def setTipoCliente(self, tipo):
        self.tipoCliente = tipo

    def agregarCliente(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Datos del Cliente")
        dialog.setFixedSize(400, 250)
        layout = QFormLayout(dialog)

        entry_nombre = QLineEdit()
        entry_dni = QLineEdit()
        entry_dni.setValidator(QIntValidator(0, 99999999))
        combo_consulta = QComboBox()
        combo_consulta.setFont(QFont("Arial", 12))
        combo_consulta.addItems(["Transferencia", "Retiro", "Trámite", "Préstamo", "Otros"])

        layout.addRow("Nombre:", entry_nombre)
        layout.addRow("DNI:", entry_dni)
        layout.addRow("Consulta:", combo_consulta)

        btn_guardar = QPushButton("Guardar")
        btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #28B463;
                color: white;
                font-size: 14px;
                border-radius: 8px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #1D8348;
            }
        """)
        layout.addRow(btn_guardar)

        def guardar_datos():
            nombre = entry_nombre.text().strip()
            dni = entry_dni.text().strip()
            consulta = combo_consulta.currentText()

            if not nombre or not dni:
                QMessageBox.critical(dialog, "Error", "Por favor, completa todos los campos.")
                return
            if len(dni) != 8:
                QMessageBox.warning(dialog, "Error", "El DNI debe tener exactamente 8 dígitos.")
                return

            tipo = self.tipoCliente
            cliente = self.controlador.recibirCliente(tipo)
            self.controlador.asignarDatosCliente(cliente, {
                "nombre": nombre,
                "dni": dni,
                "consulta": consulta
            })
            self.actualizarEstado()
            dialog.accept()

            QMessageBox.information(
                self,
                "Cliente agregado",
                f"Cliente '{nombre}' con DNI {dni} agregado correctamente."
            )

        btn_guardar.clicked.connect(guardar_datos)
        dialog.exec_()

    def ingresarClientes(self):
        self.controlador.ingresarClientes()
        self.actualizarEstado()

    def atenderClientes(self):
        self.controlador.atenderClientes()
        self.actualizarEstado()

    def finalizarAtencion(self):
        cliente = self.controlador.finalizarAtencion()
        if cliente:
            QMessageBox.information(self, "Cliente Atendido", f"Se ha atendido al cliente: {cliente}")
        else:
            QMessageBox.information(self, "Atención", "No hay clientes siendo atendidos.")
        self.actualizarEstado()

    def actualizarEstado(self):
        estado = self.controlador.estadoBanco()
        self.estado.clear()

        if not isinstance(estado, dict):
            self.estado.setText("Error: el estado del banco no es válido.")
            return

        for nombre_cola, contenido in estado.items():
            self.estado.append(f"{nombre_cola}:\n{contenido}\n")
