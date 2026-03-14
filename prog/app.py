from flask import Flask, render_template, request, send_file
from database import Database
from generate_pdf import PDFGenerator
from models import Employee, Leave
from datetime import datetime

app = Flask(__name__)

db = Database()
generator = PDFGenerator("leave_template.tex")

# قائمة الإجازات المؤقتة
leaves_list = []


# الصفحة الرئيسية
@app.route("/")
def home():
    return render_template("index.html")


# صفحة عرض الموظفين
@app.route("/employees", methods=["GET", "POST"])
def employees():

    message = ""

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add":
            national_id = request.form["national_id_input"]
            number = request.form["number"]
            num_file = request.form["num_file"]
            first_name = request.form["first_name"]
            last_name = request.form["last_name"]
            direction = request.form["direction"]
            job = request.form["job"]
            title = request.form["title"]
            department = request.form["department"]

            employee = Employee(national_id, number, num_file, first_name, last_name, direction, job, title, department)
            db.add_employee(employee)
            message = "تمت إضافة الموظف بنجاح"

        elif action == "edit":
            old_national_id = request.form["national_id"]
            new_national_id = request.form["national_id_input"]
            number = request.form["number"]
            num_file = request.form["num_file"]
            first_name = request.form["first_name"]
            last_name = request.form["last_name"]
            direction = request.form["direction"]
            job = request.form["job"]
            title = request.form["title"]
            department = request.form["department"]

            if old_national_id != new_national_id:
                # إذا تغير الرقم التعريفي، احذف القديم وأضف جديد
                db.delete_employee(old_national_id)
                employee = Employee(new_national_id, number, num_file, first_name, last_name, direction, job, title, department)
                db.add_employee(employee)
                message = "تم تحديث الموظف بنجاح (تم تغيير الرقم التعريفي)"
            else:
                employee = Employee(new_national_id, number, num_file, first_name, last_name, direction, job, title, department)
                db.update_employee(employee)
                message = "تم تحديث الموظف بنجاح"

        elif action == "delete":
            national_id = request.form["national_id"]
            db.delete_employee(national_id)
            message = "تم حذف الموظف بنجاح"

    db.cursor.execute("SELECT * FROM employees")
    rows = db.cursor.fetchall()

    return render_template("employees.html", employees=rows, message=message)


# صفحة تحرير الإجازة
@app.route("/leave", methods=["GET", "POST"])
def leave():

    message = ""

    if request.method == "POST":

        action = request.form.get("action")

        # إضافة إجازة للقائمة
        if action == "add":

            national_id = request.form["national_id"].strip()

            employee = db.find_employee_by_id(national_id)

            if not employee:
                message = "الموظف غير موجود"

            else:

                year = datetime.now().year
                serial = db.get_next_serial(year)

                issued_in = request.form["issued_in"]
                start_date = request.form["start_date"]
                end_date = request.form["end_date"]
                status = "صالح"

                leave = Leave(
                    None,
                    serial,
                    year,
                    national_id,
                    issued_in,
                    start_date,
                    end_date,
                    status
                )

                # إضافة إلى القائمة المؤقتة
                leaves_list.append(leave)

                message = "تمت إضافة الإجازة إلى القائمة"

        # طباعة جميع الإجازات
        if action == "print":

            for leave in leaves_list:

                employee = db.find_employee_by_id(leave.national_id)

                db.add_leave(leave)

                generator.generate(employee, leave)

            leaves_list.clear()

            message = "تم إنشاء جميع ملفات PDF"


    db.cursor.execute("SELECT * FROM employees")
    rows = db.cursor.fetchall()

    return render_template(
        "leave.html",
        employees=rows,
        leaves_list=leaves_list,
        message=message
    )


if __name__ == "__main__":
    app.run(debug=True)
