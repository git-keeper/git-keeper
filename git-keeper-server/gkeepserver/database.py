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


import sqlite3
import peewee as pw

from pkg_resources import resource_exists, resource_string, ResolutionError, \
    ExtractionError

from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.student import Student


class DatabaseException(GkeepException):
    pass


def username_from_email(email_address: str):
    try:
        username, domain = email_address.split('@')
    except:
        error = ('{0} does not appear to be a valid email address'
                 .format(email_address))
        raise DatabaseException(error)

    return username


database_proxy = pw.DatabaseProxy()


class BaseModel(pw.Model):
    class Meta:
        database = database_proxy


class User(BaseModel):
    email = pw.CharField(unique=True)
    username = pw.CharField(unique=True)
    role = pw.CharField()
    first_name = pw.CharField()
    last_name = pw.CharField()


class Class(BaseModel):
    name = pw.CharField()
    faculty_id = pw.ForeignKeyField(User, backref='id')

    class Meta:
        indexes = (
            (('name', 'faculty_id'), True),
        )


class ClassStudent(BaseModel):
    class_id = pw.ForeignKeyField(Class, backref='id')
    student_id = pw.ForeignKeyField(User, backref='id')


class Assignment(BaseModel):
    name = pw.CharField()
    class_id = pw.ForeignKeyField(Class, backref='id')

    class Meta:
        indexes = (
            (('name', 'class_id'), True),
        )


class Database:
    def __init__(self, db_filename):
        database_proxy.initialize(
            pw.SqliteDatabase(db_filename, pragmas={'foreign_keys': 1})
        )
        database_proxy.connect()
        database_proxy.create_tables([User, Class, ClassStudent, Assignment])

    def username_exists(self, username):
        query = User.select().where(User.username == username)
        return query.exists()

    def email_exists(self, email_address):
        query = User.select().where(User.email == email_address)
        return query.exists()

    def class_exists(self, class_name, faculty_username):
        query = 

        query = ('SELECT * FROM class, user '
                 'WHERE class.name = ? '
                 '  AND class.faculty_id = user.id '
                 '  AND user.username = ?')

        cursor = self.db.cursor()
        cursor.execute(query, (class_name, faculty_username))
        row = cursor.fetchone()

        return row is not None

    def insert_student(self, student: Student):
        self.insert_user(student.email_address, student.first_name,
                         student.last_name, 'student')

    def insert_user(self, email_address: str, first_name: str,
                    last_name: str, role: str):
        if self.email_exists(email_address):
            error = 'A user with the email address {} already exists'
            raise DatabaseException(error)

        original_username = username_from_email(email_address)
        username = original_username

        counter = 1
        while self.username_exists(username):
            username = original_username + str(counter)
            counter += 1

        query = ('INSERT INTO user(username, email, first_name, last_name,'
                 '                  role) '
                 '  VALUES(?, ?, ?, ?, ?)')

        cursor = self.db.cursor()
        cursor.execute(query, (username, email_address, first_name, last_name,
                               role))
        self.db.commit()

    def insert_class(self, class_name: str, faculty_username: str):
        faculty_id = self._get_faculty_id(faculty_username)

        if self.class_exists(class_name, faculty_username):
            error = ('{} already has a class named {}'
                     .format(faculty_username, class_name))
            raise DatabaseException(error)

        query = 'INSERT INTO class(name, faculty_id) VALUES(?,?)'
        cursor = self.db.cursor()
        cursor.execute(query, (class_name, faculty_id))
        self.db.commit()

    def add_student_to_class(self, class_name: str, student_username: str,
                             faculty_username: str):
        #if self.is_student_in_class()

        faculty_id = self._get_faculty_id(faculty_username)
        class_id = self._get_class_id(class_name, faculty_username)
        student_id = self._get_student_id(student_username)



    def get_class_students(self, class_name: str, faculty_username: str):
        class_id = self._get_class_id(class_name, faculty_username)

        query = ('SELECT username, email, first_name, last_name '
                 'FROM user, class, class_student '
                 'WHERE user.id = class_student.student_id '
                 '  AND class.id = class_student.class_id '
                 '  AND class.id = ?')

        cursor = self.db.cursor()
        cursor.execute(query, (class_id,))

        students = []

        for row in cursor.fetchall():
            student = Student(row[3], row[2], row[0], row[1])
            students.append(student)

        return students

    def _get_class_id(self, class_name, faculty_username):
            query = ('SELECT class.id FROM class, user '
                     'WHERE class.name = ? AND class.faculty_id = user.id '
                     '  AND user.username = ?')
            cursor = self.db.cursor()
            cursor.execute(query, (class_name, faculty_username))

            row = cursor.fetchone()

            if row is None:
                raise DatabaseException('Faculty user {} has no class named {}'
                                        .format(class_name, faculty_username))

            return row[0]

    def _get_faculty_id(self, faculty_username):
        query = "SELECT id FROM user WHERE username = ? AND role = 'faculty'"
        cursor = self.db.cursor()

        cursor.execute(query, (faculty_username,))

        row = cursor.fetchone()

        if row is None:
            raise DatabaseException('No such faculty user {}'
                                    .format(faculty_username))

        return row[0]

    def _get_student_id(self, student_username):
        query = "SELECT id FROM user WHERE username = ? AND role = 'student'"
        cursor = self.db.cursor()

        cursor.execute(query, (student_username,))

        row = cursor.fetchone()

        if row is None:
            raise DatabaseException('No such faculty user {}'
                                    .format(student_username))

        return row[0]



