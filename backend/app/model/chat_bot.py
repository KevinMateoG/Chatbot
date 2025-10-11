from typing import Dict
import sys
from pathlib import Path

backend_path = Path(__file__).resolve().parent
sys.path.append(str(backend_path))
from encuesta import *
from controller.base_datos import *

class ChatBot:
    def __init__(self, request, opciones: Dict):
        self.opciones = opciones
        self.request = request

    def respuesta(self):
        """Controla el flujo principal del chatbot según el estado del usuario."""
        estado = self.request.estado

        if estado == "pidiendo_tipo":
            return self._procesar_tipo()
        elif estado == "pidiendo_numero":
            return self._procesar_numero()
        elif estado == "en_opciones":
            return self._procesar_opciones()
        elif estado == "en_encuesta":
            return self._procesar_encuesta()
        elif estado == "reiniciar":
            return self._reiniciar_conversacion()
        else:
            return self._mensaje_error("Estado no reconocido o fuera de flujo.")


    def _procesar_tipo(self):
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

        return respuesta

    def _procesar_numero(self):
        """Procesa el número de identificación y muestra las opciones principales."""
        mensaje = self.request.mensaje
        identificacion = self.request.identificacion

        respuesta = self._crear_respuesta_base()
        identificacion["numero"] = mensaje
        respuesta["nuevo_estado"] = "en_opciones"
        respuesta["identificacion"] = identificacion
        respuesta["nodo_actual"] = self.opciones

        # Buscar nombre en la BD (si existe)
        try:
            nombre = BaseDatos.buscaride(identificacion["numero"])[0]
            respuesta["mensajes"].append(f"¡Gracias! {nombre}")
        except Exception:
            respuesta["mensajes"].append("Número no encontrado en la base de datos.")

        respuesta["mensajes"].append(self.opciones["pregunta"])
        respuesta["opciones"] = self.opciones["opciones"]

        return respuesta

    def _procesar_opciones(self):
        mensaje = self.request.mensaje.strip()
        nodo_actual = self.request.nodo_actual
        identificacion = self.request.identificacion

        respuesta = self._crear_respuesta_base()
        respuesta["identificacion"] = identificacion

        if not nodo_actual or "opciones" not in nodo_actual:
            return self._mensaje_error("Estructura de nodo inválida.")

        seleccion = nodo_actual["opciones"].get(mensaje)
        
        if "resultado" in seleccion:
            respuesta["nuevo_estado"] = "reiniciar"
            respuesta["mensajes"].extend([
                seleccion["resultado"],
                "¿Deseas hacer otra consulta? Escribe 'sí' o 'no'."
            ])
        else:
            # Pasar al siguiente nodo
            if "pregunta" in seleccion and "opciones" in seleccion:
                respuesta["nodo_actual"] = seleccion
                respuesta["mensajes"].append(seleccion["pregunta"])
                respuesta["opciones"] = seleccion["opciones"]
            else:
                return self._mensaje_error("Error en la estructura del flujo de opciones.")

        return respuesta

    def _procesar_encuesta(self):
        mensaje = self.request.mensaje.strip()
        nodo_actual = self.request.nodo_actual
        identificacion = self.request.identificacion

        respuesta = self._crear_respuesta_base()
        respuestas_validas = nodo_actual.get("respuestas_encuesta", {})
        seleccion = respuestas_validas.get(mensaje)

        if not seleccion:
            respuesta["mensajes"].append("Opción no válida. Selecciona un número de la lista.")
            respuesta["mensajes"].append(nodo_actual["pregunta_encuesta"])
            respuesta["opciones"] = respuestas_validas
            return respuesta

        if "datos_encuesta" not in identificacion:
            identificacion["datos_encuesta"] = {}

        dato_clave = seleccion["dato_clave"]
        identificacion["datos_encuesta"][dato_clave] = seleccion["texto"]

        siguiente = nodo_actual.get("siguiente")
        if siguiente:
            respuesta["nodo_actual"] = siguiente
            respuesta["mensajes"].append(siguiente["pregunta_encuesta"])
            respuesta["opciones"] = siguiente["respuestas_encuesta"]
            return respuesta

        mensaje_registro = encuesta.subir_opciones(
            identificacion["numero"], identificacion["datos_encuesta"]
        )
        identificacion["datos_encuesta"] = {}
        respuesta["nuevo_estado"] = "reiniciar"
        respuesta["mensajes"].extend([
            mensaje_registro,
            "¿Deseas hacer otra consulta? Escribe 'sí' o 'no'."
        ])

        return respuesta

    def _reiniciar_conversacion(self):
        mensaje = self.request.mensaje.lower()
        respuesta = self._crear_respuesta_base()

        if mensaje in ["sí", "si"]:
            respuesta["nuevo_estado"] = "en_opciones"
            respuesta["nodo_actual"] = self.opciones
            respuesta["mensajes"].append(self.opciones["pregunta"])
            respuesta["opciones"] = self.opciones["opciones"]
        else:
            respuesta["nuevo_estado"] = "finalizado"
            respuesta["mensajes"].append("¡Gracias por usar el asistente!")

        return respuesta
    
    def _crear_respuesta_base(self, nuevo_estado=None, nodo_actual=None):

        return {
            "nuevo_estado": nuevo_estado or self.request.estado,
            "identificacion": self.request.identificacion,
            "nodo_actual": nodo_actual or self.request.nodo_actual,
            "mensajes": [],
            "opciones": None
        }
