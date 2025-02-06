import mysql.connector

database = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    database="clinica"

)


print(database)
print("conexion exitosa")

cursor=database.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS clinica")