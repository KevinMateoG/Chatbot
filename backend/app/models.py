from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
import sys
from pathlib import Path

backend_path = Path(__file__).resolve().parent
sys.path.append(str(backend_path))
from databaseconfig import base as Base

class Encuesta(Base):
    """Modelo para almacenar encuestas"""
    __tablename__ = "encuesta"
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_estudiante = Column(String(30), index=True)
    facultad = Column(String(20), nullable=True)
    satisfaccion = Column(String(20))
    
    def __repr__(self):
        return f"<Survey(id={self.id}, name={self.name})>"


class HitorialChat(Base):
    """Modelo para almacenar historial de conversaciones"""
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo_documento = Column(String(50), nullable=True)
    numero_documento = Column(String(100), nullable=True)
    mensaje = Column(Text, nullable=False)
    respuesta = Column(Text, nullable=True)
    estado = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ChatHistory(id={self.id}, documento={self.numero_documento})>"


class Estudiante(Base):
    """Modelo para almacenar usuarios"""
    __tablename__ = "estudiante"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(60))
    apellidos = Column(String(60))
    tipo_id = Column(String(20))

    
    def __repr__(self):
        return f"<User(id={self.nombre}, documento={self.tipo_id} {self.id})>"