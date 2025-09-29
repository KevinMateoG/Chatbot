
class Usuario:
    def __init__(self, nombre: str, apellido: str, ide: int, tipo_ide: str):
        self.nombre = nombre
        self.apellido = apellido
        self.ide = ide
        self.tipo_ide = tipo_ide
    
    def __repr__(self):
        return f"{self.nombre} {self.apellido}, {self.tipo_ide} {self.ide}"