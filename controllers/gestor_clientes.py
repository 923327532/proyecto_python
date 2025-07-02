from model.cola import Cola
from model.cliente import Cliente
from model.usuario import Usuario
from model import db
import random
import time

class GestorClientes:
    def __init__(self):
        # Colas por tipo de cliente
        self.colaDiscapacitados = Cola(5)
        self.colaVIP = Cola(10)
        self.colaNormales = Cola(20)

        # Zonas internas del banco
        self.zonaEspera = Cola(10)
        self.zonaAtencion = Cola(5)

        # Contador de ID para clientes
        self.contador_id = 1

        # Tickets generados por clientes sin login
        self.tickets = []

    def recibirCliente(self, tipo):
        id_cliente = f"{self.contador_id:03d}"
        self.contador_id += 1
        cliente = Cliente(tipo, id_cliente)

        if tipo == "discapacitado":
            self.colaDiscapacitados.encolar(cliente)
        elif tipo == "vip":
            self.colaVIP.encolar(cliente)
        elif tipo == "normal":
            self.colaNormales.encolar(cliente)
        else:
            print("Tipo de cliente no válido")
            return None
        return cliente

    def asignarDatosCliente(self, cliente, datos):
        conexion = db.conectar()
        cursor = conexion.cursor(dictionary=True)  # para recibir resultados como diccionario

        # Buscar si cliente ya existe por DNI
        cursor.execute("SELECT * FROM clientes WHERE dni = %s", (datos["dni"],))
        resultado = cursor.fetchone()

        if resultado:
            # Cliente existe: actualizar objeto con datos de BD
            cliente.nombre = resultado["nombre"]
            cliente.dni = resultado["dni"]
            cliente.consulta = resultado["consulta"]
            cliente.tipo = resultado["tipo"]
        else:
            # Cliente no existe: insertar nuevo
            cliente.nombre = datos["nombre"]
            cliente.dni = datos["dni"]
            cliente.consulta = datos["consulta"]

            cursor.execute(
                "INSERT INTO clientes (tipo, nombre, dni, consulta) VALUES (%s, %s, %s, %s)",
                (cliente.tipo, cliente.nombre, cliente.dni, cliente.consulta)
            )
            conexion.commit()

        cursor.close()
        conexion.close()

    def ingresarClientes(self):
        while not self.zonaEspera.estaLlena():
            cliente = self._siguientePorPrioridad()
            if cliente:
                self.zonaEspera.encolar(cliente)
            else:
                break

    def atenderClientes(self):
        while not self.zonaAtencion.estaLlena() and not self.zonaEspera.estaVacia():
            cliente = self.zonaEspera.desencolar()
            self.zonaAtencion.encolar(cliente)

    def finalizarAtencion(self):
        return self.zonaAtencion.desencolar()

    def _siguientePorPrioridad(self):
        if not self.colaDiscapacitados.estaVacia():
            return self.colaDiscapacitados.desencolar()
        elif not self.colaVIP.estaVacia():
            return self.colaVIP.desencolar()
        elif not self.colaNormales.estaVacia():
            return self.colaNormales.desencolar()
        else:
            return None

    def estadoBanco(self):
        return {
            "Cola Discapacitados": self.colaDiscapacitados.mostrar(),
            "Cola VIP": self.colaVIP.mostrar(),
            "Cola Normales": self.colaNormales.mostrar(),
            "Zona de Espera (dentro del banco)": self.zonaEspera.mostrar(),
            "Zona de Atención (ventanillas)": self.zonaAtencion.mostrar()
        }

    def generar_ticket(self, dni, tramite):
        if not dni.isdigit() or len(dni) < 6:
            return None
        
        codigo = f"T{random.randint(1000,9999)}"
        ventanilla = random.choice(["A", "B", "C", "D"])
        espera = random.randint(1, 15)  # minutos estimados
        
        ticket = {
            "dni": dni,
            "tramite": tramite,
            "codigo": codigo,
            "ventanilla": ventanilla,
            "espera": espera,
            "hora": time.strftime("%H:%M:%S")
        }
        self.tickets.append(ticket)
        return ticket

