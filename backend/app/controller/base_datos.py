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

    def buscaride (ide):
        cursor = BaseDatos.obtener_cursor()

        consulta = f"select nombre from estudiante where id like '{ide}'"
        cursor.execute(consulta)

        resultado = cursor.fetchone()
        return resultado

    def obtener_cursor():
        connection = psycopg2.connect(database=secretconfig.PGDATABASE, user=secretconfig.PGUSER, password=secretconfig.PGPASSWORD, host=secretconfig.PGHOST)
        cursor = connection.cursor()
        return cursor
