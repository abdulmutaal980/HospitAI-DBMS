import mysql.connector
from config import GEMINI_API_KEY, DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

print(" MySQL connector working!")


con1 = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)

print("Connected Successfully!")
cr = con1.cursor()
cr.execute("UPDATE bills SET amount = 9999 WHERE bill_id = 1;")
con1.commit()                              
cr.execute("SELECT * FROM bills;")

for i in cr:
    print(i)
