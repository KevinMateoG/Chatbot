from fastapi import FastAPI,FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from model.chat_bot import *
from sqlalchemy.orm import Session
from typing import List
from controller import models, schemas, crud
from controller.databaseconfig import engine, get_db
from pathlib import Path
from ai_router import router as ai_router



models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar el router de IA
app.include_router(ai_router)

with open('opciones.json', encoding='utf-8') as f:
    OPCIONES = json.load(f)

class MensajeRequest(BaseModel):
    mensaje: str
    estado: str
    identificacion: dict
    nodo_actual: dict | None

@app.get("/opciones")
async def get_opciones():
    return OPCIONES

@app.post("/procesar_mensaje")
async def procesar_mensaje(request: MensajeRequest, db: Session = Depends(get_db)):
    respuesta = ChatBot(request, OPCIONES).respuesta()
    # Determinar conjunto de opciones según identificacion + rol en DB
    identificacion = request.identificacion if isinstance(request.identificacion, dict) else {}
    opciones_a_usar = OPCIONES
    try:
        tipo = identificacion.get("tipo")
        numero = identificacion.get("numero")
        if tipo and numero:
            usuario = crud.get_usuario_por_documento(db, tipo, numero)
            if usuario:
                # Ajusta el nombre del atributo 'rol' según tu modelo (p. ej. usuario.rol)
                rol = getattr(usuario, "rol", None) or getattr(usuario, "role", None)
                if rol:
                    if str(rol).lower() in ("profesor"):
                        with open('opciones_profes.json', encoding='utf-8') as f:
                            opciones_a_usar = json.load(f)
                    elif str(rol).lower() in ("estudiante"):
                        with open('opciones_estudiantes.json', encoding='utf-8') as f:
                            opciones_a_usar = json.load(f)
    except Exception as e:
        print("Error buscando rol/seleccionando opciones:", e)

    respuesta = ChatBot(request, opciones_a_usar).respuesta()

    # Guardar en el historial
    try:
        # Asegurar que identificacion sea un diccionario
        identificacion = request.identificacion if isinstance(request.identificacion, dict) else {}
        
        chat_history = schemas.ChatHistorialCreate(
            tipo_documento=identificacion.get("tipo") if identificacion else None,
            numero_documento=identificacion.get("numero") if identificacion else None,
            mensaje=request.mensaje,
            respuesta=str(respuesta.get("mensajes", [])) if isinstance(respuesta, dict) else str(respuesta),
            estado=request.estado
        )
        crud.crear_historial_chat(db, chat_history)
    except Exception as e:
        print(f"Error guardando historial: {e}")
        import traceback
        traceback.print_exc()  # Esto imprimirá más detalles del error
    
    return respuesta