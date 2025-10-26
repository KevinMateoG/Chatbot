from sqlalchemy.orm import Session
from sqlalchemy import text
import sys
from pathlib import Path

# Agregar el directorio raíz del backend al PATH
backend_path = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(backend_path))

# Importar la configuración de base de datos
sys.path.append(str(Path(__file__).resolve().parent.parent))
from databaseconfig import session_local, engine

class BaseDatos:

    @staticmethod
    def get_session() -> Session:
        """Obtener una sesión de SQLAlchemy"""
        return session_local()

    @staticmethod
    def buscar_id(id):
        """Buscar estudiante por ID"""
        db = BaseDatos.get_session()
        try:
            # Usando SQL directo con SQLAlchemy
            consulta = text("SELECT nombre FROM estudiante WHERE id LIKE :id")
            result = db.execute(consulta, {"id": f"{id}"})
            resultado = result.fetchone()
            return resultado
        finally:
            db.close()

    @staticmethod
    def ejecutar_consulta(query: str, params: dict = None):
        """
        Ejecutar una consulta SQL directa
        
        Args:
            query: Consulta SQL (usar :param para parámetros)
            params: Diccionario con los parámetros
        
        Returns:
            Resultados de la consulta
        """
        db = BaseDatos.get_session()
        try:
            consulta = text(query)
            if params:
                result = db.execute(consulta, params)
            else:
                result = db.execute(consulta)
            db.commit()
            return result.fetchall()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @staticmethod
    def ejecutar_insert(query: str, params: dict = None):
        """
        Ejecutar un INSERT/UPDATE/DELETE
        
        Args:
            query: Consulta SQL
            params: Diccionario con los parámetros
        
        Returns:
            True si se ejecutó correctamente
        """
        db = BaseDatos.get_session()
        try:
            consulta = text(query)
            if params:
                db.execute(consulta, params)
            else:
                db.execute(consulta)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()