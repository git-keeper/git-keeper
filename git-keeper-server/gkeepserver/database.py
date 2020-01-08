# Copyright 2019 Nathan Sommer and Ben Coleman
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import peewee as pw

from gkeepcore.valid_names import cleanup_string, validate_username
from gkeepserver.faculty import Faculty
from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.student import Student


class DatabaseException(GkeepException):
    pass


def username_from_email(email_address: str):
    try:
        username, domain = email_address.split('@')
    except ValueError:
        error = ('{0} does not appear to be a valid email address'
                 .format(email_address))
        raise DatabaseException(error)

    return username


database = pw.SqliteDatabase(None)


class BaseModel(pw.Model):
    class Meta:
        database = database


class User(BaseModel):
    email = pw.CharField(unique=True)
    username = pw.CharField(unique=True)
    role = pw.CharField()
    first_name = pw.CharField()
    last_name = pw.CharField()


class Admin(BaseModel):
    faculty_id = pw.ForeignKeyField(User, backref='faculty', unique=True)


class Class(BaseModel):
    name = pw.CharField()
    faculty_id = pw.ForeignKeyField(User, backref='faculty')
    open = pw.BooleanField()

    class Meta:
        indexes = (
            (('name', 'faculty_id'), True),
        )


class ClassStudent(BaseModel):
    class_id = pw.ForeignKeyField(Class, backref='class')
    student_id = pw.ForeignKeyField(User, backref='student')

    class Meta:
        indexes = (
            (('class_id', 'student_id'), True),
        )


class Assignment(BaseModel):
    name = pw.CharField()
    class_id = pw.ForeignKeyField(Class, backref='class')
    published = pw.BooleanField()

    class Meta:
        indexes = (
            (('name', 'class_id'), True),
        )


class ByteCount(BaseModel):
    file_path = pw.CharField(unique=True)
    byte_count = pw.IntegerField()


