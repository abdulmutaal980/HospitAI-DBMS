HospitAI – Intelligent Hospital DBMS

HospitAI is an intelligent desktop-based hospital management system designed to streamline hospital operations and simplify data management. Built with CustomTkinter for the graphical interface and MySQL for backend data storage, it provides an interactive platform for managing patients, doctors, appointments, rooms, prescriptions, lab tests, bills, and staff information.

The project demonstrates how different parts of an application—UI, logic, and database—work together in a practical scenario. Users interact with the system through a modern, user-friendly interface that allows them to ask questions in natural language or enter SQL queries directly. The system then processes these queries, executes them against the database, and displays the results in an organized table format.

HospitAI supports role-based access control:

Admin users can perform all operations including adding, updating, and deleting records, making it suitable for hospital staff responsible for maintaining the database.

Normal users have read-only access, allowing them to view information without making changes.

The system also integrates optional AI-assisted query generation, where natural language questions are converted into valid SQL queries. This feature helps users who may not be familiar with SQL to interact with the database efficiently.

Key features of HospitAI include:

1. Management of all core hospital entities like patients, doctors, rooms, appointments, prescriptions, and lab tests.

2. Secure login system to differentiate between admins and standard users.

3. Interactive results display using tables for clear and organized data visualization.

4. Safety measures for destructive actions, including confirmation prompts for deletion, dropping, or truncating data.

5. A modular design that showcases the connection between GUI elements, backend logic, and database operations.

Overall, HospitAI is both a functional hospital DBMS and a learning project, illustrating how to combine front-end design, backend logic, and data management in a real-world application.