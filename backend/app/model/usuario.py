from typing import Str,Int
class Usuario:
    def __init__(self, nombre: Str, apellido: Str, ide: Int, tipo_ide: Str):
        self.nombre = nombre
        self.apellido = apellido
        self.ide = ide
        self.tipo_ide = tipo_ide
    
    def __repr__(self):
        return f"{self.nombre} {self.apellido}, {self.tipo_ide} {self.ide}"