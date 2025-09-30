from typing import str,int
class Materia:
    def __init__(self,nombre:str,codigo:str,creditos:int):
        self.nombre = nombre
        self.codigo = codigo
        self.creditos = creditos

    def __repr__(self):
        return f"{self.nombre}, {self.codigo},({self.creditos} créditos"