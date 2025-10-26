from usuario import Usuario
from typing import Str,Int,Dict,Any
class Profesor(Usuario):
    def __init__(self, nombre: Str, apellido: Str, ide: Int, tipo_ide: Str):
        super().__init__(nombre, apellido, ide, tipo_ide)
        self.materias_dict:Dict [str,Any] = {}
        self.link_hoja = "https://app.udem.edu.co/ServiciosEnLinea/login.html"
    
    def hoja_calculo (self):
        return f"para calificar al profesor {self.nombre} {self.apellido}, por favor ingresa al link {self.link_hoja}"
        pass