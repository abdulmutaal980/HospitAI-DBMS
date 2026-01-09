import customtkinter as ctk
from tkinter import messagebox, ttk
from PIL import Image, ImageEnhance
import google.generativeai as genai
import mysql.connector
from config import GEMINI_API_KEY
from config import GEMINI_API_KEY, DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

#  Configure Gemini API 
genai.configure(api_key=GEMINI_API_KEY)

#  Database schema reference 
DB_SCHEMA = """
Tables and columns in the hospital_ai database:
departments(dept_id, dept_name, location)
doctors(doctor_id, name, gender, phone, specialization, dept_id, experience, available_time)
patients(patient_id, name, gender, age, city, contact)
appointments(appointment_id, patient_id, doctor_id, appointment_date, status)
rooms(room_id, room_type, availability, charges_per_day)
admissions(admission_id, patient_id, room_id, admit_date, discharge_date)
bills(bill_id, patient_id, amount, status, bill_date)
medicines(med_id, med_name, category, price, stock)
prescriptions(prescription_id, patient_id, doctor_id, med_id, dosage, duration)
lab_tests(test_id, patient_id, test_name, result, test_date)
staff(staff_id, name, role, shift, salary)
users(user_id, username, password, role)
doctor_summary(doctor_id, doctor_name, specialization, experience, dept_name, available_time)
"""

# Global variable for user role

USER_ROLE = None  # 'admin' or 'user'

#  Functions for AI DBMS 
def prompt_to_sql(prompt):
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(f"""
    You are a MySQL expert AI assistant that converts natural language questions into valid and safe MySQL queries for the hospital_ai database.
    Rules:
    1. Use only the tables and columns provided below.
    2. If the question involves names, cities, roles, or categories, use LIKE '%value%' instead of '='.
    3. If the question mentions a medical specialty like 'Cardiology', match it to 'Cardiologist' or similar.
    4. Use 'Yes' and 'No' for availability columns, 'Paid' and 'Unpaid' for status.
    5. Generate clean SQL only (no markdown, no code blocks).
    6. You can UPDATE, DELETE, DROP, INSERT, or TRUNCATE — as per user demands.
    7. Use JOINs where needed.
    8. End the query with a semicolon.

    Database schema:
    {DB_SCHEMA}

    Question: {prompt}
    SQL query:
    """)
    sql = response.text.replace("\nsql", "").replace("\n", "").strip()
    return sql

def execute_query(sql_query):
    try:
        con = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
            )
        cr = con.cursor()
        cr.execute(sql_query)

        if sql_query.strip().lower().startswith("select"):
            result = cr.fetchall()
            columns = [desc[0] for desc in cr.description]
        else:
            con.commit()
            result, columns = [("✅ Query executed successfully",)], ["Message"]

        con.close()
        return columns, result

    except Exception as e:
        return ["Error"], [(str(e),)]
    

#  Main DBMS Window 
def open_main_window():
    app = ctk.CTk()
    app.geometry('950x600')
    app.title("HospitAI - Intelligent Hospital DBMS")
    app.configure(fg_color="#102b3f")

    # Title
    img = ctk.CTkImage(Image.open('images(5).jfif'), size=(60, 60))
    l1 = ctk.CTkLabel(
        app,
    text="HospitAI",
    text_color="white",
    fg_color="#0d5172",
    height=60,
    width=280,
    font=("Arial Rounded MT Bold", 28),
    corner_radius=8,
    anchor="center",
    image=img,
    compound='left',
    padx=15
    )
    l1.pack(pady=(20, 5))

    role_color = "#00ffcc" if USER_ROLE == "admin" else "#ffcc00"
    ctk.CTkLabel(app, text=f"Welcome — Logged in as {USER_ROLE.upper()}",
                 text_color=role_color, font=("Century Gothic", 16, "bold")).pack(pady=(0, 10))
    

    container = ctk.CTkFrame(app, fg_color="#102b3f")
    container.pack(fill="both", expand=True, padx=20, pady=(10, 20))
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure((0, 1), weight=1)

    # Left Panel
    frame1 = ctk.CTkFrame(container, corner_radius=20, fg_color="#144e75", border_width=3, border_color="#1fa1b9")
    frame1.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nsew")
    ctk.CTkLabel(frame1, text="Ask a Question:", text_color="white", font=("Segoe UI", 16, "bold")).pack(pady=10)

    console = ctk.CTkTextbox(frame1, height=100)
    console.pack(expand=True, fill="both", padx=10, pady=10)
    console.insert("1.0", "")
    console.configure(state="normal")

    # Right Panel with Treeview
    frame2 = ctk.CTkFrame(container, corner_radius=20, fg_color="#0f3f5a", border_width=3, border_color="#1fa1b9")
    frame2.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="nsew")
    ctk.CTkLabel(frame2, text="Results:", text_color="white", font=("Segoe UI", 16, "bold")).pack(pady=10)

    #  Treeview setup 
    tree_container = ctk.CTkFrame(frame2, fg_color="#0f3f5a")
    tree_container.pack(expand=True, fill="both", padx=10, pady=10)

    tree_scroll = ctk.CTkScrollbar(tree_container, orientation="vertical")
    tree_scroll.pack(side="right", fill="y")

    tree = ttk.Treeview(tree_container, yscrollcommand=tree_scroll.set)
    tree.pack(expand=True, fill="both", side="left")
    tree_scroll.configure(command=tree.yview)

    # Treeview styling
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"), foreground="black")
    style.configure("Treeview", font=("Segoe UI", 11), rowheight=25,
                    fieldbackground="#0f3f5a", background="#0f3f5a", foreground="white", bordercolor="black", relief="solid")
    style.map('Treeview', background=[('selected', '#1fa1b9')], foreground=[('selected', 'white')])

    # Execute
    def click():
        user_prompt = console.get("1.0", "end").strip()
        if not user_prompt:
            return

        sql = prompt_to_sql(user_prompt)
        lower_sql = sql.lower()

        # Restrict modifications for normal users
        restricted_words = ["delete", "drop", "truncate", "update", "insert"]
        if USER_ROLE != "admin" and any(word in lower_sql for word in restricted_words):
            messagebox.showerror("Access Denied", " You are not allowed to modify data. (Read-Only User)")
            return

        # Ask admin before deletion
        if USER_ROLE == "admin" and any(word in lower_sql for word in ["delete", "drop", "truncate"]):
            if not messagebox.askyesno("Warning", "⚠️ This will permanently delete data. Continue?"):
                return

        columns, rows = execute_query(sql)
        if columns == ["Error"]:
            messagebox.showerror("Error", rows[0][0])
            return
        if not rows:
            messagebox.showinfo("Info", "✅ No results found.")
            return

        # Clear previous treeview
        for item in tree.get_children():
            tree.delete(item)

        # Setup columns
        tree["columns"] = columns
        tree["show"] = "headings"
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")

        # Insert rows
        for row in rows:
            tree.insert("", "end", values=row)

        console.delete("1.0", "end")

    ctk.CTkButton(frame1, text="↑", command=click).pack(pady=(10, 10))
    console.bind("<Return>", lambda event: click())

    app.mainloop()

