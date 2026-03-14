import os
import sqlite3
from models import Employee, Leave


class Database:

    def __init__(self, db_name="employees.db"):

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, db_name)

        print("Database path:", db_path)

        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()

        # تفعيل العلاقات
        self.cursor.execute("PRAGMA foreign_keys = ON")

        self.create_tables()
    def create_tables(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (

            national_id TEXT PRIMARY KEY,
            number INTEGER,
            num_file TEXT,
            first_name TEXT,
            last_name TEXT,
            direction TEXT,
            job TEXT,
            title TEXT,
            department TEXT

        )
        """)

        self.cursor.execute("""
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

        self.conn.commit()


    def add_employee(self, employee):

        self.cursor.execute("""
        INSERT INTO employees (
            national_id,
            number,
            num_file,
            first_name,
            last_name,
            direction,
            job,
            title,
            department
        )
        VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            employee.national_id,
            employee.number,
            employee.num_file,
            employee.first_name,
            employee.last_name,
            employee.direction,
            employee.job,
            employee.title,
            employee.department
        ))

        self.conn.commit()


    def update_employee(self, employee):

        self.cursor.execute("""
        UPDATE employees SET
            number=?,
            num_file=?,
            first_name=?,
            last_name=?,
            direction=?,
            job=?,
            title=?,
            department=?
        WHERE national_id=?
        """, (
            employee.number,
            employee.num_file,
            employee.first_name,
            employee.last_name,
            employee.direction,
            employee.job,
            employee.title,
            employee.department,
            employee.national_id
        ))

        self.conn.commit()


    def delete_employee(self, national_id):

        self.cursor.execute("DELETE FROM employees WHERE national_id=?", (national_id,))
        self.conn.commit()


    def find_employee_by_id(self, national_id):

        self.cursor.execute("""
        SELECT * FROM employees WHERE national_id=?
        """, (national_id,))

        row = self.cursor.fetchone()

        if row:
            return Employee(*row)

        return None


    def find_employee_by_name(self, name):

        self.cursor.execute("""
        SELECT * FROM employees WHERE first_name LIKE ?
        """, (f"%{name}%",))

        rows = self.cursor.fetchall()

        return [Employee(*row) for row in rows]


    def add_leave(self, leave):

        self.cursor.execute("""
        INSERT INTO leaves (
            serial_number,
            year,
            national_id,
            issued_in,
            start_date,
            end_date,
            document_status
        )
        VALUES (?,?,?,?,?,?,?)
        """, (
            leave.serial_number,
            leave.year,
            leave.national_id,
            leave.issued_in,
            leave.start_date,
            leave.end_date,
            leave.document_status
        ))

        self.conn.commit()


    def get_employee_leaves(self, national_id):

        self.cursor.execute("""
        SELECT * FROM leaves WHERE national_id=?
        """, (national_id,))

        rows = self.cursor.fetchall()

        return [Leave(*row) for row in rows]

    def get_next_serial(self, year):

        self.cursor.execute("""
        SELECT MAX(serial_number)
        FROM leaves
        WHERE year=?
        """, (year,))

        result = self.cursor.fetchone()

        if result is None or result[0] is None:
            return 1

        return result[0] + 1
