from pathlib import Path
import sys
from sqlalchemy import text

backend_path = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_path))

from controller.base_datos import BaseDatos
import crud
import schemas

class BuzonSugerencias:
    @staticmethod
    def procesar_sugerencia(id_estudiante: str, datos_sugerencia: dict):
        """
        Procesar y guardar una sugerencia en la base de datos
        """
        db = BaseDatos.get_session()
        try:
            # Crear el schema de sugerencia
            nueva_sugerencia = schemas.BuzonSugerenciasCreate(
                id_estudiante=id_estudiante,
                tipo_documento=datos_sugerencia.get("tipo_documento"),
                tipo_sugerencia=datos_sugerencia.get("tipo_sugerencia"),
                asunto=datos_sugerencia.get("asunto"),
                descripcion=datos_sugerencia.get("descripcion", ""),
                estado="Pendiente"
            )
            
            # Guardar usando CRUD
            sugerencia_guardada = crud.crear_sugerencia(db, nueva_sugerencia)
            
            return f"¡Gracias! Tu sugerencia ha sido registrada con el ID: {sugerencia_guardada.id}. Será revisada a la brevedad."
        
        except Exception as e:
            db.rollback()
            print(f"Error al guardar sugerencia: {e}")
            import traceback
            traceback.print_exc()
            return "Error al procesar tu sugerencia. Por favor, intenta nuevamente."
        
        finally:
            db.close()