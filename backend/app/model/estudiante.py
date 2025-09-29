from materias import Materias
from usuario import Usuario
from typing import Str,Int
class Estudiante(Usuario):
    def __init__(self, nombre: Str, apellido: Str, ide: Int, tipo_ide: Str):
        super().__init__(nombre, apellido, ide, tipo_ide)
        self.consultas = []
        self.tareas = []
        self.materias = []
        self.encuestas = []

    def __repr__(self):
        return super().__repr__()
    
    def prioridad_por_materias(self, materia: Materias):
        self.materias.append(materia)
        return f"Materia {materia} ha sido agregada"
    
    def enviar_tareas(self, tarea):
        self.tareas.append(tarea)
    
    def recibir_encuesta(self, encuesta):
        self.encuestas.append(encuesta)