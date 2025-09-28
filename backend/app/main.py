from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, cambiar por URL específica
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
    mensaje = request.mensaje
    estado = request.estado
    identificacion = request.identificacion
    nodo_actual = request.nodo_actual
    
    respuesta = {
        "nuevo_estado": estado,
        "identificacion": identificacion,
        "nodo_actual": nodo_actual,
        "mensajes": [],
        "opciones": None
    }

    if estado == "pidiendo_tipo":
        identificacion["tipo"] = mensaje
        respuesta["nuevo_estado"] = "pidiendo_numero"
        respuesta["identificacion"] = identificacion
        respuesta["mensajes"].append("Ahora ingresa tu número de documento:")

    elif estado == "pidiendo_numero":
        identificacion["numero"] = mensaje
        respuesta["nuevo_estado"] = "en_opciones"
        respuesta["identificacion"] = identificacion
        respuesta["nodo_actual"] = OPCIONES
        respuesta["mensajes"].extend([
            f"¡Gracias! {identificacion['tipo']} {identificacion['numero']}",
            OPCIONES["pregunta"]
        ])
        respuesta["opciones"] = OPCIONES["opciones"]

    elif estado == "en_opciones":
        if nodo_actual and "opciones" in nodo_actual:
            seleccion = mensaje.strip()
            siguiente = nodo_actual["opciones"].get(seleccion)
            
            if not siguiente:
                respuesta["mensajes"].append("Opción no válida. Intenta de nuevo.")
                respuesta["opciones"] = nodo_actual["opciones"]
                return respuesta

            if "resultado" in siguiente:
                respuesta["nuevo_estado"] = "reiniciar"
                respuesta["mensajes"].extend([
                    siguiente["resultado"],
                    "¿Deseas hacer otra consulta? Escribe 'sí' o 'no'."
                ])
            else:
                respuesta["nodo_actual"] = siguiente
                respuesta["mensajes"].append(siguiente["pregunta"])
                respuesta["opciones"] = siguiente["opciones"]

    elif estado == "reiniciar":
        if mensaje.lower() in ["sí", "si"]:
            respuesta["nuevo_estado"] = "en_opciones"
            respuesta["nodo_actual"] = OPCIONES
            respuesta["mensajes"].append(OPCIONES["pregunta"])
            respuesta["opciones"] = OPCIONES["opciones"]
        else:
            respuesta["nuevo_estado"] = "finalizado"
            respuesta["mensajes"].append("¡Gracias por usar el asistente!")

    return respuesta