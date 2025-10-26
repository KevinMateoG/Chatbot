from fastapi import FastAPI,FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from model.chat_bot import *
from sqlalchemy.orm import Session
from typing import List
import models, schemas, crud

from pathlib import Path

backend_path = Path(__file__).resolve().parent
sys.path.append(str(backend_path))
from databaseconfig import engine, get_db

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open('opciones.json') as f:
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
