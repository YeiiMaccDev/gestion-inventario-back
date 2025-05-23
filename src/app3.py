from flask import Flask, jsonify, request
from flask_cors import CORS
import cx_Oracle
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

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

# Función auxiliar para convertir cadena de fecha a objeto datetime
def parse_date(date_string):
    if date_string:
        try:
            # Intentar varios formatos comunes
            return datetime.strptime(date_string, '%Y-%m-%d')
        except ValueError:
            try:
                return datetime.strptime(date_string, '%Y/%m/%d')
            except ValueError:
                return None # O levantar una excepción
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
            cursor.execute("SELECT NVL(MAX(ID_TIPO_PRODUCTO), 0) FROM TIPO_PRODUCTOS_LZYM")
            last_id = cursor.fetchone()[0]
            new_id = last_id + 1

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

# --- Funciones CRUD para CATEGORIA_PRODUCTOS_LZYM ---

def obtener_categorias_producto_db():
    connection = obtener_conexion()
    cursor = None
    categorias = []
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT ID_CATEGORIA_PRODUCTO, NOMBRE FROM CATEGORIA_PRODUCTOS_LZYM")
            categorias = [{"id": row[0], "nombre": row[1]} for row in cursor.fetchall()]
    except cx_Oracle.Error as error:
        print("Error al consultar categorías de producto:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return categorias

def obtener_categoria_producto_por_id_db(id_categoria_producto):
    connection = obtener_conexion()
    cursor = None
    categoria = None
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT ID_CATEGORIA_PRODUCTO, NOMBRE FROM CATEGORIA_PRODUCTOS_LZYM WHERE ID_CATEGORIA_PRODUCTO = :id", id=id_categoria_producto)
            result = cursor.fetchone()
            if result:
                categoria = {"id": result[0], "nombre": result[1]}
    except cx_Oracle.Error as error:
        print(f"Error al obtener categoría de producto con ID {id_categoria_producto}:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return categoria

def crear_categoria_producto_db(nombre_categoria):
    connection = obtener_conexion()
    cursor = None
    new_id = None
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT NVL(MAX(ID_CATEGORIA_PRODUCTO), 0) FROM CATEGORIA_PRODUCTOS_LZYM")
            last_id = cursor.fetchone()[0]
            new_id = last_id + 1

            cursor.execute("INSERT INTO CATEGORIA_PRODUCTOS_LZYM (ID_CATEGORIA_PRODUCTO, NOMBRE) VALUES (:id, :nombre)", id=new_id, nombre=nombre_categoria)
            connection.commit()
            return new_id
    except cx_Oracle.Error as error:
        connection.rollback()
        print("Error al crear categoría de producto:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return None

def actualizar_categoria_producto_db(id_categoria_producto, nuevo_nombre):
    connection = obtener_conexion()
    cursor = None
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE CATEGORIA_PRODUCTOS_LZYM SET NOMBRE = :nombre WHERE ID_CATEGORIA_PRODUCTO = :id", nombre=nuevo_nombre, id=id_categoria_producto)
            if cursor.rowcount > 0:
                connection.commit()
                return True
            else:
                connection.rollback()
                return False
    except cx_Oracle.Error as error:
        connection.rollback()
        print(f"Error al actualizar categoría de producto con ID {id_categoria_producto}:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return False

def eliminar_categoria_producto_db(id_categoria_producto):
    connection = obtener_conexion()
    cursor = None
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM CATEGORIA_PRODUCTOS_LZYM WHERE ID_CATEGORIA_PRODUCTO = :id", id=id_categoria_producto)
            if cursor.rowcount > 0:
                connection.commit()
                return True
            else:
                connection.rollback()
                return False
    except cx_Oracle.Error as error:
        connection.rollback()
        print(f"Error al eliminar categoría de producto con ID {id_categoria_producto}:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return False

# --- Rutas para CATEGORIA_PRODUCTOS_LZYM ---

@app.route('/api/categorias_producto', methods=['GET'])
def get_categorias_producto():
    categorias = obtener_categorias_producto_db()
    return jsonify(categorias)

@app.route('/api/categorias_producto/<int:id_categoria_producto>', methods=['GET'])
def get_categoria_producto(id_categoria_producto):
    categoria = obtener_categoria_producto_por_id_db(id_categoria_producto)
    if categoria:
        return jsonify(categoria)
    return jsonify({"message": "Categoría de producto no encontrada"}), 404

@app.route('/api/categorias_producto', methods=['POST'])
def crear_categoria_producto():
    data = request.get_json()
    if 'nombre' in data:
        nuevo_id = crear_categoria_producto_db(data['nombre'])
        if nuevo_id:
            categoria_creada = obtener_categoria_producto_por_id_db(nuevo_id)
            return jsonify(categoria_creada), 201
        return jsonify({"message": "Error al crear la categoría de producto"}), 500
    return jsonify({"message": "El campo 'nombre' es requerido"}), 400

@app.route('/api/categorias_producto/<int:id_categoria_producto>', methods=['PUT'])
def actualizar_categoria_producto(id_categoria_producto):
    data = request.get_json()
    if 'nombre' in data:
        if actualizar_categoria_producto_db(id_categoria_producto, data['nombre']):
            categoria_actualizada = obtener_categoria_producto_por_id_db(id_categoria_producto)
            return jsonify(categoria_actualizada)
        return jsonify({"message": "Categoría de producto no encontrada o error al actualizar"}), 404
    return jsonify({"message": "El campo 'nombre' es requerido"}), 400

@app.route('/api/categorias_producto/<int:id_categoria_producto>', methods=['DELETE'])
def eliminar_categoria_producto(id_categoria_producto):
    if eliminar_categoria_producto_db(id_categoria_producto):
        return jsonify({"message": f"Categoría de producto con ID {id_categoria_producto} eliminada"})
    return jsonify({"message": "Categoría de producto no encontrada o error al eliminar"}), 404

# --- Funciones CRUD para LOTES_LZYM ---

def obtener_lotes_db():
    connection = obtener_conexion()
    cursor = None
    lotes = []
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT ID_LOTE, CODIGO_LOTE, FECHA_INGRESO, FECHA_VENCIMIENTO FROM LOTES_LZYM")
            for row in cursor.fetchall():
                lotes.append({
                    "id": row[0],
                    "codigo_lote": row[1],
                    "fecha_ingreso": row[2].strftime('%Y-%m-%d') if row[2] else None, # Formatear fecha para JSON
                    "fecha_vencimiento": row[3].strftime('%Y-%m-%d') if row[3] else None
                })
    except cx_Oracle.Error as error:
        print("Error al consultar lotes:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return lotes

def obtener_lote_por_id_db(id_lote):
    connection = obtener_conexion()
    cursor = None
    lote = None
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT ID_LOTE, CODIGO_LOTE, FECHA_INGRESO, FECHA_VENCIMIENTO FROM LOTES_LZYM WHERE ID_LOTE = :id", id=id_lote)
            result = cursor.fetchone()
            if result:
                lote = {
                    "id": result[0],
                    "codigo_lote": result[1],
                    "fecha_ingreso": result[2].strftime('%Y-%m-%d') if result[2] else None,
                    "fecha_vencimiento": result[3].strftime('%Y-%m-%d') if result[3] else None
                }
    except cx_Oracle.Error as error:
        print(f"Error al obtener lote con ID {id_lote}:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return lote

def crear_lote_db(codigo_lote, fecha_ingreso, fecha_vencimiento):
    connection = obtener_conexion()
    cursor = None
    new_id = None
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT NVL(MAX(ID_LOTE), 0) FROM LOTES_LZYM")
            last_id = cursor.fetchone()[0]
            new_id = last_id + 1

            cursor.execute("""
                INSERT INTO LOTES_LZYM (
                    ID_LOTE, CODIGO_LOTE, FECHA_INGRESO, FECHA_VENCIMIENTO
                ) VALUES (
                    :id, :codigo, :f_ingreso, :f_vencimiento
                )
            """,
            id=new_id,
            codigo=codigo_lote,
            f_ingreso=fecha_ingreso, # cx_Oracle maneja objetos datetime de Python
            f_vencimiento=fecha_vencimiento)
            connection.commit()
            return new_id
    except cx_Oracle.Error as error:
        connection.rollback()
        print("Error al crear lote:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return None

def actualizar_lote_db(id_lote, codigo_lote, fecha_ingreso, fecha_vencimiento):
    connection = obtener_conexion()
    cursor = None
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE LOTES_LZYM SET
                    CODIGO_LOTE = :codigo,
                    FECHA_INGRESO = :f_ingreso,
                    FECHA_VENCIMIENTO = :f_vencimiento
                WHERE ID_LOTE = :id
            """,
            codigo=codigo_lote,
            f_ingreso=fecha_ingreso,
            f_vencimiento=fecha_vencimiento,
            id=id_lote)
            if cursor.rowcount > 0:
                connection.commit()
                return True
            else:
                connection.rollback()
                return False
    except cx_Oracle.Error as error:
        connection.rollback()
        print(f"Error al actualizar lote con ID {id_lote}:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return False

def eliminar_lote_db(id_lote):
    connection = obtener_conexion()
    cursor = None
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM LOTES_LZYM WHERE ID_LOTE = :id", id=id_lote)
            if cursor.rowcount > 0:
                connection.commit()
                return True
            else:
                connection.rollback()
                return False
    except cx_Oracle.Error as error:
        connection.rollback()
        print(f"Error al eliminar lote con ID {id_lote}:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return False

# --- Rutas para LOTES_LZYM ---

@app.route('/api/lotes', methods=['GET'])
def get_lotes():
    lotes = obtener_lotes_db()
    return jsonify(lotes)

@app.route('/api/lotes/<int:id_lote>', methods=['GET'])
def get_lote(id_lote):
    lote = obtener_lote_por_id_db(id_lote)
    if lote:
        return jsonify(lote)
    return jsonify({"message": "Lote no encontrado"}), 404

@app.route('/api/lotes', methods=['POST'])
def crear_lote():
    data = request.get_json()
    required_fields = ['codigo_lote', 'fecha_ingreso']
    if all(field in data for field in required_fields):
        fecha_ingreso = parse_date(data['fecha_ingreso'])
        fecha_vencimiento = parse_date(data.get('fecha_vencimiento'))

        if not fecha_ingreso:
            return jsonify({"message": "Formato de fecha de ingreso inválido. UsebeginPath-MM-DD"}), 400
        if fecha_vencimiento and fecha_vencimiento < fecha_ingreso:
            return jsonify({"message": "La fecha de vencimiento no puede ser anterior a la fecha de ingreso"}), 400

        new_id = crear_lote_db(
            data['codigo_lote'],
            fecha_ingreso,
            fecha_vencimiento
        )
        if new_id:
            lote_creado = obtener_lote_por_id_db(new_id)
            return jsonify(lote_creado), 201
        return jsonify({"message": "Error al crear el lote"}), 500
    return jsonify({"message": "Los campos 'codigo_lote' y 'fecha_ingreso' son requeridos"}), 400

@app.route('/api/lotes/<int:id_lote>', methods=['PUT'])
def actualizar_lote(id_lote):
    data = request.get_json()
    required_fields = ['codigo_lote', 'fecha_ingreso']
    if all(field in data for field in required_fields):
        fecha_ingreso = parse_date(data['fecha_ingreso'])
        fecha_vencimiento = parse_date(data.get('fecha_vencimiento'))

        if not fecha_ingreso:
            return jsonify({"message": "Formato de fecha de ingreso inválido. UsebeginPath-MM-DD"}), 400
        if fecha_vencimiento and fecha_vencimiento < fecha_ingreso:
            return jsonify({"message": "La fecha de vencimiento no puede ser anterior a la fecha de ingreso"}), 400

        if actualizar_lote_db(
            id_lote,
            data['codigo_lote'],
            fecha_ingreso,
            fecha_vencimiento
        ):
            lote_actualizado = obtener_lote_por_id_db(id_lote)
            return jsonify(lote_actualizado)
        return jsonify({"message": "Lote no encontrado o error al actualizar"}), 404
    return jsonify({"message": "Los campos 'codigo_lote' y 'fecha_ingreso' son requeridos"}), 400

@app.route('/api/lotes/<int:id_lote>', methods=['DELETE'])
def eliminar_lote(id_lote):
    if eliminar_lote_db(id_lote):
        return jsonify({"message": f"Lote con ID {id_lote} eliminado"})
    return jsonify({"message": "Lote no encontrado o error al eliminar"}), 404

# --- Funciones CRUD para PRODUCTOS_LZYM ---

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

# --- Rutas para PRODUCTOS_LZYM ---

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

# --- Funciones CRUD para INVENTARIO_LZYM ---

def obtener_inventario_db():
    connection = obtener_conexion()
    cursor = None
    inventario_registros = []
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT i.ID_INVENTARIO, i.ID_PRODUCTO, p.NOMBRE AS PRODUCTO_NOMBRE,
                       i.ID_LOTE, l.CODIGO_LOTE, i.STOCK
                FROM INVENTARIO_LZYM i
                JOIN PRODUCTOS_LZYM p ON i.ID_PRODUCTO = p.ID_PRODUCTO
                JOIN LOTES_LZYM l ON i.ID_LOTE = l.ID_LOTE
            """)
            for row in cursor.fetchall():
                inventario_registros.append({
                    "id": row[0],
                    "producto": {"id": row[1], "nombre": row[2]},
                    "lote": {"id": row[3], "codigo_lote": row[4]},
                    "stock": row[5]
                })
    except cx_Oracle.Error as error:
        print("Error al consultar inventario:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return inventario_registros

def obtener_inventario_por_id_db(id_inventario):
    connection = obtener_conexion()
    cursor = None
    inventario_registro = None
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT i.ID_INVENTARIO, i.ID_PRODUCTO, p.NOMBRE AS PRODUCTO_NOMBRE,
                       i.ID_LOTE, l.CODIGO_LOTE, i.STOCK
                FROM INVENTARIO_LZYM i
                JOIN PRODUCTOS_LZYM p ON i.ID_PRODUCTO = p.ID_PRODUCTO
                JOIN LOTES_LZYM l ON i.ID_LOTE = l.ID_LOTE
                WHERE i.ID_INVENTARIO = :id
            """, id=id_inventario)
            result = cursor.fetchone()
            if result:
                inventario_registro = {
                    "id": result[0],
                    "producto": {"id": result[1], "nombre": result[2]},
                    "lote": {"id": result[3], "codigo_lote": result[4]},
                    "stock": result[5]
                }
    except cx_Oracle.Error as error:
        print(f"Error al obtener registro de inventario con ID {id_inventario}:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return inventario_registro

# Helper para validar si un ID de producto o lote existe
def _id_exists(table_name, id_column, id_value):
    connection = obtener_conexion()
    cursor = None
    exists = False
    try:
        if connection:
            cursor = connection.cursor()
            query = f"SELECT 1 FROM {table_name} WHERE {id_column} = :id"
            cursor.execute(query, id=id_value)
            exists = cursor.fetchone() is not None
    except cx_Oracle.Error as error:
        print(f"Error verificando existencia en {table_name}:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return exists

def crear_inventario_db(id_producto, id_lote, stock):
    connection = obtener_conexion()
    cursor = None
    new_id = None
    try:
        if connection:
            cursor = connection.cursor()
            # Consultar el último ID y agregar 1
            cursor.execute("SELECT NVL(MAX(ID_INVENTARIO), 0) FROM INVENTARIO_LZYM")
            last_id = cursor.fetchone()[0]
            new_id = last_id + 1

            cursor.execute("""
                INSERT INTO INVENTARIO_LZYM (
                    ID_INVENTARIO, ID_PRODUCTO, ID_LOTE, STOCK
                ) VALUES (
                    :id, :id_prod, :id_lote, :stock
                )
            """,
            id=new_id,
            id_prod=id_producto,
            id_lote=id_lote,
            stock=stock)
            connection.commit()
            return new_id
    except cx_Oracle.Error as error:
        connection.rollback()
        print("Error al crear registro de inventario:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return None

def actualizar_inventario_db(id_inventario, id_producto, id_lote, stock):
    connection = obtener_conexion()
    cursor = None
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE INVENTARIO_LZYM SET
                    ID_PRODUCTO = :id_prod,
                    ID_LOTE = :id_lote,
                    STOCK = :stock
                WHERE ID_INVENTARIO = :id
            """,
            id_prod=id_producto,
            id_lote=id_lote,
            stock=stock,
            id=id_inventario)
            if cursor.rowcount > 0:
                connection.commit()
                return True
            else:
                connection.rollback()
                return False
    except cx_Oracle.Error as error:
        connection.rollback()
        print(f"Error al actualizar registro de inventario con ID {id_inventario}:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return False

def eliminar_inventario_db(id_inventario):
    connection = obtener_conexion()
    cursor = None
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM INVENTARIO_LZYM WHERE ID_INVENTARIO = :id", id=id_inventario)
            if cursor.rowcount > 0:
                connection.commit()
                return True
            else:
                connection.rollback()
                return False
    except cx_Oracle.Error as error:
        connection.rollback()
        print(f"Error al eliminar registro de inventario con ID {id_inventario}:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return False

# --- Rutas para INVENTARIO_LZYM ---

@app.route('/api/inventario', methods=['GET'])
def get_inventario():
    inventario_registros = obtener_inventario_db()
    return jsonify(inventario_registros)

@app.route('/api/inventario/<int:id_inventario>', methods=['GET'])
def get_inventario_registro(id_inventario):
    inventario_registro = obtener_inventario_por_id_db(id_inventario)
    if inventario_registro:
        return jsonify(inventario_registro)
    return jsonify({"message": "Registro de inventario no encontrado"}), 404

@app.route('/api/inventario', methods=['POST'])
def crear_inventario():
    data = request.get_json()
    required_fields = ['id_producto', 'id_lote', 'stock']
    if not all(field in data for field in required_fields):
        return jsonify({"message": "Faltan campos requeridos para crear el registro de inventario"}), 400

    id_producto = data['id_producto']
    id_lote = data['id_lote']
    stock = data['stock']

    # Validar IDs de producto y lote
    if not _id_exists('PRODUCTOS_LZYM', 'ID_PRODUCTO', id_producto):
        return jsonify({"message": f"El ID de producto {id_producto} no existe."}), 400
    if not _id_exists('LOTES_LZYM', 'ID_LOTE', id_lote):
        return jsonify({"message": f"El ID de lote {id_lote} no existe."}), 400
    if not isinstance(stock, (int, float)) or stock < 0:
        return jsonify({"message": "El stock debe ser un número positivo."}), 400

    new_id = crear_inventario_db(id_producto, id_lote, stock)
    if new_id:
        inventario_creado = obtener_inventario_por_id_db(new_id)
        return jsonify(inventario_creado), 201
    return jsonify({"message": "Error al crear el registro de inventario"}), 500

@app.route('/api/inventario/<int:id_inventario>', methods=['PUT'])
def actualizar_inventario(id_inventario):
    data = request.get_json()
    required_fields = ['id_producto', 'id_lote', 'stock'] # Se espera que el cliente envíe todos los campos
    if not all(field in data for field in required_fields):
        return jsonify({"message": "Faltan campos requeridos para actualizar el registro de inventario"}), 400

    id_producto = data['id_producto']
    id_lote = data['id_lote']
    stock = data['stock']

    # Validar IDs de producto y lote
    if not _id_exists('PRODUCTOS_LZYM', 'ID_PRODUCTO', id_producto):
        return jsonify({"message": f"El ID de producto {id_producto} no existe."}), 400
    if not _id_exists('LOTES_LZYM', 'ID_LOTE', id_lote):
        return jsonify({"message": f"El ID de lote {id_lote} no existe."}), 400
    if not isinstance(stock, (int, float)) or stock < 0:
        return jsonify({"message": "El stock debe ser un número positivo."}), 400

    if actualizar_inventario_db(id_inventario, id_producto, id_lote, stock):
        inventario_actualizado = obtener_inventario_por_id_db(id_inventario)
        return jsonify(inventario_actualizado)
    return jsonify({"message": "Registro de inventario no encontrado o error al actualizar"}), 404

@app.route('/api/inventario/<int:id_inventario>', methods=['DELETE'])
def eliminar_inventario(id_inventario):
    if eliminar_inventario_db(id_inventario):
        return jsonify({"message": f"Registro de inventario con ID {id_inventario} eliminado"})
    return jsonify({"message": "Registro de inventario no encontrado o error al eliminar"}), 404

# --- Funciones de Reportes de Inventario ---

def obtener_productos_a_vencer_db(dias=30):
    connection = obtener_conexion()
    cursor = None
    productos_a_vencer = []
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute(f"""
                SELECT p.ID_PRODUCTO, p.NOMBRE AS PRODUCTO_NOMBRE,
                       l.CODIGO_LOTE, i.STOCK, l.FECHA_VENCIMIENTO, i.ID_LOTE
                FROM INVENTARIO_LZYM i
                JOIN PRODUCTOS_LZYM p ON i.ID_PRODUCTO = p.ID_PRODUCTO
                JOIN LOTES_LZYM l ON i.ID_LOTE = l.ID_LOTE
                WHERE l.FECHA_VENCIMIENTO BETWEEN TRUNC(SYSDATE) AND TRUNC(SYSDATE + :dias)
                AND i.STOCK > 0 -- Solo productos con stock
                ORDER BY l.FECHA_VENCIMIENTO ASC
            """, dias=dias)
            for row in cursor.fetchall():
                productos_a_vencer.append({
                    "id_producto": row[0],
                    "producto_nombre": row[1],
                    "codigo_lote": row[2],
                    "stock": row[3],
                    "fecha_vencimiento": row[4].strftime('%Y-%m-%d') if row[4] else None,
                    "id_lote": row[5]
                })
    except cx_Oracle.Error as error:
        print("Error al consultar productos a vencer:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return productos_a_vencer

def obtener_productos_menos_stock_db(limite=5):
    connection = obtener_conexion()
    cursor = None
    productos_menos_stock = []
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute(f"""
                SELECT p.ID_PRODUCTO, p.NOMBRE AS PRODUCTO_NOMBRE, SUM(i.STOCK) AS TOTAL_STOCK
                FROM INVENTARIO_LZYM i
                JOIN PRODUCTOS_LZYM p ON i.ID_PRODUCTO = p.ID_PRODUCTO
                GROUP BY p.ID_PRODUCTO, p.NOMBRE
                ORDER BY TOTAL_STOCK ASC, p.NOMBRE ASC
                FETCH FIRST :limite ROWS ONLY
            """, limite=limite)
            for row in cursor.fetchall():
                productos_menos_stock.append({
                    "id_producto": row[0],
                    "producto_nombre": row[1],
                    "total_stock": row[2]
                })
    except cx_Oracle.Error as error:
        print("Error al consultar productos con menos stock:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return productos_menos_stock

def obtener_productos_mayor_stock_db(limite=5):
    connection = obtener_conexion()
    cursor = None
    productos_mayor_stock = []
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute(f"""
                SELECT p.ID_PRODUCTO, p.NOMBRE AS PRODUCTO_NOMBRE, SUM(i.STOCK) AS TOTAL_STOCK
                FROM INVENTARIO_LZYM i
                JOIN PRODUCTOS_LZYM p ON i.ID_PRODUCTO = p.ID_PRODUCTO
                GROUP BY p.ID_PRODUCTO, p.NOMBRE
                ORDER BY TOTAL_STOCK DESC, p.NOMBRE ASC
                FETCH FIRST :limite ROWS ONLY
            """, limite=limite)
            for row in cursor.fetchall():
                productos_mayor_stock.append({
                    "id_producto": row[0],
                    "producto_nombre": row[1],
                    "total_stock": row[2]
                })
    except cx_Oracle.Error as error:
        print("Error al consultar productos con mayor stock:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return productos_mayor_stock

# --- Funciones de Reportes de Valor de Inventario (NUEVAS) ---

def obtener_valor_inventario_total_db():
    connection = obtener_conexion()
    cursor = None
    valor_total = 0.0
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT SUM(i.STOCK * p.PRECIO_COMPRA)
                FROM INVENTARIO_LZYM i
                JOIN PRODUCTOS_LZYM p ON i.ID_PRODUCTO = p.ID_PRODUCTO
                WHERE i.STOCK > 0
            """)
            result = cursor.fetchone()
            if result and result[0] is not None:
                valor_total = float(result[0])
    except cx_Oracle.Error as error:
        print("Error al calcular valor total de inventario:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return {"valor_total": round(valor_total, 2)}

def obtener_valor_inventario_por_categoria_db():
    connection = obtener_conexion()
    cursor = None
    valor_por_categoria = []
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT c.NOMBRE AS CATEGORIA_NOMBRE, SUM(i.STOCK * p.PRECIO_COMPRA) AS VALOR_CATEGORIA
                FROM INVENTARIO_LZYM i
                JOIN PRODUCTOS_LZYM p ON i.ID_PRODUCTO = p.ID_PRODUCTO
                JOIN CATEGORIA_PRODUCTOS_LZYM c ON p.ID_CATEGORIA_PRODUCTO = c.ID_CATEGORIA_PRODUCTO
                WHERE i.STOCK > 0
                GROUP BY c.NOMBRE
                ORDER BY c.NOMBRE ASC
            """)
            for row in cursor.fetchall():
                valor_por_categoria.append({
                    "categoria": row[0],
                    "valor": round(float(row[1]), 2) if row[1] is not None else 0.0
                })
    except cx_Oracle.Error as error:
        print("Error al calcular valor de inventario por categoría:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return valor_por_categoria

def obtener_valor_inventario_por_tipo_db():
    connection = obtener_conexion()
    cursor = None
    valor_por_tipo = []
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT t.NOMBRE AS TIPO_PRODUCTO_NOMBRE, SUM(i.STOCK * p.PRECIO_COMPRA) AS VALOR_TIPO
                FROM INVENTARIO_LZYM i
                JOIN PRODUCTOS_LZYM p ON i.ID_PRODUCTO = p.ID_PRODUCTO
                JOIN TIPO_PRODUCTOS_LZYM t ON p.ID_TIPO_PRODUCTO = t.ID_TIPO_PRODUCTO
                WHERE i.STOCK > 0
                GROUP BY t.NOMBRE
                ORDER BY t.NOMBRE ASC
            """)
            for row in cursor.fetchall():
                valor_por_tipo.append({
                    "tipo_producto": row[0],
                    "valor": round(float(row[1]), 2) if row[1] is not None else 0.0
                })
    except cx_Oracle.Error as error:
        print("Error al calcular valor de inventario por tipo:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return valor_por_tipo

# --- Rutas para Reportes de Inventario ---

@app.route('/api/reportes/inventario/a_vencer', methods=['GET'])
def get_productos_a_vencer():
    dias = request.args.get('dias', default=30, type=int)
    if not (1 <= dias <= 365):
        return jsonify({"message": "El número de días debe ser entre 1 y 365."}), 400
    productos = obtener_productos_a_vencer_db(dias)
    return jsonify(productos)

@app.route('/api/reportes/inventario/menos_stock', methods=['GET'])
def get_productos_menos_stock():
    limite = request.args.get('limite', default=5, type=int)
    if not (1 <= limite <= 100):
        return jsonify({"message": "El límite debe ser entre 1 y 100."}), 400
    productos = obtener_productos_menos_stock_db(limite)
    return jsonify(productos)

@app.route('/api/reportes/inventario/mayor_stock', methods=['GET'])
def get_productos_mayor_stock():
    limite = request.args.get('limite', default=5, type=int)
    if not (1 <= limite <= 100):
        return jsonify({"message": "El límite debe ser entre 1 y 100."}), 400
    productos = obtener_productos_mayor_stock_db(limite)
    return jsonify(productos)

@app.route('/api/reportes/inventario/valor/total', methods=['GET'])
def get_valor_inventario_total():
    valor = obtener_valor_inventario_total_db()
    return jsonify(valor)

@app.route('/api/reportes/inventario/valor/por_categoria', methods=['GET'])
def get_valor_inventario_por_categoria():
    valores = obtener_valor_inventario_por_categoria_db()
    return jsonify(valores)

@app.route('/api/reportes/inventario/valor/por_tipo', methods=['GET'])
def get_valor_inventario_por_tipo():
    valores = obtener_valor_inventario_por_tipo_db()
    return jsonify(valores)



# --- Funciones CRUD para USUARIOS ---

def crear_usuario_db(nombre, clave_plana, estado='Activo', rol='Analista'):
    connection = obtener_conexion()
    cursor = None
    new_id = None
    try:
        if connection:
            cursor = connection.cursor()

            # 1. Encriptar la clave
            hashed_password = generate_password_hash(clave_plana)

            # 2. Generar un nuevo ID (considera secuencias para producción)
            cursor.execute("SELECT NVL(MAX(ID_USUARIO), 0) FROM USUARIOS")
            last_id = cursor.fetchone()[0]
            new_id = last_id + 1

            # 3. Insertar el usuario
            cursor.execute("""
                INSERT INTO USUARIOS (ID_USUARIO, NOMBRE, CLAVE, ESTADO, ROL)
                VALUES (:id, :nombre, :clave, :estado, :rol)
            """,
            id=new_id,
            nombre=nombre,
            clave=hashed_password,
            estado=estado,
            rol=rol)
            connection.commit()
            return new_id
    except cx_Oracle.Error as error:
        connection.rollback()
        # Puedes querer loggear el error más detalladamente en un archivo de log
        print(f"Error al crear usuario: {error}")
        # Verificar si es un error de clave única (nombre de usuario ya existe)
        if "ORA-00001" in str(error): # Código de error para unique constraint violation
            return "DUPLICATE_USERNAME"
        return None
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return None

def obtener_usuario_por_nombre_db(nombre_usuario):
    connection = obtener_conexion()
    cursor = None
    usuario = None
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT ID_USUARIO, NOMBRE, CLAVE, ESTADO, ROL
                FROM USUARIOS
                WHERE NOMBRE = :nombre
            """, nombre=nombre_usuario)
            result = cursor.fetchone()
            if result:
                usuario = {
                    "id": result[0],
                    "nombre": result[1],
                    "clave_hash": result[2], # El hash de la clave
                    "estado": result[3],
                    "rol": result[4]
                }
    except cx_Oracle.Error as error:
        print(f"Error al obtener usuario por nombre: {error}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return usuario

def obtener_usuario_por_id_db(id_usuario):
    connection = obtener_conexion()
    cursor = None
    usuario = None
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT ID_USUARIO, NOMBRE, CLAVE, ESTADO, ROL
                FROM USUARIOS
                WHERE ID_USUARIO = :id
            """, id=id_usuario)
            result = cursor.fetchone()
            if result:
                usuario = {
                    "id": result[0],
                    "nombre": result[1],
                    "clave_hash": result[2],
                    "estado": result[3],
                    "rol": result[4]
                }
    except cx_Oracle.Error as error:
        print(f"Error al obtener usuario por ID: {error}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return usuario

def obtener_todos_los_usuarios_db():
    connection = obtener_conexion()
    cursor = None
    usuarios = []
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT ID_USUARIO, NOMBRE, ESTADO, ROL FROM USUARIOS")
            usuarios = [{"id": row[0], "nombre": row[1], "estado": row[2], "rol": row[3]} for row in cursor.fetchall()]
    except cx_Oracle.Error as error:
        print("Error al consultar todos los usuarios:", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return usuarios

def actualizar_usuario_db(id_usuario, nombre=None, estado=None, rol=None, nueva_clave_plana=None):
    connection = obtener_conexion()
    cursor = None
    try:
        if connection:
            cursor = connection.cursor()
            update_parts = []
            params = {"id": id_usuario}

            if nombre is not None:
                update_parts.append("NOMBRE = :nombre")
                params["nombre"] = nombre
            if estado is not None:
                update_parts.append("ESTADO = :estado")
                params["estado"] = estado
            if rol is not None:
                update_parts.append("ROL = :rol")
                params["rol"] = rol
            if nueva_clave_plana is not None:
                hashed_password = generate_password_hash(nueva_clave_plana)
                update_parts.append("CLAVE = :clave")
                params["clave"] = hashed_password

            if not update_parts: # No hay nada que actualizar
                return False

            query = f"UPDATE USUARIOS SET {', '.join(update_parts)} WHERE ID_USUARIO = :id"
            cursor.execute(query, params)

            if cursor.rowcount > 0:
                connection.commit()
                return True
            else:
                connection.rollback()
                return False
    except cx_Oracle.Error as error:
        connection.rollback()
        print(f"Error al actualizar usuario con ID {id_usuario}: {error}")
        if "ORA-00001" in str(error): # Código de error para unique constraint violation (si se actualiza el nombre a uno existente)
            return "DUPLICATE_USERNAME"
        return None
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return False

def eliminar_usuario_db(id_usuario):
    connection = obtener_conexion()
    cursor = None
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM USUARIOS WHERE ID_USUARIO = :id", id=id_usuario)
            if cursor.rowcount > 0:
                connection.commit()
                return True
            else:
                connection.rollback()
                return False
    except cx_Oracle.Error as error:
        connection.rollback()
        print(f"Error al eliminar usuario con ID {id_usuario}: {error}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return False


# --- Rutas de Autenticación y Gestión de USUARIOS ---

@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    nombre = data.get('nombre')
    clave = data.get('clave')
    rol = data.get('rol', 'Analista') # Rol por defecto si no se especifica

    if not nombre or not clave:
        return jsonify({"message": "El nombre de usuario y la clave son requeridos."}), 400

    if rol not in ['Administrador', 'Analista']:
        return jsonify({"message": "Rol inválido. Los roles permitidos son 'Administrador' o 'Analista'."}), 400

    new_id = crear_usuario_db(nombre, clave, rol=rol)
    if new_id == "DUPLICATE_USERNAME":
        return jsonify({"message": "El nombre de usuario ya existe."}), 409 # Conflict
    elif new_id:
        # No devolver el hash de la clave al cliente
        usuario_creado = obtener_usuario_por_id_db(new_id)
        if usuario_creado:
            del usuario_creado['clave_hash'] # Eliminar el hash antes de enviar
            return jsonify({"message": "Usuario registrado exitosamente", "usuario": usuario_creado}), 201
        return jsonify({"message": "Usuario registrado, pero no se pudo recuperar la información completa."}), 201 # Edge case
    return jsonify({"message": "Error al registrar el usuario."}), 500

@app.route('/api/login', methods=['POST'])
def login_user():
    data = request.get_json()
    nombre = data.get('nombre')
    clave = data.get('clave')

    if not nombre or not clave:
        return jsonify({"message": "El nombre de usuario y la clave son requeridos."}), 400

    usuario = obtener_usuario_por_nombre_db(nombre)

    if usuario and check_password_hash(usuario['clave_hash'], clave):
        # Autenticación exitosa
        # En una aplicación real, aquí generarías un token JWT para mantener la sesión
        # Por ahora, solo devolvemos un mensaje de éxito y el rol del usuario
        return jsonify({
            "message": "Login exitoso",
            "user_id": usuario['id'],
            "username": usuario['nombre'],
            "rol": usuario['rol']
        }), 200
    else:
        return jsonify({"message": "Nombre de usuario o clave incorrectos."}), 401 # Unauthorized

# --- Rutas de Gestión de Usuarios (Requieren autenticación/autorización en un sistema real) ---
# Por ahora, estas rutas no tienen seguridad implementada.
# En un sistema real, un 'Administrador' sería el único que podría usar estas.

@app.route('/api/users', methods=['GET'])
def get_all_users():
    # En un sistema real, solo administradores deberían acceder a esto
    usuarios = obtener_todos_los_usuarios_db()
    # Eliminar el hash de la clave antes de enviar la respuesta
    for user in usuarios:
        if 'clave_hash' in user: # La función obtener_todos_los_usuarios_db no devuelve clave_hash
            del user['clave_hash'] # Pero es buena práctica por si acaso
    return jsonify(usuarios)

@app.route('/api/users/<int:id_usuario>', methods=['GET'])
def get_user_by_id(id_usuario):
    usuario = obtener_usuario_por_id_db(id_usuario)
    if usuario:
        del usuario['clave_hash'] # No enviar el hash
        return jsonify(usuario)
    return jsonify({"message": "Usuario no encontrado"}), 404

@app.route('/api/users/<int:id_usuario>', methods=['PUT'])
def update_user(id_usuario):
    data = request.get_json()
    # No permitir que el cliente envíe el ID, y manejar la clave separadamente
    nombre = data.get('nombre')
    estado = data.get('estado')
    rol = data.get('rol')
    nueva_clave = data.get('clave') # Para actualizar la clave

    if not any([nombre, estado, rol, nueva_clave]):
        return jsonify({"message": "Al menos un campo (nombre, estado, rol, clave) es requerido para actualizar."}), 400

    result = actualizar_usuario_db(id_usuario, nombre=nombre, estado=estado, rol=rol, nueva_clave_plana=nueva_clave)

    if result == "DUPLICATE_USERNAME":
        return jsonify({"message": "El nombre de usuario ya existe."}), 409
    elif result:
        usuario_actualizado = obtener_usuario_por_id_db(id_usuario)
        if usuario_actualizado:
            del usuario_actualizado['clave_hash']
            return jsonify({"message": "Usuario actualizado exitosamente", "usuario": usuario_actualizado})
        return jsonify({"message": "Usuario actualizado, pero no se pudo recuperar la información completa."}), 200 # Edge case
    return jsonify({"message": "Usuario no encontrado o error al actualizar."}), 404

@app.route('/api/users/<int:id_usuario>', methods=['DELETE'])
def delete_user(id_usuario):
    if eliminar_usuario_db(id_usuario):
        return jsonify({"message": f"Usuario con ID {id_usuario} eliminado."})
    return jsonify({"message": "Usuario no encontrado o error al eliminar."}), 404


if __name__ == '__main__':
    app.run(debug=True)