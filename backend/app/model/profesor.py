from usuario import Usuario
from typing import Str,Int
class Profesor(Usuario):
    def __init__(self, nombre: Str, apellido: Str, ide: Int, tipo_ide: Str):
        super().__init__(nombre, apellido, ide, tipo_ide)
        self.materias_dict = {}