import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="password123",
    database="our_users"
)

mycursor = mydb.cursor()
#mycursor.execute("TRUNCATE TABLE users") #- truncate table
mycursor.execute("SELECT * FROM users") #- show table content

myresult = mycursor.fetchall()

for x in myresult:
  print(x)