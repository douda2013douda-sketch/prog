import sqlite3

conn = sqlite3.connect("employees.db")
cursor = conn.cursor()

# تفعيل العلاقات
cursor.execute("PRAGMA foreign_keys = ON")

cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (

    national_id TEXT PRIMARY KEY,
    number INTEGER UNIQUE,
    num_file TEXT,
    first_name TEXT,
    last_name TEXT,
    direction TEXT,
    job TEXT,
    title TEXT,
    department TEXT

)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS leaves (

    number INTEGER PRIMARY KEY AUTOINCREMENT,
    serial_number INTEGER,
    year INTEGER,

    national_id TEXT,

    issued_in TEXT,
    start_date TEXT,
    end_date TEXT,
    document_status TEXT,

    FOREIGN KEY (national_id)
    REFERENCES employees(national_id)

)
""")

conn.commit()
conn.close()

print("Database created successfully")
