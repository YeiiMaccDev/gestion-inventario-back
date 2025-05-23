from flask import Flask, jsonify, request
from flask_cors import CORS
import cx_Oracle
from datetime import datetime # Necesario para manejar fechas, aunque no se usa directamente en PRODUCTOS_LZYM

app = Flask(__name__)
CORS(app)

# Detalles de conexión a la base de datos
db_user = "ADMIN_INV"
db_password = "LZYM123"
db_host = "localhost"
db_port = 1521
db_sid = "xe"

def obtener_conexion():
    """Establece y devuelve una conexión a la base de datos Oracle."""
    try:
        dsn_tns = cx_Oracle.makedsn(db_host, db_port, sid=db_sid)
        connection = cx_Oracle.connect(db_user, db_password, dsn_tns)
        return connection
    except cx_Oracle.Error as error:
        print("Error al conectar a Oracle:", error)
        return None

    #  Funciones CRUD para TIPO_PRODUCTOS_LZYM 

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
            # Consultar el último ID y agregar 1 (considerar usar secuencias de Oracle para producción)
            cursor.execute("SELECT NVL(MAX(ID_TIPO_PRODUCTO), 0) FROM TIPO_PRODUCTOS_LZYM")
            last_id = cursor.fetchone()[0]
            new_id = last_id + 1

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

#  Rutas para TIPO_PRODUCTOS_LZYM 

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



# Funciones CRUD para PRODUCTOS_LZYM (AÑADIDAS Y CORREGIDAS)

