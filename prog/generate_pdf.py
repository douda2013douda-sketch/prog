import os
import subprocess
from jinja2 import Template
from pypdf import PdfWriter


class PDFGenerator:

    def __init__(self, template_path):

        self.template_path = template_path

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = os.path.join(BASE_DIR, "leaves")

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)


    def generate(self, employee, leave):

        with open(self.template_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        # حساب المتغيرات
        slash1 = "" if employee.title == "سجل غمد" else "\\slash"
        slash2 = "" if employee.title == "سامط بف" else "\\slash"
        slash3 = "" if employee.title == "سامط" else "\\slash"

        type1 = "" if leave.leave_type == "تمديد اجازة" else "\\type"
        type2 = "" if leave.leave_type == "نقاهة" else "\\type"
        type3 = "" if leave.leave_type == "عطلة" else "\\type"
        type4 = "" if leave.leave_type == "إجازة" else "\\type"

        # قاموس المتغيرات
        variables = {
            "leave_num": leave.document_number(),
            "national_id": employee.national_id,
            "department": employee.department,
            "title": employee.title,
            "name": employee.last_name,  # اللقب
            "last_name": employee.first_name,  # الإسم
            "job": employee.job,
            "duration": str(leave.duration()),
            "start-date": leave.start_date,
            "end_date": leave.end_date,
            "direction": employee.direction,
            "signature_date": leave.signature_date,
            "SLASH1": slash1,
            "SLASH2": slash2,
            "SLASH3": slash3,
            "type1": type1,
            "type2": type2,
            "type3": type3,
            "type4": type4,
        }

        # استبدال \VAR{var} بقيم
        for var, value in variables.items():
            template_content = template_content.replace(f"\\VAR{{{var}}}", str(value))

        tex_file = "temp.tex"

        with open(tex_file, "w", encoding="utf-8") as f:
            f.write(template_content)

        subprocess.run(["xelatex", "-interaction=nonstopmode", tex_file])

        # اسم الملف الاحترافي
        doc_number = f"{leave.year}-{leave.serial_number:05d}"
        filename = f"{doc_number}_{employee.first_name}_{employee.last_name}.pdf"

        output_path = os.path.join(self.output_dir, filename)

        # نقل ملف PDF
        if os.path.exists("temp.pdf"):
            os.rename("temp.pdf", output_path)

        # حذف الملفات المؤقتة
        for ext in ["aux", "log", "tex"]:
            file = f"temp.{ext}"
            if os.path.exists(file):
                os.remove(file)

        return output_path

    def merge_pdfs(self, pdf_files, output_path):

        writer = PdfWriter()

        for pdf in pdf_files:
            writer.append(pdf)

        with open(output_path, "wb") as f:
            writer.write(f)

        return output_path
