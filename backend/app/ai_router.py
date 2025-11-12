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
    """Obtiene información completa y real de la base de datos para el contexto de la IA."""
    contexto = []
    
    try:
        # ============ INFORMACIÓN DEL USUARIO ============
        if identificacion:
            # Buscar primero como estudiante
            estudiante = db.query(models.Estudiante).filter(
                models.Estudiante.identificacion == identificacion
            ).first()
            
            if estudiante:
                contexto.append("=" * 50)
                contexto.append("INFORMACIÓN DEL ESTUDIANTE")
                contexto.append("=" * 50)
                contexto.append(f"Nombre completo: {estudiante.nombre} {estudiante.apellido}")
                contexto.append(f"Identificación: {estudiante.identificacion}")
                contexto.append(f"Correo: {estudiante.correo}")
                contexto.append(f"Programa académico: {estudiante.programa}")
                contexto.append(f"Semestre actual: {estudiante.semestre}")
                contexto.append(f"Estado: {estudiante.estado}")
                
                # Materias matriculadas con todos los detalles
                materias = db.query(models.EstudianteMateria, models.Materia).join(
                    models.Materia, models.EstudianteMateria.id_materia == models.Materia.id
                ).filter(
                    models.EstudianteMateria.id_estudiante == estudiante.id
                ).all()
                
                if materias:
                    contexto.append(f"\nMATERIAS MATRICULADAS ({len(materias)} materias):")
                    total_creditos = 0
                    for est_mat, mat in materias:
                        estado_materia = est_mat.estado if hasattr(est_mat, 'estado') else 'Cursando'
                        contexto.append(f"  • {mat.nombre}")
                        contexto.append(f"    - Créditos: {mat.creditos}")
                        contexto.append(f"    - Calificación: {est_mat.calificacion if est_mat.calificacion else 'Pendiente'}")
                        contexto.append(f"    - Estado: {estado_materia}")
                        if hasattr(mat, 'profesor'):
                            contexto.append(f"    - Profesor: {mat.profesor}")
                        total_creditos += mat.creditos
                    contexto.append(f"\nTotal de créditos matriculados: {total_creditos}")
                contexto.append("")
            
            # Si no es estudiante, buscar como profesor
            if not estudiante:
                profesor = db.query(models.Profesor).filter(
                    models.Profesor.identificacion == identificacion
                ).first()
                
                if profesor:
                    contexto.append("=" * 50)
                    contexto.append("INFORMACIÓN DEL PROFESOR")
                    contexto.append("=" * 50)
                    contexto.append(f"Nombre completo: {profesor.nombre} {profesor.apellido}")
                    contexto.append(f"Identificación: {profesor.identificacion}")
                    contexto.append(f"Correo: {profesor.correo}")
                    contexto.append(f"Departamento: {profesor.departamento}")
                    
                    # Materias que enseña
                    materias_profesor = db.query(models.Materia).filter(
                        models.Materia.profesor_id == profesor.id
                    ).all()
                    
                    if materias_profesor:
                        contexto.append(f"\nMATERIAS QUE ENSEÑA ({len(materias_profesor)}):")
                        for mat in materias_profesor:
                            contexto.append(f"  • {mat.nombre} ({mat.creditos} créditos)")
                    contexto.append("")
        
        # ============ TODAS LAS MATERIAS DISPONIBLES ============
        todas_materias = db.query(models.Materia).limit(20).all()
        if todas_materias:
            contexto.append("=" * 50)
            contexto.append(f"MATERIAS DISPONIBLES EN LA UNIVERSIDAD ({len(todas_materias)} primeras):")
            contexto.append("=" * 50)
            for mat in todas_materias:
                contexto.append(f"  • {mat.nombre} - {mat.creditos} créditos")
            contexto.append("")
        
        # ============ NOTICIAS Y EVENTOS ============
        noticias = db.query(models.Noticia).order_by(models.Noticia.fecha.desc()).limit(5).all()
        if noticias:
            contexto.append("=" * 50)
            contexto.append("NOTICIAS RECIENTES DE LA UNIVERSIDAD:")
            contexto.append("=" * 50)
            for noticia in noticias:
                contexto.append(f"📰 {noticia.titulo}")
                contexto.append(f"   Fecha: {noticia.fecha}")
                contexto.append(f"   {noticia.contenido[:200]}...")
                contexto.append("")
        
        # ============ GRUPOS ESTUDIANTILES ============
        grupos = db.query(models.GrupoEstudiantil).limit(10).all()
        if grupos:
            contexto.append("=" * 50)
            contexto.append("GRUPOS ESTUDIANTILES ACTIVOS:")
            contexto.append("=" * 50)
            for grupo in grupos:
                contexto.append(f"👥 {grupo.nombre}")
                contexto.append(f"   {grupo.descripcion}")
                contexto.append("")
        
        # ============ PROFESORES DISPONIBLES ============
        profesores = db.query(models.Profesor).limit(10).all()
        if profesores:
            contexto.append("=" * 50)
            contexto.append("PROFESORES DE LA UNIVERSIDAD:")
            contexto.append("=" * 50)
            for prof in profesores:
                contexto.append(f"👨‍🏫 {prof.nombre} {prof.apellido}")
                contexto.append(f"   Departamento: {prof.departamento}")
                contexto.append(f"   Correo: {prof.correo}")
                contexto.append("")
                
    except Exception as e:
        logger.warning(f"Error obteniendo contexto de BD: {e}")
    
    return "\n".join(contexto) if contexto else None


