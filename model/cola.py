class Nodo:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None

class Cola:
    def __init__(self, L=10):
        self.frente = None
        self.final = None
        self.L = L
        self.tope = 0

    def estaVacia(self):
        return self.tope == 0

    def estaLlena(self):
        return self.tope == self.L

    def encolar(self, dato):
        if self.estaLlena():
            print("Cola llena")
            return

        nuevo = Nodo(dato)
        if self.estaVacia():
            self.frente = self.final = nuevo
        else:
            self.final.siguiente = nuevo
            self.final = nuevo
        self.tope += 1

    def desencolar(self):
        if self.estaVacia():
            print("Cola vacía")
            return None

        dato = self.frente.dato
        self.frente = self.frente.siguiente
        if self.frente is None:
            self.final = None
        self.tope -= 1
        return dato

    def verPrimero(self):
        if self.estaVacia():
            return None
        return self.frente.dato

    def tamanio(self):
        return self.tope

    def mostrar(self):
        texto = ""
        actual = self.frente
        while actual is not None:
            texto += str(actual.dato) + "\n"
            actual = actual.siguiente
        return texto.strip() if texto else "Vacío"
