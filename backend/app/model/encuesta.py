from pathlib import Path
import sys
backend_path = Path(__file__).resolve().parent
sys.path.append(str(backend_path))

from controller.base_datos import BaseDatos

class encuesta:
    def subir_opciones(id_estudiante, repuestas):
        cursor = BaseDatos.obtener_cursor()
        guardar_respuestas = []
        for key, value in repuestas.items():
            guardar_respuestas.append(value)
        subir_encuesta = f"insert into encuesta (id_estudiante, facultad, satisfaccion) values ('{id_estudiante}', '{guardar_respuestas[0]}', '{guardar_respuestas[0]}')"
        cursor.execute(subir_encuesta)

        return "¡Gracias! Tu respuesta ha sido registrada exitosamente."