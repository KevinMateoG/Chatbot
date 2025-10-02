from typing import Dict
import sys
from pathlib import Path

backend_path = Path(__file__).resolve().parent
sys.path.append(str(backend_path))
from encuesta import *
from controller.base_datos import *

class ChatBot:
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

                # --- NUEVO: DETECTAR INICIO DE ENCUESTA ---
                if siguiente.get("pregunta_encuesta"):
                    # Inicializar datos temporales de la encuesta
                    if "datos_encuesta" not in identificacion:
                        identificacion["datos_encuesta"] = {}
                        
                    respuesta["nuevo_estado"] = "en_encuesta"
                    respuesta["nodo_actual"] = siguiente 
                    
                    # Mostrar la primera pregunta de la encuesta y sus opciones
                    respuesta["mensajes"].append(siguiente["pregunta_encuesta"])
                    respuesta["opciones"] = siguiente["respuestas_encuesta"]
                    return respuesta

                if "resultado" in siguiente:
                    respuesta["nuevo_estado"] = "reiniciar"
                    respuesta["mensajes"].extend([
                        siguiente["resultado"],
                    "¿Deseas hacer otra consulta? Escribe 'sí' o 'no'."
                    ])
                
                else:
                    if "pregunta" in siguiente and "opciones" in siguiente:
                        respuesta["nodo_actual"] = siguiente
                        respuesta["mensajes"].append(siguiente["pregunta"])
                        respuesta["opciones"] = siguiente["opciones"]
                    else:
                        respuesta["mensajes"].append("Error en la estructura del nodo. No se encontró 'pregunta'.")
                        respuesta["opciones"] = nodo_actual["opciones"]
                        return respuesta 

        elif estado == "en_encuesta":
            seleccion = mensaje.strip()
            respuestas_validas = nodo_actual.get("respuestas_encuesta", {})
            respuesta_seleccionada = respuestas_validas.get(seleccion)

            if not respuesta_seleccionada:
                respuesta["mensajes"].append("Opción no válida para la encuesta. Por favor, selecciona un número de la lista.")
                respuesta["mensajes"].append(nodo_actual["pregunta_encuesta"])
                respuesta["opciones"] = respuestas_validas
                return respuesta

            dato_clave = respuesta_seleccionada["dato_clave"]
            identificacion["datos_encuesta"][dato_clave] = respuesta_seleccionada["texto"]

            siguiente_nodo = nodo_actual.get("siguiente")

            if siguiente_nodo:
                respuesta["nodo_actual"] = siguiente_nodo
                
                respuesta["mensajes"].append(siguiente_nodo["pregunta_encuesta"])
                respuesta["opciones"] = siguiente_nodo["respuestas_encuesta"]
                
                return respuesta 
            
            else:
                mensaje_registro = encuesta.subir_opciones(identificacion['numero'], identificacion["datos_encuesta"])
                
                identificacion["datos_encuesta"] = {}
                respuesta["nuevo_estado"] = "reiniciar"
                respuesta["mensajes"].extend([
                    mensaje_registro,
                    "¿Deseas hacer otra consulta? Escribe 'sí' o 'no'."
                ])
                
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