#  LOGIN PAGE 
def login_page():
    global USER_ROLE

    ctk.set_appearance_mode("light")
    login = ctk.CTk()
    login.geometry("900x520")
    login.title("HospitAI - Login")

    # Left side with image
    left_frame = ctk.CTkFrame(login, width=450, height=520, corner_radius=0)
    left_frame.pack(side="left", fill="both", expand=False)

    try:
        bg_image = Image.open("Screenshot 2025-11-13 111947.png")
        bg_image = ImageEnhance.Brightness(bg_image).enhance(1)
        bg_img = ctk.CTkImage(bg_image, size=(450, 520))
        bg_label = ctk.CTkLabel(left_frame, text="", image=bg_img)
        bg_label.place(relx=0.5, rely=0.5, anchor="center")
    except Exception as e:
        ctk.CTkLabel(left_frame, text=f"Image Error:\n{e}", text_color="red").pack(expand=True)

    # Right side login form
    right_frame = ctk.CTkFrame(login, width=450, height=520, fg_color="white", corner_radius=25)
    right_frame.pack(side="right", fill="both", expand=True, padx=30, pady=30)

    brand = ctk.CTkLabel(right_frame, text="HospitAI", text_color="#3B0CA3", font=("Poppins ExtraBold", 32))
    brand.pack(pady=(40, 0))

    ctk.CTkLabel(right_frame, text="Welcome Back!", text_color="#3b0ca3", font=("Poppins SemiBold", 24)).pack(pady=(20, 5))
    ctk.CTkLabel(right_frame, text="Sign in to your account", text_color="#666666", font=("Poppins", 14)).pack(pady=(0, 30))

    username_entry = ctk.CTkEntry(right_frame, placeholder_text="Username", width=300, height=40, corner_radius=12, fg_color="#f4f4f4", border_color="#cccccc", text_color="black")
    username_entry.pack(pady=10)

    password_entry = ctk.CTkEntry(right_frame, placeholder_text="Password", show="*", width=300, height=40, corner_radius=12, fg_color="#f4f4f4", border_color="#cccccc", text_color="black")
    password_entry.pack(pady=10)

    def authenticate():
        global USER_ROLE
        username = username_entry.get().strip().lower()
        password = password_entry.get().strip()

        if username == "admin" and password == "admin123":
            USER_ROLE = "admin"
            messagebox.showinfo("Login Successful", "Welcome, Admin!")
            login.destroy()
            open_main_window()
        elif username == "user" and password == "user123":
            USER_ROLE = "user"
            messagebox.showinfo("Login Successful", "Welcome, User!")
            login.destroy()
            open_main_window()
        else:
            messagebox.showerror("Invalid Credentials", "Incorrect username or password!")

    ctk.CTkButton(right_frame, text="Login", command=authenticate, width=300, height=40, corner_radius=12, fg_color="#3b0ca3", hover_color="#5d2ff5", font=("Poppins SemiBold", 16)).pack(pady=(25, 15))

    ctk.CTkLabel(right_frame, text="HospitAI © 2025", text_color="#888888", font=("Poppins", 11)).pack(side="bottom", pady=15)

    login.mainloop()

# Run the app 
if __name__ == "__main__":
    login_page()