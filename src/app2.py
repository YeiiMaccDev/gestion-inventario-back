from flask import Flask, jsonify
from flask_cors import CORS
import cx_Oracle

app = Flask(__name__)
CORS(app) # Habilitar CORS para permitir peticiones desde Angular

# Detalles de conexión a la base de datos (reemplaza con tus credenciales)
db_user = "ADMIN_INV"
db_password = "LZYM123"
db_host = "localhost"
db_port = 1521
db_sid = "xe" 

def obtener_datos_de_oracle():
    try:
        dsn_tns = cx_Oracle.makedsn(db_host, db_port, sid=db_sid)
        connection = cx_Oracle.connect(db_user, db_password, dsn_tns)
        cursor = connection.cursor()
        cursor.execute("SELECT ID_PRODUCTO, NOMBRE FROM PRODUCTOS_LZYM") # Ejemplo de consulta
        productos = [{"id": row[0], "nombre": row[1]} for row in cursor.fetchall()]
        return productos
    except cx_Oracle.Error as error:
        print("Error al consultar Oracle:", error)
        return []
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/', methods=['GET'])
def get_api():
    productos = obtener_datos_de_oracle()
    return jsonify(productos)

@app.route('/api/productos', methods=['GET'])
def get_productos():
    productos = obtener_datos_de_oracle()
    return jsonify(productos)

if __name__ == '__main__':
    app.run(debug=True)