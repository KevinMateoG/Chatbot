from typing import Dict
import sys
from pathlib import Path

backend_path = Path(__file__).resolve().parent
sys.path.append(str(backend_path))
from materia import Materia
from encuesta import *
from controller.base_datos import *
from model.buzon_sugerencias import BuzonSugerencia

class ChatBot:
    def __init__(self, request, opciones: Dict):
        self.opciones = opciones
        self.request = request

    def _mensaje_error(self, mensaje):
        return mensaje

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
        elif estado == "en_sugerencia":
            return self._procesar_sugerencia()
        elif estado == "ordenar_materias":
            return self._priorizar_materias()
        elif estado == "reiniciar":
            return self._reiniciar_conversacion()
        else:
            return self._mensaje_error("Estado no reconocido o fuera de flujo.")

    def _priorizar_materias(self):
        """Obtiene y muestra las materias priorizadas del estudiante"""
        identificacion = self.request.identificacion
        respuesta = self._crear_respuesta_base()
        try:
            # Obtener el ID del estudiante
            id_estudiante = identificacion.get("numero")
            
            if not id_estudiante:
                respuesta["mensajes"].append("No se pudo identificar tu número de documento.")
                respuesta["nuevo_estado"] = "reiniciar"
                respuesta["mensajes"].append("¿Deseas hacer otra consulta? Escribe 'sí' o 'no'.")
                return respuesta
            
            # Obtener materias priorizadas
            materias_priorizadas = Materia.ordenar_matrias(id_estudiante)
            
            if not materias_priorizadas:
                respuesta["mensajes"].append("No tienes materias registradas en el sistema.")
            else:
                # Construir mensaje con las materias
                mensaje_materias = "📚 <b>Tus materias priorizadas son:</b><br><br>"
                
                for materia, prioridad in materias_priorizadas.items():
                    mensaje_materias += f"• <b>{materia.nombre_materia}</b><br>"
                    mensaje_materias += f"  Créditos: {materia.creditos}<br>"
                    mensaje_materias += f"  Prioridad: <b>{prioridad}</b><br><br>"
                
                respuesta["mensajes"].append(mensaje_materias)
            
            # Cambiar a estado de reiniciar
            respuesta["nuevo_estado"] = "reiniciar"
            respuesta["mensajes"].append("¿Deseas hacer otra consulta? Escribe 'sí' o 'no'.")
            
        except Exception as e:
            print(f"Error al priorizar materias: {e}")
            import traceback
            traceback.print_exc()
            respuesta["mensajes"].append("Error al obtener las materias priorizadas.")
            respuesta["nuevo_estado"] = "reiniciar"
            respuesta["mensajes"].append("¿Deseas intentar nuevamente? Escribe 'sí' o 'no'.")
        
        return respuesta

    def _procesar_sugerencia(self):
        """Procesa las sugerencias del buzón paso a paso."""
        mensaje = self.request.mensaje.strip()
        nodo_actual = self.request.nodo_actual
        identificacion = self.request.identificacion

        respuesta = self._crear_respuesta_base()
        respuestas_validas = nodo_actual.get("respuestas_sugerencia", {})
        
        # Inicializar datos_buzon si no existe
        if "datos_buzon" not in identificacion:
            identificacion["datos_buzon"] = {}

        # Verificar si es un campo de texto libre (descripción)
        if "libre" in respuestas_validas:
            # El usuario está escribiendo la descripción
            dato_clave = respuestas_validas["libre"].get("dato_clave")
            identificacion["datos_buzon"][dato_clave] = mensaje
            
            # Verificar si hay resultado_sugerencia para guardar
            if nodo_actual.get("resultado_sugerencia"):
                try:
                    # Agregar tipo_documento al diccionario
                    datos_completos = {
                        "tipo_documento": identificacion.get("tipo"),
                        **identificacion["datos_buzon"]
                    }
                    
                    mensaje_registro = BuzonSugerencia.procesar_sugerencia(
                        id_estudiante=identificacion.get("numero"),
                        datos_sugerencia=datos_completos
                    )
                    
                    # Limpiar los datos temporales
                    identificacion["datos_buzon"] = {}
                    
                    respuesta["nuevo_estado"] = "reiniciar"
                    respuesta["mensajes"].extend([
                        mensaje_registro,
                        "¿Deseas hacer otra consulta? Escribe 'sí' o 'no'."
                    ])
                    return respuesta
                except Exception as e:
                    print(f"Error al guardar sugerencia: {e}")
                    import traceback
                    traceback.print_exc()
                    respuesta["mensajes"].append(f"Error al procesar la sugerencia: {str(e)}")
                    respuesta["mensajes"].append("¿Deseas intentar nuevamente? Escribe 'sí' o 'no'.")
                    respuesta["nuevo_estado"] = "reiniciar"
                    return respuesta
        
        # Si no es texto libre, validar selección de opciones
        seleccion = respuestas_validas.get(mensaje)
        
        if not seleccion:
            respuesta["mensajes"].append("Opción no válida. Selecciona un número de la lista.")
            respuesta["mensajes"].append(nodo_actual.get("pregunta_sugerencia", "Por favor, selecciona una opción."))
            respuesta["opciones"] = respuestas_validas
            return respuesta

        # Guardar la respuesta del usuario
        dato_clave = seleccion.get("dato_clave")
        if dato_clave:
            identificacion["datos_buzon"][dato_clave] = seleccion["texto"]
        
        # Verificar si hay siguiente pregunta
        siguiente = nodo_actual.get("siguiente")
        if siguiente:
            respuesta["nodo_actual"] = siguiente
            respuesta["mensajes"].append(siguiente.get("pregunta_sugerencia", "Siguiente pregunta..."))
            respuesta["opciones"] = siguiente.get("respuestas_sugerencia", {})
            return respuesta
        
        return respuesta
    
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
            nombre = BaseDatos.buscar_id(identificacion["numero"])[0]
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
            # Verificar si tiene un estado específico (como ordenar_materias)
            if "estado" in seleccion:
                estado = seleccion["estado"]
                if estado == "ordenar_materias":
                    return self._priorizar_materias()
                else:
                    # Para otros estados futuros
                    respuesta["nuevo_estado"] = estado
                    return respuesta
            
            # Verificar si es una encuesta
            elif "pregunta_encuesta" in seleccion:
                respuesta["nuevo_estado"] = "en_encuesta"
                respuesta["nodo_actual"] = seleccion
                respuesta["mensajes"].append(seleccion["pregunta_encuesta"])
                respuesta["opciones"] = seleccion["respuestas_encuesta"]
                return respuesta
            
            # Verificar si es una sugerencia
            elif "pregunta_sugerencia" in seleccion:
                respuesta["nuevo_estado"] = "en_sugerencia"
                respuesta["nodo_actual"] = seleccion
                respuesta["mensajes"].append(seleccion["pregunta_sugerencia"])
                respuesta["opciones"] = seleccion["respuestas_sugerencia"]
                return respuesta
            
            elif "pregunta" in seleccion and "opciones" in seleccion:
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
