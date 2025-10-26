from sqlalchemy.orm import Session
import models
import schemas
from typing import List, Optional

# CRUD para Encuesta
def crear_encuesta(db: Session, encuesta: schemas.EncuestaCreate):
    """Crear una nueva encuesta"""
    db_encuesta = models.Encuesta(**encuesta.dict())
    db.add(db_encuesta)
    db.commit()
    db.refresh(db_encuesta)
    return db_encuesta

def leer_encuesta(db: Session, survey_id: int):
    """Obtener una encuesta por ID"""
    return db.query(models.Survey).filter(models.Survey.id == survey_id).first()

# CRUD para BuzonSugerencias
def crear_sugerencia(db: Session, sugerencia: schemas.BuzonSugerenciasCreate):
    """Crear una nueva sugerencia"""
    db_sugerencia = models.BuzonSugerencias(**sugerencia.dict())
    db.add(db_sugerencia)
    db.commit()
    db.refresh(db_sugerencia)
    return db_sugerencia

def obtener_sugerencia(db: Session, sugerencia_id: int):
    """Obtener una sugerencia por ID"""
    return db.query(models.BuzonSugerencias)\
        .filter(models.BuzonSugerencias.id == sugerencia_id)\
        .first()

def obtener_sugerencias_por_estudiante(db: Session, id_estudiante: str):
    """Obtener todas las sugerencias de un estudiante"""
    return db.query(models.BuzonSugerencias)\
        .filter(models.BuzonSugerencias.id_estudiante == id_estudiante)\
        .order_by(models.BuzonSugerencias.created_at.desc())\
        .all()

def obtener_todas_sugerencias(db: Session, skip: int = 0, limit: int = 100):
    """Obtener todas las sugerencias"""
    return db.query(models.BuzonSugerencias)\
        .order_by(models.BuzonSugerencias.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def actualizar_estado_sugerencia(db: Session, sugerencia_id: int, nuevo_estado: str):
    """Actualizar el estado de una sugerencia"""
    sugerencia = obtener_sugerencia(db, sugerencia_id)
    if sugerencia:
        sugerencia.estado = nuevo_estado
        db.commit()
        db.refresh(sugerencia)
    return sugerencia

# CRUD para historial de chat
def crear_historial_chat(db: Session, chat: schemas.ChatHistorialCreate):
    """Guardar historial de chat"""
    db_chat = models.ChatHistory(**chat.dict())
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

# CRUD para User
def crear_estudiante(db: Session, user: schemas.EstudianteCreate):
    """Crear un nuevo usuario"""
    db_user = models.Estudiante(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_documento(db: Session, tipo_documento: str, numero_documento: str):
    """Obtener usuario por documento"""
    return db.query(models.User)\
        .filter(
            models.User.tipo_documento == tipo_documento,
            models.User.numero_documento == numero_documento
        )\
        .first()

def get_user(db: Session, user_id: int):
    """Obtener usuario por ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()

def update_user(db: Session, user_id: int, user_update: schemas.EstudianteUpdate):
    """Actualizar usuario"""
    db_user = get_user(db, user_id)
    if db_user:
        for key, value in user_update.dict(exclude_unset=True).items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Obtener todos los usuarios con paginación"""
    return db.query(models.User).offset(skip).limit(limit).all()