def obtener_productos_db():
    connection = obtener_conexion()
    cursor = None
    productos = []
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT p.ID_PRODUCTO, p.NOMBRE, p.DESCRIPCION, p.COD_BARRAS,
                       p.PRECIO_COMPRA, p.PRECIO_VENTA,
                       t.ID_TIPO_PRODUCTO, t.NOMBRE AS TIPO_PRODUCTO_NOMBRE,
                       c.ID_CATEGORIA_PRODUCTO, c.NOMBRE AS CATEGORIA_PRODUCTO_NOMBRE
                FROM PRODUCTOS_LZYM p
                JOIN TIPO_PRODUCTOS_LZYM t ON p.ID_TIPO_PRODUCTO = t.ID_TIPO_PRODUCTO
                JOIN CATEGORIA_PRODUCTOS_LZYM c ON p.ID_CATEGORIA_PRODUCTO = c.ID_CATEGORIA_PRODUCTO
            """)
            for row in cursor.fetchall():
                productos.append({
                    "id": row[0],
                    "nombre": row[1],
                    "descripcion": row[2],
                    "cod_barras": row[3],
                    "precio_compra": row[4],
                    "precio_venta": row[5],
                    "tipo_producto": {"id": row[6], "nombre": row[7]},
                    "categoria_producto": {"id": row[8], "nombre": row[9]}
                })
    except cx_Oracle.Error as error:
        print("Error al consultar productos:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return productos

def obtener_producto_por_id_db(id_producto):
    connection = obtener_conexion()
    cursor = None
    producto = None
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT p.ID_PRODUCTO, p.NOMBRE, p.DESCRIPCION, p.COD_BARRAS,
                       p.PRECIO_COMPRA, p.PRECIO_VENTA,
                       t.ID_TIPO_PRODUCTO, t.NOMBRE AS TIPO_PRODUCTO_NOMBRE,
                       c.ID_CATEGORIA_PRODUCTO, c.NOMBRE AS CATEGORIA_PRODUCTO_NOMBRE
                FROM PRODUCTOS_LZYM p
                JOIN TIPO_PRODUCTOS_LZYM t ON p.ID_TIPO_PRODUCTO = t.ID_TIPO_PRODUCTO
                JOIN CATEGORIA_PRODUCTOS_LZYM c ON p.ID_CATEGORIA_PRODUCTO = c.ID_CATEGORIA_PRODUCTO
                WHERE p.ID_PRODUCTO = :id
            """, id=id_producto)
            result = cursor.fetchone()
            if result:
                producto = {
                    "id": result[0],
                    "nombre": result[1],
                    "descripcion": result[2],
                    "cod_barras": result[3],
                    "precio_compra": result[4],
                    "precio_venta": result[5],
                    "tipo_producto": {"id": result[6], "nombre": result[7]},
                    "categoria_producto": {"id": result[8], "nombre": result[9]}
                }
    except cx_Oracle.Error as error:
        print(f"Error al obtener producto con ID {id_producto}:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return producto

def crear_producto_db(nombre, descripcion, cod_barras, precio_compra, precio_venta, id_tipo_producto, id_categoria_producto):
    connection = obtener_conexion()
    cursor = None
    new_id = None
    try:
        if connection:
            cursor = connection.cursor()
            # Consultar el último ID y agregar 1 (considerar usar secuencias de Oracle para producción)
            cursor.execute("SELECT NVL(MAX(ID_PRODUCTO), 0) FROM PRODUCTOS_LZYM")
            last_id = cursor.fetchone()[0]
            new_id = last_id + 1

            cursor.execute("""
                INSERT INTO PRODUCTOS_LZYM (
                    ID_PRODUCTO, NOMBRE, DESCRIPCION, COD_BARRAS, PRECIO_COMPRA, PRECIO_VENTA,
                    ID_TIPO_PRODUCTO, ID_CATEGORIA_PRODUCTO
                ) VALUES (
                    :id, :nombre, :descripcion, :cod_barras, :precio_compra, :precio_venta,
                    :id_tipo, :id_categoria
                )
            """,
            id=new_id,
            nombre=nombre,
            descripcion=descripcion,
            cod_barras=cod_barras,
            precio_compra=precio_compra,
            precio_venta=precio_venta,
            id_tipo=id_tipo_producto,
            id_categoria=id_categoria_producto)
            connection.commit()
            return new_id
    except cx_Oracle.Error as error:
        connection.rollback()
        print("Error al crear producto:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return None

def actualizar_producto_db(id_producto, nombre, descripcion, cod_barras, precio_compra, precio_venta, id_tipo_producto, id_categoria_producto):
    connection = obtener_conexion()
    cursor = None
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE PRODUCTOS_LZYM SET
                    NOMBRE = :nombre,
                    DESCRIPCION = :descripcion,
                    COD_BARRAS = :cod_barras,
                    PRECIO_COMPRA = :precio_compra,
                    PRECIO_VENTA = :precio_venta,
                    ID_TIPO_PRODUCTO = :id_tipo,
                    ID_CATEGORIA_PRODUCTO = :id_categoria
                WHERE ID_PRODUCTO = :id
            """,
            nombre=nombre,
            descripcion=descripcion,
            cod_barras=cod_barras,
            precio_compra=precio_compra,
            precio_venta=precio_venta,
            id_tipo=id_tipo_producto,
            id_categoria=id_categoria_producto,
            id=id_producto)
            if cursor.rowcount > 0:
                connection.commit()
                return True
            else:
                connection.rollback()
                return False
    except cx_Oracle.Error as error:
        connection.rollback()
        print(f"Error al actualizar producto con ID {id_producto}:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return False

def eliminar_producto_db(id_producto):
    connection = obtener_conexion()
    cursor = None
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM PRODUCTOS_LZYM WHERE ID_PRODUCTO = :id", id=id_producto)
            if cursor.rowcount > 0:
                connection.commit()
                return True
            else:
                connection.rollback()
                return False
    except cx_Oracle.Error as error:
        connection.rollback()
        print(f"Error al eliminar producto con ID {id_producto}:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return False

#  Rutas para PRODUCTOS_LZYM 

@app.route('/', methods=['GET'])
def get_api_root():
    return jsonify({"message": "API de gestión de inventario LZYM"})

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
    required_fields = ['nombre', 'descripcion', 'cod_barras', 'precio_compra', 'precio_venta', 'id_tipo_producto', 'id_categoria_producto']
    if all(field in data for field in required_fields):
        new_id = crear_producto_db(
            data['nombre'],
            data['descripcion'],
            data['cod_barras'],
            data['precio_compra'],
            data['precio_venta'],
            data['id_tipo_producto'],
            data['id_categoria_producto']
        )
        if new_id:
            producto_creado = obtener_producto_por_id_db(new_id)
            return jsonify(producto_creado), 201
        return jsonify({"message": "Error al crear el producto"}), 500
    return jsonify({"message": "Faltan campos requeridos para crear el producto"}), 400

@app.route('/api/productos/<int:id_producto>', methods=['PUT'])
def actualizar_producto(id_producto):
    data = request.get_json()
    required_fields = ['nombre', 'descripcion', 'cod_barras', 'precio_compra', 'precio_venta', 'id_tipo_producto', 'id_categoria_producto']
    if all(field in data for field in required_fields):
        if actualizar_producto_db(
            id_producto,
            data['nombre'],
            data['descripcion'],
            data['cod_barras'],
            data['precio_compra'],
            data['precio_venta'],
            data['id_tipo_producto'],
            data['id_categoria_producto']
        ):
            producto_actualizado = obtener_producto_por_id_db(id_producto)
            return jsonify(producto_actualizado)
        return jsonify({"message": "Producto no encontrado o error al actualizar"}), 404
    return jsonify({"message": "Faltan campos requeridos para actualizar el producto"}), 400

@app.route('/api/productos/<int:id_producto>', methods=['DELETE'])
def eliminar_producto(id_producto):
    if eliminar_producto_db(id_producto):
        return jsonify({"message": f"Producto con ID {id_producto} eliminado"})
    return jsonify({"message": "Producto no encontrado o error al eliminar"}), 404

if __name__ == '__main__':
    # Ejecutar en modo debug para desarrollo. Desactivar en producción.
    app.run(debug=True)