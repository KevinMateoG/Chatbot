import json
from typing import Dict
from pydantic import BaseModel, Field 
import sys
from pathlib import Path


backend_path = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(backend_path))

from app.model.base_datos import *

class Chat:
    def __init__(self, request, opciones:Dict):
        self.opciones = opciones
        self.request = request

    def respuesta(self):
        mensaje = self.request.mensaje
        estado = self.request.estado
        identificacion = self.request.identificacion
        nodo_actual = self.request.nodo_actual
    
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
            respuesta["nodo_actual"] = self.opciones
            respuesta["mensajes"].extend([
                f"¡Gracias! {BaseDatos.buscaride(identificacion['numero'])[0]}",
                self.opciones["pregunta"]
            ])
            respuesta["opciones"] = self.opciones["opciones"]

        elif estado == "en_opciones":
            # Usamos .get() para acceder de forma segura a opciones
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
                respuesta["nodo_actual"] = self.opciones
                respuesta["mensajes"].append(self.opciones["pregunta"])
                respuesta["opciones"] = self.opciones["opciones"]
            else:
                respuesta["nuevo_estado"] = "finalizado"
                respuesta["mensajes"].append("¡Gracias por usar el asistente!")

        return respuesta
    
    def buscar_estudiante (self,Estudiante):
        pass