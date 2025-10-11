class Materia:
    def __init__(self,nombre:str,codigo:str,creditos:int):
        self.nombre = nombre
        self.codigo = codigo
        self.creditos = creditos

    def __repr__(self):
        return f"{self.nombre}, {self.codigo},({self.creditos} créditos"
    
    def prioridad (self):
        if self.creditos >= 4:
            return 'Alta'
        elif 2 <= self.creditos < 4:
            return 'Media'
        else:
            return 'Baja'
        
materia_procesadas = []

materia_sin = [
     
    Materia("Calculo integral","calc123", 4),
    Materia("Codigo Limpio","limp123", 1),
    Materia("Estructuras","estru123", 3),
    Materia("Física","fisi123", 5)
    ]

for i in materia_sin:
    procesados = i.prioridad()
    materia_procesadas.append((i.nombre,i.codigo,procesados))
    
print('Lista de prioridad de materias:')
for nombre, codigo, prioridad in materia_procesadas: 
    print(f"- {nombre} ({codigo}): prioridad {prioridad}")

    