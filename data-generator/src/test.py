import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="admin",
    database="cdc_db"
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM order_reviews")
rows = cursor.fetchall()

for row in rows:
    print(row)

cursor.close()
conn.close()