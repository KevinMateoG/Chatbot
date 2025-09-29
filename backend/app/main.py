from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from model.chat_bot import *
app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # URL de tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar opciones.json
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
async def procesar_mensaje(request: MensajeRequest):
    return Chat(request,OPCIONES).respuesta()