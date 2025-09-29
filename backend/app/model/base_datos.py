import psycopg2
import sys
sys.path.append(".")
from backend import secretconfig

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
