from usuario import Usuario
class Estudiante(Usuario):
    def __init__(self, nombre: str = None, apellido: str=None, ide: int=None, tipo_ide: str=None):
        super().__init__(nombre, apellido, ide, tipo_ide)
        self.consultas = []
        self.tareas = []
        self.materias = []
        self.encuestas = []

    def __repr__(self):
        return super().__repr__()
    
    def prioridad_por_materias(self, materia):
        self.materias.append(materia)
        return f"Materia {materia} ha sido agregada"
    
    def enviar_tareas(self, tarea):
        self.tareas.append(tarea)
    
    def recibir_encuesta(self, encuesta):
        self.encuestas.append(encuesta)