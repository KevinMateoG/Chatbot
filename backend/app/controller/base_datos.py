import psycopg2
import sys
from pathlib import Path

# Agregar el directorio raíz del backend al PATH
backend_path = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(backend_path))

import secretconfig

class BaseDatos:

    def consulta_estudiante ():
        cursor = BaseDatos.obtener_cursor()

    def buscaride (id):
        cursor = BaseDatos.obtener_cursor()

        consulta = f"select nombre from estudiante where id like '{id}'"
        cursor.execute(consulta)

        resultado = cursor.fetchone()
        return resultado

    def guardar_encuesta(identificacion, datos_encuesta):
        
        # --- Lógica de la base de datos (Ejemplo de simulación) ---
        print(f"✅ ¡Encuesta registrada! Usuario: {identificacion['numero']}")
        for key, value in datos_encuesta.items():
             print(f"- {key}: {value}")
        # Aquí debes añadir el código de inserción real
        # usando tu conector de base de datos (e.g., psycopg2, mysql.connector, SQLAlchemy, etc.)
        # -----------------------------------------------------------

        return "¡Gracias! Tu respuesta ha sido registrada exitosamente."

    def obtener_cursor():
        connection = psycopg2.connect(database=secretconfig.PGDATABASE, user=secretconfig.PGUSER, password=secretconfig.PGPASSWORD, host=secretconfig.PGHOST)
        cursor = connection.cursor()
        return cursor
