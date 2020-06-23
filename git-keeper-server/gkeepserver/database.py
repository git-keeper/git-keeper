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
    """
    Extract the portion of an email address before the '@' character. Intended
    to be used from within the Database class.

    Raises a DatabaseException if the string does not contain a single '@'

    :param email_address: string from which to extract the username
    :return: the username from the provided email address
    """
    try:
        username, domain = email_address.split('@')
    except ValueError:
        error = ('{0} does not appear to be a valid email address'
                 .format(email_address))
        raise DatabaseException(error)

    return username


# Used by the peewee Model classes
database = pw.SqliteDatabase(None)


class BaseModel(pw.Model):
    class Meta:
        database = database


class User(BaseModel):
    email_address = pw.CharField(unique=True)
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
    """
    Provides an interface for interacting with the database that stores
    information about users, classes, and assignments.
    """

    def connect(self, db_filename):
        """
        Connects the database to a file, or creates an in-memory database if
        given the string ':memory:'. Database tables are created if they do
        not already exist in the given file. This method must be called before
        any other methods are called.

        :param db_filename: name of the file to connect to
        """
        database.init(db_filename, pragmas={'foreign_keys': 1})
        database.create_tables([User, Admin, Class, ClassStudent, Assignment,
                                ByteCount])

    def username_exists(self, username):
        """
        Determines whether or not a user with the given username exists in
        the database.

        :param username: username to check
        :return: True if the username exists, False if not
        """
        query = User.select().where(User.username == username)
        return query.exists()

    def email_exists(self, email_address):
        """
        Determines whether or not a user with the given email address exists
        in the database.

        :param email_address: the email address to check
        :return: True if the email address exists, False if not
        """
        query = User.select().where(User.email_address == email_address)
        return query.exists()

    def class_exists(self, class_name, faculty_username):
        """
        Determines whether or not a class with the given name exists for the
        faculty member with the given username.

        :param class_name: name of the class to check
        :param faculty_username: username of the faculty member
        :return: True if the class exists, False if not
        """
        query = Class.select().join(User).where(
            (Class.name == class_name) &
            (Class.faculty_id == User.id) &
            (User.username == faculty_username)
        )
        return query.exists()

    def insert_student(self, student: Student) -> Student:
        """
        Inserts a student into the database. The username attribute of the
        provided Student object is ignored, and is updated with the username
        assigned by the database. The updated Student object is returned.

        :param student: a Student object representing the student to insert
        :return: the Student object, which may have an updated username field
        """
        username = self.insert_user(student.email_address, student.first_name,
                                    student.last_name, 'student')
        student.username = username
        return student

    def insert_faculty(self, faculty: Faculty) -> Faculty:
        """
        Inserts a faculty member into the database. The username attribute of
        the provided Faculty object is ignored, and is updated with the
        username assigned by the database. The updated Faculty object is
        returned.

        :param faculty: a Faculty object representing the faculty to insert
        :return: the Faculty object, which may have an updated username field
        """
        username = self.insert_user(faculty.email_address, faculty.first_name,
                                    faculty.last_name, 'faculty')
        if faculty.admin:
            self.set_admin(username)

        faculty.username = username
        return faculty

    def insert_user(self, email_address: str, first_name: str,
                    last_name: str, role: str):
        """
        Inserts a user into the database. The user's username will the username
        from the user's email address unless the username already exists. If
        the username already exists, an integer will be appended to the email
        username to form a new unique username. The username assigned to the
        user is returned.

        :param email_address: the email address of the user
        :param first_name: the first name of the user
        :param last_name: the last name of the user
        :param role: the role of the user, either 'faculty' or 'student'
        :return: the username of the user
        """
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

        User.create(username=username, email_address=email_address,
                    first_name=first_name, last_name=last_name,
                    role=role)

        return username

    def get_faculty_by_username(self, username: str) -> Faculty:
        """
        Returns a Faculty object representing the faculty user with the
        given username. Raises a DatabaseException if there is no such faculty

        :param username: username of the faculty user
        :return: Faculty object representing the faculty user
        """
        try:
            user = User.get((User.username == username) &
                            (User.role == 'faculty'))
            admin = self.is_admin(username)
            return Faculty(user.last_name, user.first_name, user.username,
                           user.email_address, admin)
        except User.DoesNotExist:
            error = 'No faculty user with the username {}'.format(username)
            raise DatabaseException(error)

    def get_all_faculty(self):
        """
        Returns a list of all the faculty users in the database, as Faculty
        objects.

        :return: list of Faculty objects representing all faculty users
        """

        faculty_objects = []

        query = (User.select().where(User.role == 'faculty'))

        for result in query:
            admin = self.is_admin(result.username)

            faculty_objects.append(
                Faculty(result.last_name, result.first_name, result.username,
                        result.email_address, admin=admin)
            )

        return faculty_objects

    def get_faculty_class_names(self, username: str):
        """
        Returns a list of strings representing the names of all of the classes
        owned by a particular faculty user.

        :param username: username of the faculty user
        :return: list of class names owned by the faculty user
        """

        query = Class.select().join(User).where(
            (Class.faculty_id == User.id) &
            (User.username == username)
        )

        class_names = [row.name for row in query]

        return class_names

    def faculty_username_exists(self, username: str):
        """
        Determines if a faculty user exists with the given username.

        :param username: username of the faculty user
        :return: True if the username exists, False if not
        """

        try:
            self.get_faculty_by_username(username)
            return True
        except DatabaseException:
            return False

    def get_faculty_by_email(self, email_address: str) -> Faculty:
        """
        Returns a Faculty object representing the faculty user with the
        given email address. Raises a DatabaseException if the user does not
        exist.

        :param email_address: email address of the faculty user
        :return: Faculty object representing the faculty user
        """

        try:
            user = User.get((User.email_address == email_address) &
                            (User.role == 'faculty'))
            admin = self.is_admin(user.username)
            return Faculty(user.last_name, user.first_name, user.username,
                           user.email_address, admin=admin)
        except User.DoesNotExist:
            error = ('No faculty user with the email address {}'
                     .format(email_address))
            raise DatabaseException(error)

    def is_admin(self, username: str):
        """
        Determines if the given username refers to a user with admin privileges

        :param username: username to check
        :return: True if the username refers to an admin, False if not
        """

        query = User.select().join(Admin).where(User.username == username)
        return query.exists()

    def set_admin(self, username: str):
        """
        Make the user with the given username an admin. Raises a
        DatabaseException if the user does not exist.

        :param username: username of the user
        """
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
        """
        Removes admin privileges for a user. Raises a DatabaseException if the
        username does not refer to a faculty user with admin privileges, or if
        the username refers to the only admin.

        :param username: username for which to remove privileges
        """
        if Admin.select().count() == 1:
            raise DatabaseException('You may not demote the only admin user')

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
        """
        Insert a new class into the database. Raises a DatabaseException if
        the class already exists.

        :param class_name: name of the new class
        :param faculty_username: username of the faculty user who owns the
         class
        """
        faculty_id = self._get_faculty_id(faculty_username)

        if self.class_exists(class_name, faculty_username):
            error = ('{} already has a class named {}'
                     .format(faculty_username, class_name))
            raise DatabaseException(error)

        Class.create(name=class_name, faculty_id=faculty_id, open=True)

    def close_class(self, class_name: str, faculty_username: str):
        """
        Mark a class as closed. Raises a DatabaseException if the class does
        not exist.

        :param class_name: name of the class
        :param faculty_username: username of the faculty user that owns the
         class
        """
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
        """
        Mark a class as open. Raises a DatabaseException if the class does not
        exist.

        :param class_name: name of the class
        :param faculty_username: name of the faculty user that owns the class
        """

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
        """
        Determine if a class is open. Raises a DatabaseException if the class
        does not exist.

        :param class_name: name of the class
        :param faculty_username: username of the faculty user that owns the
         class
        :return: True if the class exists, False if it does not
        """

        faculty_id = self._get_faculty_id(faculty_username)

        try:
            the_class = Class.get((Class.name == class_name) &
                                  (Class.faculty_id == faculty_id))
            return the_class.open
        except Class.DoesNotExist:
            error = ('Faculty {} does not have a class named {}'
                     .format(faculty_username, class_name))
            raise DatabaseException(error)

    def insert_assignment(self, class_name: str, assignment_name: str,
                          faculty_username: str):
        """
        Inserts a new assignment into the database. Raises a DatabaseException
        if the class does not exist, or if the assignment already exists
        :param class_name: name of the class that the assignment belongs to
        :param assignment_name: name of the assignment
        :param faculty_username: username of the facutly member that owns the
         assignment
        """

        class_id = self._get_class_id(class_name, faculty_username)

        try:
            Assignment.create(class_id=class_id, name=assignment_name,
                              published=False)
        except pw.IntegrityError:
            error = ('Class {} already has an assignment named {}'
                     .format(class_name, assignment_name))
            raise DatabaseException(error)

    def remove_assignment(self, class_name: str, assignment_name: str,
                          faculty_username: str):
        """
        Removes an assignment from the database. Raises a DatabaseException
        if either the class or assignment do not exist.

        :param class_name: name of the class that the assignment belongs to
        :param assignment_name: name of the assignment
        :param faculty_username: username of the faculty user that owns the
         assignment
        """
        class_id = self._get_class_id(class_name, faculty_username)

        try:
            assignment = Assignment.get(class_id=class_id,
                                        name=assignment_name)
            assignment.delete_instance()
        except Assignment.DoesNotExist:
            error = ('No assignment named {} in class {}'
                     .format(assignment_name, class_name))
            raise DatabaseException(error)

    def set_published(self, class_name: str, assignment_name: str,
                      faculty_username: str, published=True):
        """
        Marks an assignment as published or unpublished. Raises a
        DatabaseException if either the class or assignment do not exist.

        :param class_name: name of the class the assignment belongs to
        :param assignment_name: name of the assignment
        :param faculty_username: username of the faculty user that owns the
         assignment
        :param published: True if the assignment should be published, False
         if the assignment should be unpublished
        """
        class_id = self._get_class_id(class_name, faculty_username)

        try:
            query = Assignment.update(published=published).where(
                (Assignment.class_id == class_id) &
                (Assignment.name == assignment_name)
            )
            query.execute()
        except Assignment.DoesNotExist:
            error = ('No assignment named {} in class {}'
                     .format(assignment_name, class_name))
            raise DatabaseException(error)

    def is_published(self, class_name: str, assignment_name: str,
                     faculty_username: str):
        """
        Determine if an assignment is published. Raises a DatabaseException if
        the class or assignment do not exist.

        :param class_name: name of the class the assignment belongs to
        :param assignment_name: name of the assignment
        :param faculty_username: username of the faculty member that owns the
         assignment
        :return: True if the assignment is published, False if not
        """
        class_id = self._get_class_id(class_name, faculty_username)

        try:
            selected_assignment = Assignment.select().where(
                (Assignment.name == assignment_name) &
                (Assignment.class_id == class_id)
            ).get()

            return selected_assignment.published
        except Assignment.DoesNotExist:
            error = ('Class {} has no assignment {}'
                     .format(class_name, assignment_name))
            raise DatabaseException(error)

    def add_student_to_class(self, class_name: str, student_username: str,
                             faculty_username: str):
        """
        Add a student to a class. Raises a DatabaseException if either the
        class or the student do not exist.

        :param class_name: name of the class
        :param student_username: username of the student
        :param faculty_username: username of the faculty user that owns the
         class
        """
        class_id = self._get_class_id(class_name, faculty_username)
        student_id = self._get_student_id(student_username)

        try:
            ClassStudent.create(class_id=class_id, student_id=student_id)
        except pw.IntegrityError:
            error = '{} is already in class {}'.format(student_username,
                                                       class_name)
            raise DatabaseException(error)

    def remove_student_from_class(self, class_name: str, student_username: str,
                                  faculty_username: str):
        """
        Remove a student from a class. Raises a DatabaseException if the class
        does not exist or if the student is not in the class.

        :param class_name:
        :param student_username:
        :param faculty_username:
        :return:
        """
        class_id = self._get_class_id(class_name, faculty_username)
        student_id = self._get_student_id(student_username)

        try:
            class_student = ClassStudent.get(
                (ClassStudent.class_id == class_id) &
                (ClassStudent.student_id == student_id)
            )

            class_student.delete_instance()
        except ClassStudent.DoesNotExist:
            error = ('{} is not a student in {}'.format(student_username,
                                                        class_name))
            raise DatabaseException(error)

    def get_class_students(self, class_name: str, faculty_username: str):
        """
        Returns a list of all the students in a class, as Student objects.
        Raises a DatabaseException if the class does not exist.

        :param class_name: name of the class
        :param faculty_username: username of the faculty user that owns the
         class
        :return:
        """
        class_id = self._get_class_id(class_name, faculty_username)

        query = User.select().join(ClassStudent).join(Class).where(
            (Class.id == class_id)
        )

        students = []

        for row in query:
            student = Student(row.last_name, row.first_name, row.username,
                              row.email_address)
            students.append(student)

        return students

    def student_in_class(self, username, class_name, faculty_username):
        """
        Determines if a student is in a class. Raises a DatabaseException
        if the class does not exist, or if there is no student with the given
        username.

        :param username: username of the student
        :param class_name: name of the class
        :param faculty_username: username of the faculty user that owns the
         class
        :return: True if the student is in the class, False otherwise
        """
        try:
            class_id = self._get_class_id(class_name, faculty_username)
            student_id = self._get_student_id(username)

            ClassStudent.get((ClassStudent.student_id == student_id) &
                             (ClassStudent.class_id == class_id))
            return True
        except (DatabaseException, ClassStudent.DoesNotExist):
            return False

    def get_student_by_email(self, email_address: str) -> Student:
        """
        Returns a Student object representing the student with the given
        email address. Raises a DatabaseException if the student does not
        exist.

        :param email_address: email address of the student
        :return: a Student object representing the student
        """

        try:
            user = User.get((User.email_address == email_address) &
                            (User.role == 'student'))
            return Student(user.last_name, user.first_name, user.username,
                           user.email_address)
        except User.DoesNotExist:
            error = ('No student user with the email address {}'
                     .format(email_address))
            raise DatabaseException(error)

    def get_student_by_username(self, username: str) -> Student:
        """
        Returns a Student object representing the student with the given
        username. Raises a DatabaseException if the student does not exist.

        :param username: username of the student
        :return: Student object representing the student
        """

        try:
            user = User.get((User.username == username) &
                            (User.role == 'student'))
            return Student(user.last_name, user.first_name, user.username,
                           user.email_address)
        except User.DoesNotExist:
            error = ('No student user with the username {}'
                     .format(username))
            raise DatabaseException(error)

    def update_byte_counts(self, byte_counts_by_file_path: dict):
        """
        Update the byte counts of the files in the provided dictionary. The
        dictionary must map file paths (as strings) to integer byte counts.

        :param byte_counts_by_file_path: dictionary mapping file paths to
         byte counts
        """
        data = [
            {'file_path': path, 'byte_count': byte_counts_by_file_path[path]}
            for path in byte_counts_by_file_path
        ]

        ByteCount.replace_many(data).execute()

    def get_byte_count(self, file_path: str):
        """
        Get the byte count of the file with the given path. Raises a
        DatabaseException if the file is not in the database.

        :param file_path: path of the file
        :return: byte count of the file
        """

        try:
            byte_count = ByteCount.get(ByteCount.file_path == file_path)
            return byte_count.byte_count
        except ByteCount.DoesNotExist:
            raise DatabaseException('No byte count found for {}'
                                    .format(file_path))

    def get_byte_counts(self):
        """
        Returns a list of all the byte counts in the database, as a list of
        tuples. Each tuple is a 2-tuple which stores the path of the file
        and the number of bytes in the file.

        :return: a list of 2-tuples representing file paths and byte counts
        """

        query = ByteCount.select()

        byte_counts = [
            (byte_count.file_path, byte_count.byte_count)
            for byte_count in query
        ]

        return byte_counts

    def delete_byte_count(self, file_path: str):
        """
        Deletes the byte count for a specific file. Raises a DatabaseException
        if the file is not in the database.

        :param file_path: path to the file
        """

        try:
            byte_count = ByteCount.get(ByteCount.file_path == file_path)
            byte_count.delete_instance()
        except ByteCount.DoesNotExist:
            raise DatabaseException('No byte count found for {}'
                                    .format(file_path))

    def _get_class_id(self, class_name, faculty_username):
        try:
            selected_class = Class.select().join(User).where(
                (Class.name == class_name) &
                (Class.faculty_id == User.id) &
                (User.username == faculty_username)
            ).get()
            return selected_class.id
        except Class.DoesNotExist:
            raise DatabaseException('{} has no class named {}'
                                    .format(faculty_username, class_name))

    def _get_faculty_id(self, faculty_username):
        try:
            faculty = User.select().where(
                (User.username == faculty_username) &
                (User.role == 'faculty')
            ).get()
            return faculty.id
        except User.DoesNotExist:
            raise DatabaseException('No faculty with the username {}'
                                    .format(faculty_username))

    def _get_student_id(self, student_username):
        try:
            student = User.select().where(
                (User.username == student_username) &
                (User.role == 'student')
            ).get()
            return student.id
        except User.DoesNotExist:
            raise DatabaseException('No student with the username {}'
                                    .format(student_username))


db = Database()