def _construir_prompt_con_contexto(prompt_usuario: str, contexto_json: dict = None, contexto_bd: str = None):
    """Construye un prompt enriquecido con el contexto del sistema."""
    
    partes = [
        "="*70,
        "ASISTENTE VIRTUAL INTELIGENTE - UNIVERSIDAD DE MEDELLÍN",
        "="*70,
        "",
        "Eres un asistente virtual avanzado de la Universidad de Medellín (UdeM).",
        "",
        "TU MISIÓN:",
        "- Ayudar a estudiantes y profesores con información precisa y personalizada",
        "- Responder preguntas sobre materias, calificaciones, profesores, eventos",
        "- Guiar en trámites administrativos y procesos académicos",
        "- Ser amigable, profesional y usar un tono conversacional",
        "",
        "CAPACIDADES:",
        "✓ Acceso COMPLETO a la base de datos de la universidad",
        "✓ Información en TIEMPO REAL de estudiantes, profesores, materias, noticias",
        "✓ Puedes llamar al usuario por su NOMBRE si está identificado",
        "✓ Puedes hacer cálculos (promedios, créditos, etc.)",
        "",
        "REGLAS IMPORTANTES:",
        "1. Si el usuario está identificado, dirígete a él por su NOMBRE",
        "2. Si preguntan por materias/notas, usa la información REAL de la BD",
        "3. Si preguntan por profesores, usa los datos REALES",
        "4. Si no tienes la info exacta, sugiere contactar a la universidad",
        "5. SIEMPRE responde en español de forma clara y concisa",
        "6. Si hay múltiples opciones, preséntalas en formato de lista",
        "7. Incluye emojis relevantes para hacer la conversación más amigable 😊",
        "",
        "⚠️ REGLA CRÍTICA SOBRE ENLACES:",
        "- Cuando una respuesta incluya una URL, DEBES mostrar el enlace COMPLETO",
        "- NO digas 'haz clic aquí' sin el enlace",
        "- Formato correcto: 'Accede aquí: https://ejemplo.com/url-completa'",
        "- Las URLs pueden ser largas, NO LAS ACORTES",
        "- Siempre verifica en las OPCIONES Y SERVICIOS si hay enlaces disponibles",
        "",
    ]
    
    # Agregar contexto de BD si existe
    if contexto_bd:
        partes.append("="*70)
        partes.append("📊 INFORMACIÓN DE LA BASE DE DATOS (TIEMPO REAL):")
        partes.append("="*70)
        partes.append(contexto_bd)
        partes.append("")
    
    # Agregar contexto del JSON si existe
    if contexto_json:
        partes.append("="*70)
        partes.append("📋 OPCIONES, SERVICIOS Y ENLACES DISPONIBLES:")
        partes.append("="*70)
        
        # Extraer información completa del JSON incluyendo resultados y URLs
        if "opciones" in contexto_json:
            for key, opcion in contexto_json["opciones"].items():
                partes.append(f"\n{key}. {opcion.get('texto', '')}")
                
                # Si tiene sub-opciones
                if "opciones" in opcion:
                    for sub_key, sub_opcion in opcion["opciones"].items():
                        partes.append(f"   {key}.{sub_key}. {sub_opcion.get('texto', '')}")
                        
                        # IMPORTANTE: Incluir el resultado con URLs
                        if "resultado" in sub_opcion:
                            resultado = sub_opcion["resultado"]
                            partes.append(f"      → Resultado: {resultado}")
                
                # Si tiene resultado directo (sin sub-opciones)
                elif "resultado" in opcion:
                    partes.append(f"   → Resultado: {opcion['resultado']}")
        
        partes.append("")
        partes.append("🔗 INSTRUCCIONES SOBRE ENLACES:")
        partes.append("- Cuando respondas con URLs, SIEMPRE muestra el enlace completo")
        partes.append("- Usa el formato: 'Puedes acceder aquí: [URL completa]'")
        partes.append("- NO acortes ni omitas las URLs")
        partes.append("- Si el resultado contiene un enlace, INCLÚYELO en tu respuesta")
        partes.append("")
    
    # Agregar pregunta del usuario
    partes.append("="*70)
    partes.append("💬 PREGUNTA DEL USUARIO:")
    partes.append("="*70)
    partes.append(prompt_usuario)
    partes.append("")
    partes.append("="*70)
    partes.append("📝 TU RESPUESTA (clara, precisa y amigable):")
    partes.append("="*70)
    
    return "\n".join(partes)


@router.get("/verificar_identificacion/{identificacion}")
async def verificar_identificacion(identificacion: str, db: Session = Depends(get_db)):
    """Verifica la identificación y retorna el nombre del usuario."""
    try:
        # Buscar como estudiante
        estudiante = db.query(models.Estudiante).filter(
            models.Estudiante.id == identificacion
        ).first()
        
        if estudiante:
            return {
                "encontrado": True,
                "tipo": "estudiante",
                "nombre": f"{estudiante.nombre} {estudiante.apellidos}",
                "identificacion": identificacion
            }
        
        # Buscar como usuario general
        usuario = db.query(models.Usuario).filter(
            models.Usuario.id == identificacion
        ).first()
        
        if usuario:
            return {
                "encontrado": True,
                "tipo": usuario.rol,
                "nombre": f"{usuario.nombre} {usuario.apellidos}",
                "identificacion": identificacion
            }
        
        # No encontrado
        return {
            "encontrado": False,
            "mensaje": "Identificación no encontrada en el sistema"
        }
        
    except Exception as e:
        logger.error(f"Error verificando identificación: {e}")
        raise HTTPException(status_code=500, detail=f"Error al verificar identificación: {str(e)}")


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
