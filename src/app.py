from flask import Flask, jsonify, request
from flask_cors import CORS
import cx_Oracle

app = Flask(__name__)
CORS(app)

# Detalles de conexión a la base de datos
db_user = "ADMIN_INV"
db_password = "LZYM123"
db_host = "localhost"
db_port = 1521
db_sid = "xe"

def obtener_conexion():
    try:
        dsn_tns = cx_Oracle.makedsn(db_host, db_port, sid=db_sid)
        connection = cx_Oracle.connect(db_user, db_password, dsn_tns)
        return connection
    except cx_Oracle.Error as error:
        print("Error al conectar a Oracle:", error)
        return None

# --- Funciones CRUD para TIPO_PRODUCTOS_LZYM ---

def obtener_tipos_producto_db():
    connection = obtener_conexion()
    cursor = None
    tipos = []
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT ID_TIPO_PRODUCTO, NOMBRE FROM TIPO_PRODUCTOS_LZYM")
            tipos = [{"id": row[0], "nombre": row[1]} for row in cursor.fetchall()]
    except cx_Oracle.Error as error:
        print("Error al consultar tipos de producto:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return tipos

def obtener_tipo_producto_por_id_db(id_tipo_producto):
    connection = obtener_conexion()
    cursor = None
    tipo = None
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT ID_TIPO_PRODUCTO, NOMBRE FROM TIPO_PRODUCTOS_LZYM WHERE ID_TIPO_PRODUCTO = :id", id=id_tipo_producto)
            result = cursor.fetchone()
            if result:
                tipo = {"id": result[0], "nombre": result[1]}
    except cx_Oracle.Error as error:
        print(f"Error al obtener tipo de producto con ID {id_tipo_producto}:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return tipo

def crear_tipo_producto_db(nombre_tipo):
    connection = obtener_conexion()
    cursor = None
    new_id = None
    try:
        if connection:
            cursor = connection.cursor()
            # Consultar el último ID y agregar 1
            cursor.execute("SELECT MAX(ID_TIPO_PRODUCTO) FROM TIPO_PRODUCTOS_LZYM")
            last_id = cursor.fetchone()[0]
            new_id = (last_id or 0) + 1

            # Insertar el nuevo tipo de producto con el ID generado
            cursor.execute("INSERT INTO TIPO_PRODUCTOS_LZYM (ID_TIPO_PRODUCTO, NOMBRE) VALUES (:id, :nombre)", id=new_id, nombre=nombre_tipo)
            connection.commit()
            return new_id
    except cx_Oracle.Error as error:
        connection.rollback()
        print("Error al crear tipo de producto:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return None

def actualizar_tipo_producto_db(id_tipo_producto, nuevo_nombre):
    connection = obtener_conexion()
    cursor = None
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE TIPO_PRODUCTOS_LZYM SET NOMBRE = :nombre WHERE ID_TIPO_PRODUCTO = :id", nombre=nuevo_nombre, id=id_tipo_producto)
            if cursor.rowcount > 0:
                connection.commit()
                return True
            else:
                connection.rollback()
                return False
    except cx_Oracle.Error as error:
        connection.rollback()
        print(f"Error al actualizar tipo de producto con ID {id_tipo_producto}:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return False

def eliminar_tipo_producto_db(id_tipo_producto):
    connection = obtener_conexion()
    cursor = None
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM TIPO_PRODUCTOS_LZYM WHERE ID_TIPO_PRODUCTO = :id", id=id_tipo_producto)
            if cursor.rowcount > 0:
                connection.commit()
                return True
            else:
                connection.rollback()
                return False
    except cx_Oracle.Error as error:
        connection.rollback()
        print(f"Error al eliminar tipo de producto con ID {id_tipo_producto}:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return False

# --- Rutas para TIPO_PRODUCTOS_LZYM ---

@app.route('/api/tipos_producto', methods=['GET'])
def get_tipos_producto():
    tipos = obtener_tipos_producto_db()
    return jsonify(tipos)

@app.route('/api/tipos_producto/<int:id_tipo_producto>', methods=['GET'])
def get_tipo_producto(id_tipo_producto):
    tipo = obtener_tipo_producto_por_id_db(id_tipo_producto)
    if tipo:
        return jsonify(tipo)
    return jsonify({"message": "Tipo de producto no encontrado"}), 404

@app.route('/api/tipos_producto', methods=['POST'])
def crear_tipo_producto():
    data = request.get_json()
    if 'nombre' in data:
        nuevo_id = crear_tipo_producto_db(data['nombre'])
        if nuevo_id:
            tipo_creado = obtener_tipo_producto_por_id_db(nuevo_id)
            return jsonify(tipo_creado), 201
        return jsonify({"message": "Error al crear el tipo de producto"}), 500
    return jsonify({"message": "El campo 'nombre' es requerido"}), 400

@app.route('/api/tipos_producto/<int:id_tipo_producto>', methods=['PUT'])
def actualizar_tipo_producto(id_tipo_producto):
    data = request.get_json()
    if 'nombre' in data:
        if actualizar_tipo_producto_db(id_tipo_producto, data['nombre']):
            tipo_actualizado = obtener_tipo_producto_por_id_db(id_tipo_producto)
            return jsonify(tipo_actualizado)
        return jsonify({"message": "Tipo de producto no encontrado o error al actualizar"}), 404
    return jsonify({"message": "El campo 'nombre' es requerido"}), 400

@app.route('/api/tipos_producto/<int:id_tipo_producto>', methods=['DELETE'])
def eliminar_tipo_producto(id_tipo_producto):
    if eliminar_tipo_producto_db(id_tipo_producto):
        return jsonify({"message": f"Tipo de producto con ID {id_tipo_producto} eliminado"})
    return jsonify({"message": "Tipo de producto no encontrado o error al eliminar"}), 404

# --- Rutas para PRODUCTOS_LZYM (actualizadas) ---

@app.route('/', methods=['GET'])
def get_api_root():
    return jsonify({"message": "API de gestión de productos y tipos de producto"})

@app.route('/api/productos', methods=['GET'])
def get_productos():
    productos = obtener_productos_db()
    return jsonify(productos)

@app.route('/api/productos/<int:id_producto>', methods=['GET'])
def get_producto(id_producto):
    producto = obtener_producto_por_id_db(id_producto)
    if producto:
        return jsonify(producto)
    return jsonify({"message": "Producto no encontrado"}), 404

@app.route('/api/productos', methods=['POST'])
def crear_producto():
    data = request.get_json()
    if 'nombre' in data and 'tipo_producto_id' in data:
        nuevo_id = crear_producto_db(data['nombre'], data['tipo_producto_id'])
        if nuevo_id:
            producto_creado = obtener_producto_por_id_db(nuevo_id)
            return jsonify(producto_creado), 201
        return jsonify({"message": "Error al crear el producto"}), 500
    return jsonify({"message": "Los campos 'nombre' y 'tipo_producto_id' son requeridos"}), 400

@app.route('/api/productos/<int:id_producto>', methods=['PUT'])
def actualizar_producto(id_producto):
    data = request.get_json()
    if 'nombre' in data and 'tipo_producto_id' in data:
        if actualizar_producto_db(id_producto, data['nombre'], data['tipo_producto_id']):
            producto_actualizado = obtener_producto_por_id_db(id_producto)
            return jsonify(producto_actualizado)
        return jsonify({"message": "Producto no encontrado o error al actualizar"}), 404
    return jsonify({"message": "Los campos 'nombre' y 'tipo_producto_id' son requeridos"}), 400

@app.route('/api/productos/<int:id_producto>', methods=['DELETE'])
def eliminar_producto(id_producto):
    if eliminar_producto_db(id_producto):
        return jsonify({"message": f"Producto con ID {id_producto} eliminado"})
    return jsonify({"message": "Producto no encontrado o error al eliminar"}), 404

if __name__ == '__main__':
    app.run(debug=True)