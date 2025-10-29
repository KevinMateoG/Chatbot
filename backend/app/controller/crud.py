from sqlalchemy.orm import Session
from controller import models
import schemas
from typing import List, Optional
from pathlib import Path
from sqlalchemy import text
from controller.base_datos import BaseDatos
import sys

from controller import models
from controller import schemas
"""sys.path.append(str(Path(__file__).resolve().parent))

#import models
import schemas"""

# CRUD para Materia
def crear_materia(db: Session, materia: schemas.MateriaCreate):
    db_materia = models.Materia(**materia.dict())
    db.add(db_materia)
    db.commit()
    db.refresh(db_materia)
    return db_materia

def obtener_materia(db: Session, id_materia: int):
    """Obtener una materia por ID"""
    return db.query(models.Materia)\
        .filter(models.Materia.id_materia == id_materia)\
        .first()

def obtener_todas_materias(db: Session, skip: int = 0, limit: int = 100):
    """Obtener todas las materias"""
    return db.query(models.Materia)\
        .offset(skip)\
        .limit(limit)\
        .all()

# CRUD para Estudiante_Materia (Matrícula)
def crear_estudiante_materia(db: Session, estudiante_materia: schemas.EstudianteMateriaCreate):
    db_estudiante_materia = models.EstudianteMateria(**estudiante_materia.dict())
    db.add(db_estudiante_materia)
    db.commit()
    db.refresh(db_estudiante_materia)
    return db_estudiante_materia

def obtener_materias_estudiante(db: Session, id_estudiante: int):
    """
    Obtener todas las materias de un estudiante con información completa
    """
    return db.query(models.EstudianteMateria, models.Materia)\
        .join(models.Materia)\
        .filter(models.EstudianteMateria.id_estudiante == id_estudiante)\
        .all()

def obtener_materias_estudiante_ordenadas(
    db: Session, 
    id_estudiante: int,
    criterio: str = "creditos",
    orden_desc: bool = True
):
    """
    Obtener materias de un estudiante ordenadas según criterio
    
    Args:
        db: Sesión de base de datos
        id_estudiante: ID del estudiante
        criterio: Campo por el cual ordenar (creditos, semestre, nombre)
        orden_desc: True para descendente, False para ascendente
    """
    query = db.query(models.EstudianteMateria, models.Materia)\
        .join(models.Materia)\
        .filter(models.EstudianteMateria.id_estudiante == id_estudiante)
    
    # Aplicar ordenamiento según criterio
    if criterio == "creditos":
        if orden_desc:
            query = query.order_by(models.Materia.creditos.desc())
        else:
            query = query.order_by(models.Materia.creditos.asc())
    elif criterio == "semestre":
        if orden_desc:
            query = query.order_by(models.Materia.semestre.desc())
        else:
            query = query.order_by(models.Materia.semestre.asc())
    elif criterio == "nombre":
        if orden_desc:
            query = query.order_by(models.Materia.nombre_materia.desc())
        else:
            query = query.order_by(models.Materia.nombre_materia.asc())
    elif criterio == "estado":
        # Ordenar por estado con prioridad personalizada
        from sqlalchemy import case
        estado_orden = case(
            (models.EstudianteMateria.estado == "Cursando", 1),
            (models.EstudianteMateria.estado == "Pendiente", 2),
            (models.EstudianteMateria.estado == "Aprobada", 3),
            (models.EstudianteMateria.estado == "Reprobada", 4),
            else_=5
        )
        query = query.order_by(estado_orden)
    
    return query.all()

def obtener_materias_prioritarias(db: Session, id_estudiante: int, limite: int = 5):
    """
    Obtener las materias más prioritarias para el estudiante
    Ordenadas por: estado (Cursando primero) -> créditos (mayor primero) -> semestre (menor primero)
    """
    from sqlalchemy import case
    
    estado_orden = case(
        (models.EstudianteMateria.estado == "Cursando", 1),
        (models.EstudianteMateria.estado == "Pendiente", 2),
        (models.EstudianteMateria.estado == "Reprobada", 3),
        (models.EstudianteMateria.estado == "Aprobada", 4),
        else_=5
    )
    
    return db.query(models.EstudianteMateria, models.Materia)\
        .join(models.Materia)\
        .filter(models.EstudianteMateria.id_estudiante == id_estudiante)\
        .order_by(
            estado_orden,
            models.Materia.creditos.desc(),
            models.Materia.semestre.asc()
        )\
        .limit(limite)\
        .all()

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

def get_usuario_por_documento(db: Session, tipo_id: str, id: str):
    """Obtener usuario por documento"""
    return db.query(models.Usuario).filter(
        models.Usuario.tipo_id == tipo_id,
        models.Usuario.id == id
    ).first()


def obtener_link_hoja(profesor_id: int):
    """
    Retorna el link de la hoja de calificaciones del profesor según su ID.
    """
    db = BaseDatos.get_session()
    try:
        consulta = text("SELECT link_hoja FROM profesores WHERE id = :id")
        result = db.execute(consulta, {"id": profesor_id})
        row = result.fetchone()
        if row and row[0]:
            return row[0]
        return None  # Si no hay link asignado
    finally:
        db.close()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Obtener todos los usuarios con paginación"""
    return db.query(models.User).offset(skip).limit(limit).all()

def get_usuario_por_documento(db: Session, tipo_id: str, id: str):
    """Obtener usuario por documento"""
    return db.query(models.Usuario).filter(
        models.Usuario.tipo_id == tipo_id,
        models.Usuario.id == id
    ).first()