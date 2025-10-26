from pydantic import BaseModel
from pathlib import Path
import sys
from sqlalchemy import text
from abc import ABC

ruta = Path(__file__).resolve().parent.parent
sys.path.append(str(ruta))
import schemas
from controller.base_datos import BaseDatos

class Materia(ABC):
    id_materia = None
    nombre_materia = None
    creditos = None

    def crear_materias(id):
        materias_de_estudiante = []
        buscar_materias = BaseDatos.buscar_materias_de_estudiante(id)
        for materia in buscar_materias:
            materia_completa = BaseDatos.buscar_materias_por_id(materia[0])

            objecto_materia = Materia()
            objecto_materia.id_materia = materia_completa[0][0]
            objecto_materia.nombre_materia = materia_completa[0][1]
            objecto_materia.creditos = materia_completa[0][2]
            
            materias_de_estudiante.append(objecto_materia)
        return materias_de_estudiante


    def prioridad (materia):
        if materia.creditos >= 4:
            return 'Alta'
        elif 2 <= materia.creditos < 4:
            return 'Media'
        else:
            return 'Baja'

    def ordenar_matrias(id):
        mensaje:dict[Materia,str] = {}
        materias_priorizadas = sorted(Materia.crear_materias(id),key=lambda Materia: Materia.creditos, reverse=True)
        for i in materias_priorizadas:
            mensaje[i] = Materia.prioridad(i)
        return mensaje
    