import google.generativeai as genai
import mysql.connector
from config import GEMINI_API_KEY, DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

# Load your Gemini API key from config
from config import GEMINI_API_KEY
genai.configure(api_key= GEMINI_API_KEY)

def prompt_to_sql(prompt):
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(f"""
    You are a SQL expert. Convert this hospital-related question into a MySQL query.
    Database tables: doctors, patients, appointments, departments, rooms, bills, medicines, staff, lab_tests, etc.
    Natural language: {prompt}
    SQL query:
    """)
    return response.text.strip()

def execute_query(sql_query):
    con = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
        )
    cr = con.cursor()
    cr.execute(sql_query)
    result = cr.fetchall()
    con.close()
    return result 