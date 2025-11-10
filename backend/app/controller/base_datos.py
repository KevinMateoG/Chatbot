from sqlalchemy.orm import Session
from sqlalchemy import text
import sys
from pathlib import Path

# Importar la configuración de base de datos
#sys.path.append(str(Path(__file__).resolve().parent.parent))
from .databaseconfig import session_local, engine


class BaseDatos:

    @staticmethod
    def get_session() -> Session:
        """Obtener una sesión de SQLAlchemy"""
        return session_local()

    @staticmethod
    def buscar_id(id: int):
        """Buscar estudiante por ID"""
        db = BaseDatos.get_session()
        try:
            # Buscar en usuarios, sigue igual
            consulta = text("SELECT nombre FROM usuarios WHERE id = :id")
            result = db.execute(consulta, {"id": id})
            resultado = result.fetchone()
            if resultado:
                return resultado
            return None
        finally:
            db.close()

    @staticmethod
    def buscar_materias_de_estudiante(id: int):
        """Buscar todas las materias de un estudiante"""
        db = BaseDatos.get_session()
        try:
            # Cambié 'like' por '=' y aseguré que el tipo sea integer
            consulta = text("SELECT id_materia FROM estudiante_materias WHERE id_estudiante = :id")
            result = db.execute(consulta, {"id": id})
            resultado = result.fetchall()
            return resultado
        finally:
            db.close()

    @staticmethod
    def buscar_materias_por_id(id_materia: int):
        """Buscar información de una materia por su ID"""
        db = BaseDatos.get_session()
        try:
            consulta = text("SELECT id_materia, nombre_materia, creditos FROM materias WHERE id_materia = :id")
            result = db.execute(consulta, {"id": id_materia})
            resultado = result.fetchall()
            return resultado
        finally:
            db.close()

    @staticmethod
    def ejecutar_consulta(query: str, params: dict = None):
        """Ejecutar cualquier consulta SQL"""
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
        """Ejecutar un INSERT/UPDATE/DELETE"""
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

    @staticmethod
    def obtener_link_hoja(id: int) -> str | None:
        """Retorna el link de la hoja de calificaciones para un usuario"""
        session = BaseDatos.get_session()
        try:
            resultado = session.execute(
                text("SELECT link_hoja FROM profesores WHERE id = :id"),
                {"id": id}
            ).fetchone()
            if resultado:
                return resultado[0]
            return None
        finally:
            session.close()
