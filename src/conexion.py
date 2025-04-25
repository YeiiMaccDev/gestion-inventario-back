import cx_Oracle

# Detalles de conexión a la base de datos
db_user = "ADMIN_INV"
db_password = "LZYM123"
db_host = "localhost"
db_port = 1521
db_sid = "xe" 

try:
    # Crear una cadena de conexión
    dsn_tns = cx_Oracle.makedsn(db_host, db_port, sid=db_sid)
    connection = cx_Oracle.connect(db_user, db_password, dsn_tns)

    # Crear un cursor para ejecutar consultas
    cursor = connection.cursor()

    # Ejemplo de consulta
    cursor.execute("SELECT * FROM lotes_lzym")
    results = cursor.fetchall()

    for row in results:
        print(row)

except cx_Oracle.Error as error:
    print("Error al conectar a la base de datos Oracle:", error)

finally:
    # Cerrar el cursor y la conexión
    if cursor:
        cursor.close()
    if connection:
        connection.close()