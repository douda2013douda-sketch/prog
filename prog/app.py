from flask import Flask, render_template, request, send_file
from database import Database
from generate_pdf import PDFGenerator
from models import Employee, Leave
from datetime import datetime
import os

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
            num_file = request.form["num_file"]
            first_name = request.form["first_name"]
            last_name = request.form["last_name"]
            direction = request.form["direction"]
            job = request.form["job"]
            title = request.form["title"]
            department = request.form["department"]

            employee = Employee(national_id, None, num_file, first_name, last_name, direction, job, title, department)
            db.add_employee(employee)
            message = "تمت إضافة الموظف بنجاح"

        elif action == "edit":
            number = request.form["number"]
            old_national_id = request.form["national_id_input"]  # wait, no, since it's the same field
            new_national_id = request.form["national_id_input"]
            num_file = request.form["num_file"]
            first_name = request.form["first_name"]
            last_name = request.form["last_name"]
            direction = request.form["direction"]
            job = request.form["job"]
            title = request.form["title"]
            department = request.form["department"]

            # For edit, national_id is the new one, but since it's the same field, we need to check if it changed
            # But since we don't have old, perhaps always update
            employee = Employee(number, new_national_id, num_file, first_name, last_name, direction, job, title, department)
            db.update_employee(employee)
            message = "تم تحديث الموظف بنجاح"

        elif action == "delete":
            number = request.form["number"]
            db.delete_employee(number)
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

        # طباعة إجازة منفردة
        elif action == "print_single":

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

                # إضافة إلى القاعدة
                db.add_leave(leave)

                # إنشاء PDF
                pdf_path = generator.generate(employee, leave)

                # بيانات للطباعة
                leaves_data = [{'employee': employee, 'leave': leave}]

                return render_template("print_leaves.html", leaves_data=leaves_data)

        # طباعة جميع الإجازات
        if action == "print":

            leaves_data = []

            pdf_files = []

            for leave in leaves_list:

                employee = db.find_employee_by_id(leave.national_id)

                db.add_leave(leave)

                pdf_path = generator.generate(employee, leave)

                pdf_files.append(pdf_path)

                leaves_data.append({'employee': employee, 'leave': leave})

            # دمج PDFs
            merged_pdf = os.path.join(generator.output_dir, "merged_leaves.pdf")
            generator.merge_pdfs(pdf_files, merged_pdf)

            leaves_list.clear()

            # حذف الملف المجمع بعد الطباعة (لأن الملفات المنفصلة محفوظة)
            # لكن لنحتفظ به مؤقتاً للتحميل إذا لزم الأمر
            # os.remove(merged_pdf)  # يمكن تفعيله إذا أردت الحذف الفوري

            return render_template("print_leaves.html", leaves_data=leaves_data)


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

@app.route("/download_merged")
def download_merged():
    merged_pdf = os.path.join(generator.output_dir, "merged_leaves.pdf")
    if os.path.exists(merged_pdf):
        response = send_file(merged_pdf, as_attachment=True)
        # حذف الملف بعد التحميل
        os.remove(merged_pdf)
        return response
    else:
        return "الملف غير موجود", 404
