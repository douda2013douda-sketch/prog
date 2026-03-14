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
            template = Template(f.read())

        data = {
            "employee": employee,
            "leave": leave
        }

        tex_file = "temp.tex"

        with open(tex_file, "w", encoding="utf-8") as f:
            f.write(template.render(data))

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