class Database:
    def connect(self, db_filename):
        database.init(db_filename, pragmas={'foreign_keys': 1})
        database.create_tables([User, Admin, Class, ClassStudent, Assignment,
                                ByteCount])

    def username_exists(self, username):
        query = User.select().where(User.username == username)
        return query.exists()

    def email_exists(self, email_address):
        query = User.select().where(User.email == email_address)
        return query.exists()

    def class_exists(self, class_name, faculty_username):
        query = Class.select().join(User).where(
            (Class.name == class_name) &
            (Class.faculty_id == User.id) &
            (User.username == faculty_username)
        )
        return query.exists()

    def insert_student(self, student: Student):
        username = self.insert_user(student.email_address, student.first_name,
                                    student.last_name, 'student')
        return username

    def insert_faculty(self, faculty: Faculty):
       username = self.insert_user(faculty.email_address, faculty.first_name,
                                   faculty.last_name, 'faculty')
       return username

    def insert_user(self, email_address: str, first_name: str,
                    last_name: str, role: str):
        if self.email_exists(email_address):
            error = 'A user with the email address {} already exists'
            raise DatabaseException(error)

        original_username = username_from_email(email_address)
        clean_username = cleanup_string(original_username, is_username=True)

        validate_username(clean_username)

        username = clean_username

        counter = 1
        while self.username_exists(username):
            username = clean_username + str(counter)
            counter += 1

        User.create(username=username, email=email_address,
                    first_name=first_name, last_name=last_name,
                    role=role)

        return username

    def get_faculty_by_username(self, username: str) -> Faculty:
        try:
            user = User.get((User.username == username) &
                            (User.role == 'faculty'))
            admin = self.is_admin(username)
            return Faculty(user.last_name, user.first_name, user.username,
                           user.email, admin)
        except User.DoesNotExist:
            error = 'No faculty user with the username {}'.format(username)
            raise DatabaseException(error)

    def get_all_faculty(self):
        faculty_objects = []

        query = (User.select().
                 join(Admin, pw.JOIN.LEFT_OUTER, on=(User.id == Admin.faculty_id)))

        for result in query:
            admin = result.faculty_id is not None

            faculty_objects.append(
                Faculty(result.last_name, result.first_name, result.username,
                        result.email_address, admin=admin)
            )

        return faculty_objects

    def is_admin(self, username: str):
        query = User.select().join(Admin).where(User.username == username)
        return query.exists()

    def set_admin(self, username: str):
        try:
            user = User.get(User.username == username)
            Admin.create(faculty_id=user.id)
        except User.DoesNotExist:
            error = 'No faculty with the username {}'.format(username)
            raise DatabaseException(error)
        except pw.IntegrityError:
            error = 'User {} is already an admin'.format(username)
            raise DatabaseException(error)

    def remove_admin(self, username: str):
        try:
            user = User.get((User.username == username) &
                            (User.role == 'faculty'))
            admin = Admin.get(Admin.id == user.id)
            admin.delete_instance()
        except User.DoesNotExist:
            error = 'No faculty with the username {}'.format(username)
            raise DatabaseException(error)
        except Admin.DoesNotExist:
            error = '{} is not an admin'.format(username)
            raise DatabaseException(error)

    def insert_class(self, class_name: str, faculty_username: str):
        faculty_id = self._get_faculty_id(faculty_username)

        if self.class_exists(class_name, faculty_username):
            error = ('{} already has a class named {}'
                     .format(faculty_username, class_name))
            raise DatabaseException(error)

        Class.create(name=class_name, faculty_id=faculty_id, open=True)

    def close_class(self, class_name: str, faculty_username: str):
        faculty_id = self._get_faculty_id(faculty_username)

        try:
            query = (Class.update(open=False)
                          .where((Class.name == class_name) &
                                 (Class.faculty_id == faculty_id)))
            query.execute()
        except Class.DoesNotExist:
            error = ('Faculty {} does not have a class named {}'
                     .format(faculty_username, class_name))
            raise DatabaseException(error)

    def open_class(self, class_name: str, faculty_username: str):
        faculty_id = self._get_faculty_id(faculty_username)

        try:
            query = (Class.update(open=True)
                          .where((Class.name == class_name) &
                                 (Class.faculty_id == faculty_id)))
            query.execute()
        except Class.DoesNotExist:
            error = ('Faculty {} does not have a class named {}'
                     .format(faculty_username, class_name))
            raise DatabaseException(error)

    def class_is_open(self, class_name: str, faculty_username: str) -> bool:
        faculty_id = self._get_faculty_id(faculty_username)

        try:
            the_class = Class.get((Class.name == class_name) &
                                  (Class.faculty_id == faculty_id))
            return the_class.open
        except Class.DoesNotExist:
            error = ('Faculty {} does not have a class named {}'
                     .format(faculty_username, class_name))
            raise DatabaseException(error)

    def add_student_to_class(self, class_name: str, student_username: str,
                             faculty_username: str):
        faculty_id = self._get_faculty_id(faculty_username)
        class_id = self._get_class_id(class_name, faculty_username)
        student_id = self._get_student_id(student_username)

        try:
            ClassStudent.create(class_id=class_id, student_id=student_id)
        except pw.IntegrityError:
            error = '{} is already in class {}'.format(student_username,
                                                       class_name)
            raise DatabaseException(error)

    def get_class_students(self, class_name: str, faculty_username: str):
        class_id = self._get_class_id(class_name, faculty_username)

        query = User.select().join(ClassStudent).join(Class).where(
            (Class.id == class_id)
        )

        students = []

        for row in query:
            student = Student(row.last_name, row.first_name, row.username,
                              row.email)
            students.append(student)

        return students

    def update_byte_counts(self, byte_counts_by_file_path: dict):
        data = [
            {'file_path': path, 'byte_count': byte_counts_by_file_path[path]}
            for path in byte_counts_by_file_path
        ]

        ByteCount.replace_many(data).execute()

    def get_byte_count(self, file_path: str):
        try:
            byte_count = ByteCount.get(ByteCount.file_path == file_path)
            return byte_count.byte_count
        except ByteCount.DoesNotExist:
            raise DatabaseException('No byte count found for {}'
                                    .format(file_path))

    def get_byte_counts(self):
        query = ByteCount.select()

        byte_counts = [
            (byte_count.file_path, byte_count.byte_count)
            for byte_count in query
        ]

        return byte_counts

    def delete_byte_count(self, file_path: str):
        try:
            byte_count = ByteCount.get(ByteCount.file_path == file_path)
            byte_count.delete_instance()
        except ByteCount.DoesNotExist:
            raise DatabaseException('No byte count found for {}'
                                    .format(file_path))

    def _get_class_id(self, class_name, faculty_username):
        selected_class = Class.select().join(User).where(
            (Class.name == class_name) &
            (Class.faculty_id == User.id) &
            (User.username == faculty_username)
        ).get()

        if selected_class is None:
            raise DatabaseException('{} has no class named {}'
                                    .format(faculty_username, class_name))

        return selected_class.id

    def _get_faculty_id(self, faculty_username):
        faculty = User.select().where(
            (User.username == faculty_username) &
            (User.role == 'faculty')
        ).get()

        if faculty is None:
            raise DatabaseException('No faculty with the username {}'
                                    .format(faculty_username))

        return faculty.id

    def _get_student_id(self, student_username):
        student = User.select().where(
            (User.username == student_username) &
            (User.role == 'student')
        ).get()

        if student is None:
            raise DatabaseException('No student with the username {}'
                                    .format(student_username))

        return student.id


db = Database()