# class Database:
#     def __init__(self, db_filename):
#         database_proxy.initialize(SqliteDatabase(db_filename))
#         database_proxy.connect()
#
#     def connect(self, db_filename):
#         self.db = sqlite3.connect(db_filename)
#         self.db.cursor().execute('PRAGMA foreign_keys = ON')
#
#     def initialize(self):
#         if not resource_exists('gkeepserver', 'data/schema.sql'):
#             error = 'Database schema does not exist'
#             raise DatabaseException(error)
#
#         try:
#             sql = resource_string('gkeepserver', 'data/schema.sql').decode()
#         except (ResolutionError, ExtractionError, UnicodeDecodeError):
#             raise DatabaseException('Error reading database schema')
#
#         try:
#             cursor = self.db.cursor()
#             cursor.executescript(sql)
#             self.db.commit()
#         except sqlite3.DatabaseError as e:
#             raise DatabaseException('Error initializing database: {}'
#                                     .format(e))
#
#     def username_exists(self, username):
#         cursor = self.db.cursor()
#         cursor.execute('SELECT * FROM user WHERE username = ?', (username,))
#         row = cursor.fetchone()
#         return row is not None
#
#     def email_exists(self, email_address):
#         cursor = self.db.cursor()
#         cursor.execute('SELECT * FROM user WHERE email = ?', (email_address,))
#         row = cursor.fetchone()
#         return row is not None
#
#     def class_exists(self, class_name, faculty_username):
#         query = ('SELECT * FROM class, user '
#                  'WHERE class.name = ? '
#                  '  AND class.faculty_id = user.id '
#                  '  AND user.username = ?')
#
#         cursor = self.db.cursor()
#         cursor.execute(query, (class_name, faculty_username))
#         row = cursor.fetchone()
#
#         return row is not None
#
#     def insert_student(self, student: Student):
#         self.insert_user(student.email_address, student.first_name,
#                          student.last_name, 'student')
#
#     @synchronized
#     def insert_user(self, email_address: str, first_name: str,
#                     last_name: str, role: str):
#         if self.email_exists(email_address):
#             error = 'A user with the email address {} already exists'
#             raise DatabaseException(error)
#
#         original_username = username_from_email(email_address)
#         username = original_username
#
#         counter = 1
#         while self.username_exists(username):
#             username = original_username + str(counter)
#             counter += 1
#
#         query = ('INSERT INTO user(username, email, first_name, last_name,'
#                  '                  role) '
#                  '  VALUES(?, ?, ?, ?, ?)')
#
#         cursor = self.db.cursor()
#         cursor.execute(query, (username, email_address, first_name, last_name,
#                                role))
#         self.db.commit()
#
#     @synchronized
#     def insert_class(self, class_name: str, faculty_username: str):
#         faculty_id = self._get_faculty_id(faculty_username)
#
#         if self.class_exists(class_name, faculty_username):
#             error = ('{} already has a class named {}'
#                      .format(faculty_username, class_name))
#             raise DatabaseException(error)
#
#         query = 'INSERT INTO class(name, faculty_id) VALUES(?,?)'
#         cursor = self.db.cursor()
#         cursor.execute(query, (class_name, faculty_id))
#         self.db.commit()
#
#     def add_student_to_class(self, class_name: str, student_username: str,
#                              faculty_username: str):
#         if self.is_student_in_class()
#
#         faculty_id = self._get_faculty_id(faculty_username)
#         class_id = self._get_class_id(class_name, faculty_username)
#         student_id = self._get_student_id(student_username)
#
#
#
#     def get_class_students(self, class_name: str, faculty_username: str):
#         class_id = self._get_class_id(class_name, faculty_username)
#
#         query = ('SELECT username, email, first_name, last_name '
#                  'FROM user, class, class_student '
#                  'WHERE user.id = class_student.student_id '
#                  '  AND class.id = class_student.class_id '
#                  '  AND class.id = ?')
#
#         cursor = self.db.cursor()
#         cursor.execute(query, (class_id,))
#
#         students = []
#
#         for row in cursor.fetchall():
#             student = Student(row[3], row[2], row[0], row[1])
#             students.append(student)
#
#         return students
#
#     def _get_class_id(self, class_name, faculty_username):
#             query = ('SELECT class.id FROM class, user '
#                      'WHERE class.name = ? AND class.faculty_id = user.id '
#                      '  AND user.username = ?')
#             cursor = self.db.cursor()
#             cursor.execute(query, (class_name, faculty_username))
#
#             row = cursor.fetchone()
#
#             if row is None:
#                 raise DatabaseException('Faculty user {} has no class named {}'
#                                         .format(class_name, faculty_username))
#
#             return row[0]
#
#     def _get_faculty_id(self, faculty_username):
#         query = "SELECT id FROM user WHERE username = ? AND role = 'faculty'"
#         cursor = self.db.cursor()
#
#         cursor.execute(query, (faculty_username,))
#
#         row = cursor.fetchone()
#
#         if row is None:
#             raise DatabaseException('No such faculty user {}'
#                                     .format(faculty_username))
#
#         return row[0]
#
#     def _get_student_id(self, student_username):
#         query = "SELECT id FROM user WHERE username = ? AND role = 'student'"
#         cursor = self.db.cursor()
#
#         cursor.execute(query, (student_username,))
#
#         row = cursor.fetchone()
#
#         if row is None:
#             raise DatabaseException('No such faculty user {}'
#                                     .format(student_username))
#
#         return row[0]


