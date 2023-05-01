import mysql.connector

db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='MYPASS',
    auth_plugin='mysql_native_password',
)

cursor = db.cursor()

cursor.execute("CREATE TABLE Persons ( name VARCHAR(50) )")
print("Table created")