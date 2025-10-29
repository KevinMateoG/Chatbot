from fastapi import APIRouter, Body, HTTPException, Depends
import os
import logging
import json
from typing import Optional
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from controller.databaseconfig import get_db
from controller import models
from pydantic import BaseModel, Field

# Cargar variables de entorno desde .env
load_dotenv()

router = APIRouter(prefix="/ai", tags=["ai"])
logger = logging.getLogger(__name__)


# Modelo Pydantic para el request
class AIGenerateRequest(BaseModel):
    prompt: str = Field(..., description="Texto del prompt")
    model: Optional[str] = Field(None, description="Modelo a usar (opcional)")
    max_tokens: int = Field(512, description="Máximo de tokens en la respuesta")
    temperature: float = Field(0.7, description="Temperatura (0.0-2.0)")
    identificacion: Optional[str] = Field(None, description="Identificación del estudiante para contexto personalizado")
    usar_contexto: bool = Field(True, description="Si usar el contexto del sistema (JSON + BD)")

# Configuración de Groq con API Key (ahora desde variable de entorno)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Modelos disponibles en Groq (ordenados por velocidad/calidad)
AVAILABLE_MODELS = [
    "llama-3.3-70b-versatile",    # Más nuevo y potente (recomendado)
    "llama-3.1-70b-versatile",    # Muy bueno, rápido
    "mixtral-8x7b-32768",         # Excelente para español
    "llama-3.1-8b-instant",       # Ultra rápido
]


def _get_groq_client():
    """Obtiene el cliente de Groq configurado con API key."""
    if not GROQ_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY no configurada. Obtén una en https://console.groq.com/ y configúrala como variable de entorno."
        )
    
    try:
        from groq import Groq
        return Groq(api_key=GROQ_API_KEY)
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="Paquete 'groq' no instalado. Ejecuta: pip install groq"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error configurando Groq: {e}")


def _cargar_contexto_json():
    """Carga el archivo opciones.json para usar como contexto."""
    try:
        ruta_opciones = os.path.join(os.path.dirname(__file__), "opciones.json")
        with open(ruta_opciones, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"No se pudo cargar opciones.json: {e}")
        return None


def _obtener_contexto_bd(db: Session, identificacion: str = None):
    """Obtiene información relevante de la base de datos para el contexto de la IA."""
    contexto = []
    
    try:
        # Si hay identificación, buscar datos del estudiante
        if identificacion:
            estudiante = db.query(models.Estudiante).filter(
                models.Estudiante.identificacion == identificacion
            ).first()
            
            if estudiante:
                contexto.append(f"Estudiante: {estudiante.nombre} {estudiante.apellido}")
                contexto.append(f"Programa: {estudiante.programa}")
                contexto.append(f"Semestre: {estudiante.semestre}")
                
                # Obtener materias del estudiante
                materias = db.query(models.EstudianteMateria, models.Materia).join(
                    models.Materia, models.EstudianteMateria.id_materia == models.Materia.id
                ).filter(
                    models.EstudianteMateria.id_estudiante == estudiante.id
                ).all()
                
                if materias:
                    contexto.append("\nMaterias matriculadas:")
                    for est_mat, mat in materias:
                        contexto.append(f"- {mat.nombre} ({mat.creditos} créditos, Nota: {est_mat.calificacion or 'N/A'})")
        
        # Obtener noticias recientes (últimas 3)
        noticias = db.query(models.Noticia).order_by(models.Noticia.fecha.desc()).limit(3).all()
        if noticias:
            contexto.append("\nNoticias recientes de la universidad:")
            for noticia in noticias:
                contexto.append(f"- {noticia.titulo}: {noticia.contenido[:100]}...")
        
        # Obtener grupos estudiantiles
        grupos = db.query(models.GrupoEstudiantil).limit(5).all()
        if grupos:
            contexto.append("\nGrupos estudiantiles disponibles:")
            for grupo in grupos:
                contexto.append(f"- {grupo.nombre}: {grupo.descripcion}")
                
    except Exception as e:
        logger.warning(f"Error obteniendo contexto de BD: {e}")
    
    return "\n".join(contexto) if contexto else None


