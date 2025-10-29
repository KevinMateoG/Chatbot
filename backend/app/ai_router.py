from fastapi import APIRouter, Body, HTTPException
import os
import logging
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

router = APIRouter(prefix="/ai", tags=["ai"])
logger = logging.getLogger(__name__)

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


@router.post("/generate")
async def generate_ai(
    prompt: str = Body(..., description="Texto del prompt"),
    model: str | None = Body(None, description="Modelo a usar (opcional)"),
    max_tokens: int | None = Body(512, description="Máximo de tokens en la respuesta"),
    temperature: float | None = Body(0.7, description="Temperatura (0.0-2.0)")
):
    """Genera texto usando Groq (LLaMA/Mixtral).
    
    Ejemplo de uso:
    ```json
    {
        "prompt": "Escribe una frase motivacional en español",
        "max_tokens": 128
    }
    ```
    """
    if not prompt or not prompt.strip():
        raise HTTPException(status_code=400, detail="El prompt no puede estar vacío")

    client = _get_groq_client()
    
    # Determinar qué modelo usar
    models_to_try = [model] if model else AVAILABLE_MODELS
    
    last_error = None
    for model_name in models_to_try:
        try:
            logger.info(f"Intentando generar con modelo: {model_name}")
            
            # Llamar a Groq API (compatible con OpenAI)
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
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
