from pathlib import Path
import sys
from sqlalchemy import text

backend_path = Path(__file__).resolve().parent
sys.path.append(str(backend_path))

from controller.base_datos import BaseDatos

class encuesta:
    @staticmethod
    def subir_opciones(id_estudiante, respuestas):
        """
        Guardar respuestas de encuesta en la base de datos
        
        Args:
            id_estudiante: ID del estudiante
            respuestas: Diccionario con las respuestas
        
        Returns:
            Mensaje de confirmación
        """
        db = BaseDatos.get_session()
        try:
            guardar_respuestas = []
            for key, value in respuestas.items():
                guardar_respuestas.append(value)
            
            # Usar text() para consultas SQL textuales en SQLAlchemy
            # Y usar parámetros para prevenir SQL injection
            subir_encuesta = text(
                "INSERT INTO encuesta (id_estudiante, facultad, satisfaccion) "
                "VALUES (:id_estudiante, :facultad, :satisfaccion)"
            )
            
            db.execute(subir_encuesta, {
                "id_estudiante": id_estudiante,
                "facultad": guardar_respuestas[0] if len(guardar_respuestas) > 0 else None,
                "satisfaccion": guardar_respuestas[1] if len(guardar_respuestas) > 1 else None
            })
            
            db.commit()
            return "¡Gracias! Tu respuesta ha sido registrada exitosamente."
        
        except Exception as e:
            db.rollback()
            print(f"Error al guardar encuesta: {e}")
            return f"Error al guardar la encuesta: {str(e)}"
        
        finally:
            db.close()