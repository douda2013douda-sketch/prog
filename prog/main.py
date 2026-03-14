from database import Database
from generate_pdf import PDFGenerator

db = Database()

# طلب الرقم التعريفي من المستخدم
national_id = input("ادخل الرقم التعريفي للموظف: ")

employee = db.find_employee_by_id(national_id)

if employee is None:
    print("الموظف غير موجود")
    exit()

leaves = db.get_employee_leaves(national_id)

if not leaves:
    print("لا توجد إجازات لهذا الموظف")
    exit()

leave = leaves[0]  # نأخذ أول إجازة

generator = PDFGenerator("leave_template.tex")

generator.generate(employee, leave)

print("تم إنشاء ملف PDF بنجاح")