def _construir_prompt_con_contexto(prompt_usuario: str, contexto_json: dict = None, contexto_bd: str = None):
    """Construye un prompt enriquecido con el contexto del sistema."""
    
    partes = [
        "Eres un asistente virtual de la Universidad de Medellín. Tu objetivo es ayudar a estudiantes con información precisa y útil.",
        ""
    ]
    
    # Agregar contexto del JSON si existe
    if contexto_json:
        partes.append("INFORMACIÓN DEL SISTEMA:")
        partes.append("Las opciones disponibles en el chatbot son:")
        
        # Extraer información relevante del JSON
        if "opciones" in contexto_json:
            for key, opcion in contexto_json["opciones"].items():
                partes.append(f"{key}. {opcion.get('texto', '')}")
                if "opciones" in opcion:
                    for sub_key, sub_opcion in opcion["opciones"].items():
                        partes.append(f"  {key}.{sub_key}. {sub_opcion.get('texto', '')}")
        
        partes.append("")
    
    # Agregar contexto de BD si existe
    if contexto_bd:
        partes.append("INFORMACIÓN DEL ESTUDIANTE Y LA UNIVERSIDAD:")
        partes.append(contexto_bd)
        partes.append("")
    
    # Agregar pregunta del usuario
    partes.append("PREGUNTA DEL ESTUDIANTE:")
    partes.append(prompt_usuario)
    partes.append("")
    partes.append("Responde de forma clara, precisa y amigable en español. Si la información no está en el contexto, indica que el estudiante puede consultar directamente con la universidad.")
    
    return "\n".join(partes)


@router.post("/generate")
async def generate_ai(
    request: AIGenerateRequest,
    db: Session = Depends(get_db)
):
    """Genera texto usando Groq (LLaMA/Mixtral) con contexto del sistema.
    
    La IA puede usar:
    - Opciones del chatbot (opciones.json)
    - Información del estudiante de la BD (si se proporciona identificación)
    - Noticias, grupos estudiantiles, etc.
    
    Ejemplo de uso:
    ```json
    {
        "prompt": "¿Qué materias tengo matriculadas?",
        "identificacion": "1234567890",
        "max_tokens": 256
    }
    ```
    """
    if not request.prompt or not request.prompt.strip():
        raise HTTPException(status_code=400, detail="El prompt no puede estar vacío")

    client = _get_groq_client()
    
    # Construir prompt con contexto si está habilitado
    prompt_final = request.prompt
    if request.usar_contexto:
        contexto_json = _cargar_contexto_json()
        contexto_bd = _obtener_contexto_bd(db, request.identificacion) if request.identificacion else None
        prompt_final = _construir_prompt_con_contexto(request.prompt, contexto_json, contexto_bd)
        logger.info(f"Prompt con contexto construido (longitud: {len(prompt_final)} caracteres)")
    
    # Determinar qué modelo usar
    models_to_try = [request.model] if request.model else AVAILABLE_MODELS
    
    last_error = None
    for model_name in models_to_try:
        try:
            logger.info(f"Intentando generar con modelo: {model_name}")
            
            # Llamar a Groq API (compatible con OpenAI)
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "user", "content": prompt_final}
                ],
                max_tokens=request.max_tokens,
                temperature=request.temperature,
            )
            
            # Extraer respuesta
            text = response.choices[0].message.content
            
            return {
                "text": text,
                "model": model_name,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
                "finish_reason": response.choices[0].finish_reason,
                "contexto_usado": request.usar_contexto
            }
                
        except Exception as e:
            error_msg = str(e)
            logger.warning(f"Fallo con modelo {model_name}: {error_msg}")
            last_error = error_msg
            
            # Si es un error de modelo no encontrado, probar el siguiente
            if "model" in error_msg.lower() and "not found" in error_msg.lower():
                continue
            else:
                # Otros errores (rate limit, auth, etc.) no reintentar
                raise HTTPException(status_code=500, detail=f"Error al generar con {model_name}: {error_msg}")
    
    # Si llegamos aquí, ningún modelo funcionó
    raise HTTPException(
        status_code=502,
        detail=f"No se pudo generar contenido con ningún modelo disponible. Último error: {last_error}"
    )


@router.get("/models")
async def list_models():
    """Lista los modelos disponibles de Groq."""
    return {
        "models": [
            {
                "name": "llama-3.3-70b-versatile",
                "description": "LLaMA 3.3 70B - Más nuevo y potente, excelente para español",
                "context_window": 32768
            },
            {
                "name": "llama-3.1-70b-versatile", 
                "description": "LLaMA 3.1 70B - Muy bueno, equilibrio perfecto",
                "context_window": 131072
            },
            {
                "name": "mixtral-8x7b-32768",
                "description": "Mixtral 8x7B - Excelente para español y multilingüe",
                "context_window": 32768
            },
            {
                "name": "llama-3.1-8b-instant",
                "description": "LLaMA 3.1 8B - Ultra rápido para respuestas simples",
                "context_window": 131072
            }
        ],
        "count": 4,
        "provider": "Groq"
    }
