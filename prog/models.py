class Employee:

    def __init__(self, national_id, number, num_file,
                 first_name, last_name,
                 direction, job, title, department):

        self.national_id = national_id
        self.number = number
        self.num_file = num_file
        self.first_name = first_name
        self.last_name = last_name
        self.direction = direction
        self.job = job
        self.title = title
        self.department = department

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def to_dict(self):
        return self.__dict__


class Leave:

    def __init__(self, number, serial_number, year, national_id,
                 issued_in, start_date, end_date, document_status):

        self.number = number
        self.serial_number = serial_number
        self.year = year
        self.national_id = national_id
        self.issued_in = issued_in
        self.start_date = start_date
        self.end_date = end_date
        self.document_status = document_status

    def to_dict(self):
        return self.__dict__
    def document_number(self):

        return f"{self.year}/{self.serial_number:05d}"
