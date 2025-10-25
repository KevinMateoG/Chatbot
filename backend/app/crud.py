from sqlalchemy.orm import Session
import models
import schemas
from typing import List, Optional

# CRUD para Encuesta
def crear_encuesta(db: Session, survey: schemas.EncuestaCreate):
    """Crear una nueva encuesta"""
    db_encuesta = models.Encuesta(**survey.dict())
    db.add(db_encuesta)
    db.commit()
    db.refresh(db_encuesta)
    return db_encuesta

def leer_encuesta(db: Session, survey_id: int):
    """Obtener una encuesta por ID"""
    return db.query(models.Survey).filter(models.Survey.id == survey_id).first()


# CRUD para histotial de chat
def crear_historial_chat(db: Session, chat: schemas.ChatHistorialCreate):
    """Guardar historial de chat"""
    db_chat = models.HitorialChat(**chat.dict())
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