from typing import Str,Int
class Materias:
    def __init__(self,nombre:Str,codigo:Str,creditos:Int):
        self.nombre = nombre
        self.codigo = codigo
        self.creditos = creditos

    def __repr__(self):
        return f"{self.nombre}, {self.codigo},({self.creditos} créditos)"