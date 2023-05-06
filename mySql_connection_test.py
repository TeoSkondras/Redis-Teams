import mysql.connector

db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='mypass',
    auth_plugin='mysql_native_password',
    database="users_meetings"
)

cursor = db.cursor()

cursor.execute("SELECT * FROM users")


for row in cursor:
    print(row)