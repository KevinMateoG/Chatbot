from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Schemas para Survey
class EncuestaBase(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    answer1: Optional[str] = None
    answer2: Optional[str] = None
    answer3: Optional[str] = None

class EncuestaCreate(EncuestaBase):
    pass

class EncuestaResponse(EncuestaBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Schemas para ChatHistory
class ChatHistorialBase(BaseModel):
    tipo_documento: Optional[str] = None
    numero_documento: Optional[str] = None
    mensaje: str
    respuesta: Optional[str] = None
    estado: Optional[str] = None

class ChatHistorialCreate(ChatHistorialBase):
    pass

class ChatHistorailResponse(ChatHistorialBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Schemas para User
class EstudianteBase(BaseModel):
    tipo_documento: str
    numero_documento: str
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None

class EstudianteCreate(EstudianteBase):
    pass

class EstudianteUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

class EstudianteResponse(EstudianteBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True