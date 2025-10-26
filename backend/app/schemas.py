from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Schema para BuzonSugerencias
class BuzonSugerenciasBase(BaseModel):
    id_estudiante: Optional[str] = None
    tipo_documento: Optional[str] = None
    tipo_sugerencia: Optional[str] = None
    asunto: Optional[str] = None
    descripcion: str
    estado: Optional[str] = "Pendiente"

class BuzonSugerenciasCreate(BuzonSugerenciasBase):
    pass

class BuzonSugerenciasResponse(BuzonSugerenciasBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Schemas para Encuesta
class EncuestaBase(BaseModel):
    id_estudiante: str
    facultad: str
    satisfaccion: str 

class EncuestaCreate(EncuestaBase):
    pass

class EncuestaResponse(EncuestaBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Schemas para ChatHistorial
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