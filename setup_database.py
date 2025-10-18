import sqlite3
import os

DB_FILE = "societe.db"

# Delete the old database file if it exists, to start fresh
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

# Connect to the database (this will create the file)
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# --- Create the 'employees' table ---
cursor.execute('''
    CREATE TABLE employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
''')
print("Table 'employees' created successfully.")

# --- Create the 'attendance' table ---
cursor.execute('''
    CREATE TABLE attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        timestamp DATETIME NOT NULL,
        FOREIGN KEY (employee_id) REFERENCES employees (id)
    )
''')
print("Table 'attendance' created successfully.")


# This is how you'll add new people.
employees_to_add = ['mohamed', 'azza', 'hanem', 'eya', 'adel','alma','mamoun'] # Use the same names as your folder names
for employee_name in employees_to_add:
    try:
        cursor.execute("INSERT INTO employees (name) VALUES (?)", (employee_name,))
        print(f"Added employee: {employee_name}")
    except sqlite3.IntegrityError:
        print(f"Employee {employee_name} already exists.")


# Commit the changes and close the connection
conn.commit()
conn.close()

print("\nDatabase setup complete. The file 'societe.db' is ready.")