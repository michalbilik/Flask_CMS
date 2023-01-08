#this scripts creates the DB
import mysql.connector 

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="password123",
)

my_cursor = mydb.cursor()

#my_cursor.execute("CREATE DATABASE our_users") - uncomment to create a new dabatase, but change the name of it

my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
    print(db)