# Copyright 2019, 2020 Nathan Sommer and Ben Coleman
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

from gkeepcore.assignment import Assignment
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
    """
    This is a base class used by all of the peewee classes in order to specify
    the database type.
    """
    class Meta:
        database = database


class DBUser(BaseModel):
    email_address = pw.CharField(unique=True)
    username = pw.CharField(unique=True)


class DBFacultyUser(BaseModel):
    user_id = pw.ForeignKeyField(DBUser, unique=True)
    first_name = pw.CharField()
    last_name = pw.CharField()
    admin = pw.BooleanField()


class DBStudentUser(BaseModel):
    user_id = pw.ForeignKeyField(DBUser, unique=True)


class DBDummyUser(BaseModel):
    user_id = pw.ForeignKeyField(DBUser, unique=True)


class DBClass(BaseModel):
    name = pw.CharField()
    faculty_id = pw.ForeignKeyField(DBUser)
    open = pw.BooleanField()

    class Meta:
        indexes = (
            (('name', 'faculty_id'), True),
        )


class DBClassStudent(BaseModel):
    class_id = pw.ForeignKeyField(DBClass)
    user_id = pw.ForeignKeyField(DBUser)
    first_name = pw.CharField()
    last_name = pw.CharField()
    active = pw.BooleanField()

    class Meta:
        indexes = (
            (('class_id', 'user_id'), True),
        )


class DBAssignment(BaseModel):
    name = pw.CharField()
    class_id = pw.ForeignKeyField(DBClass)
    published = pw.BooleanField()
    disabled = pw.BooleanField()

    class Meta:
        indexes = (
            (('name', 'class_id'), True),
        )


class DBByteCount(BaseModel):
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
        database.create_tables([DBUser, DBFacultyUser, DBStudentUser,
                                DBDummyUser, DBClass, DBClassStudent,
                                DBAssignment, DBByteCount])

    def username_exists(self, username):
        """
        Determines whether or not a user with the given username exists in
        the database.

        :param username: username to check
        :return: True if the username exists, False if not
        """
        query = DBUser.select().where(DBUser.username == username)
        return query.exists()

    def email_exists(self, email_address):
        """
        Determines whether or not a user with the given email address exists
        in the database. Matching is case-insensitive.

        :param email_address: the email address to check
        :return: True if the email address exists, False if not
        """

        lower_email = pw.fn.LOWER(DBUser.email_address)
        query = DBUser.select().where(lower_email == email_address.lower())
        return query.exists()

    def get_username_from_email(self, email_address):
        """
        Get a user's username from their email address.

        Raises a DatabaseException if there is no such user.

        :param email_address: email address of the user
        :return: username of the user
        """
        try:
            lower_email = pw.fn.LOWER(DBUser.email_address)
            return DBUser.get(lower_email == email_address.lower()).username
        except DBUser.DoesNotExist:
            error = 'No user with email address {}'.format(email_address)
            raise DatabaseException(error)

    def get_email_from_username(self, username):
        """
        Get a user's email address from their username.

        Raises a DatabaseException if there is no such user.

        :param username: username of the user
        :return: email address of the user
        """
        try:
            return DBUser.get(DBUser.username == username).email_address
        except DBUser.DoesNotExist:
            error = 'No user with username {}'.format(username)
            raise DatabaseException(error)

    def class_exists(self, class_name, faculty_username):
        """
        Determines whether or not a class with the given name exists for the
        faculty member with the given username.

        :param class_name: name of the class to check
        :param faculty_username: username of the faculty member
        :return: True if the class exists, False if not
        """
        query = DBClass.select().join(DBUser).where(
            (DBClass.name == class_name) &
            (DBUser.username == faculty_username)
        )
        return query.exists()

    def insert_dummy_user(self, username):
        """
        Inserts a user into the database that exists purely to prevent its
        username from being used in the future.

        :param username: dummy username to insert
        """

        if self.username_exists(username):
            error = ('Cannot insert dummy user {} into the database, that '
                     'username already exists in the database'
                     .format(username))
            raise DatabaseException(error)

        email_address = '{}@DUMMY'.format(username)

        DBUser.create(username=username, email_address=email_address)
        user_id = self._user_id_from_username(username)
        DBDummyUser.create(user_id=user_id)

    def insert_student(self, student: Student, existing_users,
                       user_exists=False) -> Student:
        """
        Inserts a student into the database. The username attribute of the
        provided Student object is ignored, and is updated with the username
        assigned by the database. The updated Student object is returned.

        :param student: a Student object representing the student to insert
        :param existing_users: list of usernames that already exist on the
         system, but are not necessarily in the db
        :param user_exists: True if the user already exists as faculty
        :return: the Student object, which may have an updated username field
        """

        if not user_exists:
            username = self._insert_user(student.email_address, existing_users)
        else:
            username = self.get_username_from_email(student.email_address)

        user_id = self._user_id_from_username(username)
        DBStudentUser.create(user_id=user_id)
        student.username = username
        return student

    def change_student_name(self, student: Student, class_name: str,
                            faculty_username: str):
        """
        Change the name of a student in a particular class.

        Raises a DatabaseException if the student is not in the class.

        :param student: Student object containing the student's existing
         username and email address, and new first and last names
        :param class_name: name of the class the student is in
        :param faculty_username: username of the faculty that owns the class
        """
        if not self.student_in_class(student.email_address, class_name,
                                     faculty_username):
            error = ('No student with email address {} in class {}'
                     .format(student.email_address, class_name))
            raise DatabaseException(error)

        if (self.get_username_from_email(student.email_address)
                != student.username):
            error = ('Username {} and email address {} do not match'
                     .format(student.email_address, student.username))
            raise DatabaseException(error)

        student_id = self._user_id_from_username(student.username)
        class_id = self._get_class_id(class_name, faculty_username)
        class_student = DBClassStudent.get(DBClassStudent.user_id == student_id,
                                           DBClassStudent.class_id == class_id)
        class_student.first_name = student.first_name
        class_student.last_name = student.last_name
        class_student.save()

    def insert_faculty(self, faculty: Faculty, existing_users,
                       user_exists=False) -> Faculty:
        """
        Inserts a faculty member into the database. The username attribute of
        the provided Faculty object is ignored, and is updated with the
        username assigned by the database. The updated Faculty object is
        returned.

        :param faculty: a Faculty object representing the faculty to insert
        :param existing_users: list of usernames that already exist on the
         system, but are not necessarily in the db
        :param user_exists: True if the user exists as a student
        :return: the Faculty object, which may have an updated username field
        """

        if user_exists:
            username = self.get_username_from_email(faculty.email_address)
        else:
            username = self._insert_user(faculty.email_address, existing_users)

        user_id = self._user_id_from_username(username)
        DBFacultyUser.create(user_id=user_id,
                             first_name=faculty.first_name,
                             last_name=faculty.last_name,
                             admin=faculty.admin)
        faculty.username = username
        return faculty

    def get_faculty_by_username(self, username: str) -> Faculty:
        """
        Returns a Faculty object representing the faculty user with the
        given username. Raises a DatabaseException if there is no such faculty

        :param username: username of the faculty user
        :return: Faculty object representing the faculty user
        """
        try:
            user = (DBUser
                    .select(DBUser.username, DBUser.email_address,
                            DBFacultyUser.first_name, DBFacultyUser.last_name,
                            DBFacultyUser.admin)
                    .join(DBFacultyUser)
                    .where(DBUser.username == username)).get()
            return Faculty(user.dbfacultyuser.last_name,
                           user.dbfacultyuser.first_name,
                           user.username, user.email_address,
                           user.dbfacultyuser.admin)
        except DBUser.DoesNotExist:
            error = 'No faculty user with the username {}'.format(username)
            raise DatabaseException(error)

    def get_faculty_by_email(self, email_address: str) -> Faculty:
        """
        Returns a Faculty object representing the faculty user with the
        given email address. Raises a DatabaseException if the user does not
        exist.

        :param email_address: email address of the faculty user
        :return: Faculty object representing the faculty user
        """

        try:
            lower_email = pw.fn.LOWER(DBUser.email_address)
            user = (DBUser
                    .select(DBUser.username, DBUser.email_address,
                            DBFacultyUser.first_name, DBFacultyUser.last_name,
                            DBFacultyUser.admin)
                    .join(DBFacultyUser)
                    .where(lower_email == email_address.lower())).get()
            return Faculty(user.dbfacultyuser.last_name,
                           user.dbfacultyuser.first_name,
                           user.username, user.email_address,
                           user.dbfacultyuser.admin)
        except DBUser.DoesNotExist:
            error = ('No faculty user with the email address {}'
                     .format(email_address))
            raise DatabaseException(error)

    def get_all_faculty(self):
        """
        Returns a list of all the faculty users in the database, as Faculty
        objects.

        :return: list of Faculty objects representing all faculty users
        """

        faculty_objects = []

        query = (DBUser
                 .select(DBUser.username, DBUser.email_address,
                         DBFacultyUser.first_name, DBFacultyUser.last_name,
                         DBFacultyUser.admin)
                 .join(DBFacultyUser))

        for result in query:
            faculty_objects.append(
                Faculty(result.dbfacultyuser.last_name,
                        result.dbfacultyuser.first_name, result.username,
                        result.email_address, admin=result.dbfacultyuser.admin)
            )

        return faculty_objects

    def get_faculty_class_names(self, username: str):
        """
        Returns a list of strings representing the names of all of the classes
        owned by a particular faculty user.

        :param username: username of the faculty user
        :return: list of class names owned by the faculty user
        """

        query = DBClass.select().join(DBUser).where(DBUser.username == username)
        return [row.name for row in query]

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

    def student_username_exists(self, username: str):
        """
        Determines if a student user exists with the given username.

        :param username: username of the student user
        :return: True if the username exists, False if not
        """

        try:
            user = (DBUser
                    .select()
                    .join(DBStudentUser)
                    .where(DBUser.username == username)).get()
            return True
        except DBUser.DoesNotExist:
            return False

    def is_admin(self, username: str):
        """
        Determines if the given username refers to a user with admin privileges

        :param username: username to check
        :return: True if the username refers to an admin, False if not
        """

        query = DBUser.select().join(DBFacultyUser).where(
            (DBUser.username == username) & (DBFacultyUser.admin == True)
        )
        return query.exists()

    def set_admin(self, username: str):
        """
        Make the user with the given username an admin. Raises a
        DatabaseException if the user does not exist.

        :param username: username of the user
        """

        user_id = self._get_faculty_id(username)
        faculty_user = DBFacultyUser.get(DBFacultyUser.user_id == user_id)
        if faculty_user.admin:
            error = 'User {} is already an admin'.format(username)
            raise DatabaseException(error)
        faculty_user.admin = True
        faculty_user.save()

    def remove_admin(self, username: str):
        """
        Removes admin privileges for a user. Raises a DatabaseException if the
        username does not refer to a faculty user with admin privileges, or if
        the username refers to the only admin.

        :param username: username for which to remove privileges
        """

        if DBFacultyUser.select().where(DBFacultyUser.admin == True).count() == 1:
            raise DatabaseException('You may not demote the only admin user')

        user_id = self._get_faculty_id(username)
        faculty_user = DBFacultyUser.get(DBFacultyUser.user_id == user_id)
        if not faculty_user.admin:
            error = 'User {} is not an admin'.format(username)
            raise DatabaseException(error)
        faculty_user.admin = False
        faculty_user.save()

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

        DBClass.create(name=class_name, faculty_id=faculty_id, open=True)

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
            query = (DBClass.update(open=False)
                     .where((DBClass.name == class_name) &
                            (DBClass.faculty_id == faculty_id)))
            query.execute()
        except DBClass.DoesNotExist:
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
            query = (DBClass.update(open=True)
                     .where((DBClass.name == class_name) &
                            (DBClass.faculty_id == faculty_id)))
            query.execute()
        except DBClass.DoesNotExist:
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
            the_class = DBClass.get((DBClass.name == class_name) &
                                    (DBClass.faculty_id == faculty_id))
            return the_class.open
        except DBClass.DoesNotExist:
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
            assignment = DBAssignment.get((DBAssignment.class_id == class_id) &
                                          (DBAssignment.name == assignment_name))
            if assignment.disabled:
                error = ('Assignment {} is a disabled assignment in class {}'
                         .format(assignment_name, class_name))
                raise DatabaseException(error)
            else:
                error = ('Class {} already has an assignment named {}'
                         .format(class_name, assignment_name))
                raise DatabaseException(error)
        except DBAssignment.DoesNotExist:
            pass

        try:
            DBAssignment.create(class_id=class_id, name=assignment_name,
                                published=False, disabled=False)
        except pw.IntegrityError:
            error = ('Class {} already has an assignment named {}'
                     .format(class_name, assignment_name))
            raise DatabaseException(error)

    def get_class_assignments(self, class_name: str, faculty_username: str,
                              include_disabled=False):
        """
        Get all of the assignments from a class as a list of Assignment
        objects.

        Raises a DatabaseException if the class does not exist.

        :param class_name: name of the class
        :param faculty_username: username of the faculty that owns the class
        :param include_disabled: if True,
        :return: list of Assignment object representing the assignments
         in the class
        """

        class_id = self._get_class_id(class_name, faculty_username)

        assignments = []

        query = DBAssignment.select().where((DBAssignment.class_id == class_id))

        for assignment in query:
            if not assignment.disabled or include_disabled:
                assignments.append(Assignment(assignment.name, class_name,
                                              faculty_username,
                                              assignment.published,
                                              assignment.disabled))

        return assignments

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
            assignment = DBAssignment.get(class_id=class_id,
                                          name=assignment_name)
            assignment.delete_instance()
        except DBAssignment.DoesNotExist:
            error = ('No assignment named {} in class {}'
                     .format(assignment_name, class_name))
            raise DatabaseException(error)

    def disable_assignment(self, class_name: str, assignment_name: str,
                           faculty_username: str):
        """
        Disables an assignment. Raises a DatabaseException if either the class
        or assignment do not exist, if the assignment is already disabled, or
        if the assignment is not published.

        :param class_name: name of the class that the assignment belongs to
        :param assignment_name: name of the assignment
        :param faculty_username: username of the faculty user that owns the
         assignment
        """
        class_id = self._get_class_id(class_name, faculty_username)

        try:
            assignment = DBAssignment.get(class_id=class_id,
                                          name=assignment_name)
            if assignment.disabled:
                error = ('Assignment {} in class {} is already disabled'
                         .format(assignment_name, class_name))
                raise DatabaseException(error)

            if not assignment.published:
                error = ('Assignment {} in class {} cannot be disabled '
                         'because it is not published'
                         .format(assignment_name, class_name))
                raise DatabaseException(error)

            assignment.disabled = True
            assignment.save()
        except DBAssignment.DoesNotExist:
            error = ('No assignment named {} in class {}'
                     .format(assignment_name, class_name))
            raise DatabaseException(error)

    def is_disabled(self, class_name: str, assignment_name: str,
                    faculty_username: str):
        """
        Determine if an assignment is disabled. Raises a DatabaseException if
        the class or assignment do not exist.

        :param class_name: name of the class the assignment belongs to
        :param assignment_name: name of the assignment
        :param faculty_username: username of the faculty member that owns the
         assignment
        :return: True if the assignment is disabled, False if not
        """
        class_id = self._get_class_id(class_name, faculty_username)

        try:
            selected_assignment = DBAssignment.select().where(
                (DBAssignment.name == assignment_name) &
                (DBAssignment.class_id == class_id)
            ).get()

            return selected_assignment.disabled
        except DBAssignment.DoesNotExist:
            error = ('Class {} has no assignment {}'
                     .format(class_name, assignment_name))
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
            query = DBAssignment.update(published=published).where(
                (DBAssignment.class_id == class_id) &
                (DBAssignment.name == assignment_name)
            )
            query.execute()
        except DBAssignment.DoesNotExist:
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
            selected_assignment = DBAssignment.select().where(
                (DBAssignment.name == assignment_name) &
                (DBAssignment.class_id == class_id)
            ).get()

            return selected_assignment.published
        except DBAssignment.DoesNotExist:
            error = ('Class {} has no assignment {}'
                     .format(class_name, assignment_name))
            raise DatabaseException(error)

    def add_student_to_class(self, class_name: str, student: Student,
                             faculty_username: str):
        """
        Add a student to a class. Raises a DatabaseException if either the
        class or the student do not exist.

        :param class_name: name of the class
        :param student: Student object representing the student
        :param faculty_username: username of the faculty user that owns the
         class
        """
        class_id = self._get_class_id(class_name, faculty_username)
        student_id = self._student_id_from_email(student.email_address)

        try:
            DBClassStudent.create(class_id=class_id, user_id=student_id,
                                  first_name=student.first_name,
                                  last_name=student.last_name, active=True)
        except pw.IntegrityError:
            error = '{} is already in class {}'.format(student.email_address,
                                                       class_name)
            raise DatabaseException(error)

    def deactivate_student_in_class(self, class_name: str, student_email: str,
                                    faculty_username: str):
        """
        Mark a student as inactive in a class. Raises a DatabaseException if
        the class does not exist, or if the student is not in the class,
        or if the student is already inactive in the class

        :param class_name: name of the class
        :param student_email: email address of the student to deactivate
        :param faculty_username: username of the faculty user that owns the
         class
        """
        class_id = self._get_class_id(class_name, faculty_username)
        student_id = self._student_id_from_email(student_email)

        try:
            class_student = DBClassStudent.get(
                (DBClassStudent.class_id == class_id) &
                (DBClassStudent.user_id == student_id)
            )
        except DBClassStudent.DoesNotExist:
            error = ('{} is not a student in {}'.format(student_email,
                                                        class_name))
            raise DatabaseException(error)

        if not class_student.active:
            error = ('{} is already inactive in class {}'
                     .format(student_email, class_name))
            raise DatabaseException(error)

        DBClassStudent.update(active=False).where(
            (DBClassStudent.class_id == class_id) &
            (DBClassStudent.user_id == student_id)
        ).execute()

    def activate_student_in_class(self, class_name: str, student_email: str,
                                  faculty_username: str):
        """
        Mark a student as active in a class. Raises a DatabaseException if
        the class does not exist, or if the student is not in the class,
        or if the student is already active in the class

        :param class_name: name of the class
        :param student_email: email address of the student to deactivate
        :param faculty_username: username of the faculty user that owns the
         class
        """
        class_id = self._get_class_id(class_name, faculty_username)
        student_id = self._student_id_from_email(student_email)

        try:
            class_student = DBClassStudent.get(
                (DBClassStudent.class_id == class_id) &
                (DBClassStudent.user_id == student_id)
            )
        except DBClassStudent.DoesNotExist:
            error = ('{} is not a student in {}'.format(student_email,
                                                        class_name))
            raise DatabaseException(error)

        if class_student.active:
            error = ('{} is already active in class {}'
                     .format(student_email, class_name))
            raise DatabaseException(error)

        DBClassStudent.update(active=True).where(
            (DBClassStudent.class_id == class_id) &
            (DBClassStudent.user_id == student_id)
        ).execute()

    def get_class_students(self, class_name: str, faculty_username: str):
        """
        Returns a list of all the active students in a class, as Student
        objects. Raises a DatabaseException if the class does not exist.

        :param class_name: name of the class
        :param faculty_username: username of the faculty user that owns the
         class
        :return:
        """
        class_id = self._get_class_id(class_name, faculty_username)

        query = (DBUser
                 .select(DBUser.username, DBUser.email_address,
                         DBClassStudent.first_name, DBClassStudent.last_name)
                 .join(DBClassStudent)
                 .join(DBClass)
                 .where((DBClass.id == class_id) & (DBClassStudent.active == True))
                 )

        students = []

        for row in query:
            student = Student(row.dbclassstudent.last_name,
                              row.dbclassstudent.first_name, row.username,
                              row.email_address)
            students.append(student)

        return students

    def student_in_class(self, email_address, class_name, faculty_username):
        """
        Determines if a student is an active student in a class. Raises a
        DatabaseException if the class does not exist, or if there is no
        student with the given username.

        :param email_address: email address of the student
        :param class_name: name of the class
        :param faculty_username: username of the faculty user that owns the
         class
        :return: True if the student is in the class, False otherwise
        """
        try:
            class_id = self._get_class_id(class_name, faculty_username)
            student_id = self._student_id_from_email(email_address)

            DBClassStudent.get((DBClassStudent.user_id == student_id) &
                               (DBClassStudent.class_id == class_id) &
                               (DBClassStudent.active == True))
            return True
        except (DatabaseException, DBClassStudent.DoesNotExist):
            return False

    def student_inactive_in_class(self, email_address, class_name,
                                  faculty_username):
        """
        Determines if a student is an inactive student in a class. Raises a
        DatabaseException if the class does not exist, or if there is no
        student with the given username.

        :param email_address: email address of the student
        :param class_name: name of the class
        :param faculty_username: username of the faculty user that owns the
         class
        :return: True if the student is in the class, False otherwise
        """
        try:
            class_id = self._get_class_id(class_name, faculty_username)
            student_id = self._student_id_from_email(email_address)

            DBClassStudent.get((DBClassStudent.user_id == student_id) &
                               (DBClassStudent.class_id == class_id) &
                               (DBClassStudent.active == False))
            return True
        except (DatabaseException, DBClassStudent.DoesNotExist):
            return False

    def get_class_student_by_username(self, username: str, class_name: str,
                                      faculty_username: str) -> Student:
        """
        Returns a Student object representing the student with the given
        username. Raises a DatabaseException if the student does not exist.

        :param username: username of the student
        :param class_name: name of the class to look in
        :param faculty_username: username of the faculty that owns the class
        :return: Student object representing the student
        """

        try:
            faculty_id = self._get_faculty_id(faculty_username)
            student_id = self._user_id_from_username(username)

            user = (DBUser
                    .select(DBUser.username, DBUser.email_address,
                            DBClassStudent.first_name,
                            DBClassStudent.last_name)
                    .join(DBClassStudent)
                    .join(DBClass)
                    .where(
                (DBClass.faculty_id == faculty_id) &
                (DBClass.name == class_name) &
                (DBClassStudent.user_id == student_id) &
                (DBClassStudent.active == True))
                    ).get()

            return Student(user.dbclassstudent.last_name,
                           user.dbclassstudent.first_name, user.username,
                           user.email_address)
        except DBUser.DoesNotExist:
            error = ('No student user with the username {} in class {}'
                     .format(username, class_name))
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

        DBByteCount.replace_many(data).execute()

    def get_byte_count(self, file_path: str):
        """
        Get the byte count of the file with the given path. Raises a
        DatabaseException if the file is not in the database.

        :param file_path: path of the file
        :return: byte count of the file
        """

        try:
            byte_count = DBByteCount.get(DBByteCount.file_path == file_path)
            return byte_count.byte_count
        except DBByteCount.DoesNotExist:
            raise DatabaseException('No byte count found for {}'
                                    .format(file_path))

    def get_byte_counts(self):
        """
        Returns a list of all the byte counts in the database, as a list of
        tuples. Each tuple is a 2-tuple which stores the path of the file
        and the number of bytes in the file.

        :return: a list of 2-tuples representing file paths and byte counts
        """

        query = DBByteCount.select()

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
            byte_count = DBByteCount.get(DBByteCount.file_path == file_path)
            byte_count.delete_instance()
        except DBByteCount.DoesNotExist:
            raise DatabaseException('No byte count found for {}'
                                    .format(file_path))

    def _insert_user(self, email_address: str, existing_users):
        """
        Inserts a user into the database. The user's username will the username
        from the user's email address unless the username already exists. If
        the username already exists, an integer will be appended to the email
        username to form a new unique username. The username assigned to the
        user is returned.

        :param email_address: the email address of the user
        :param existing_users: list of usernames that already exist on the
         system, but are not necessarily in the db
        :return: the username of the user
        """
        if self.email_exists(email_address):
            error = ('A user with the email address {} already exists'
                     .format(email_address))
            raise DatabaseException(error)

        original_username = username_from_email(email_address)
        clean_username = cleanup_string(original_username, is_username=True)

        validate_username(clean_username)

        username = clean_username

        counter = 1
        while username in existing_users or self.username_exists(username):
            username = clean_username + str(counter)
            counter += 1

        DBUser.create(username=username, email_address=email_address)

        return username

    def _get_class_id(self, class_name, faculty_username):
        try:
            selected_class = DBClass.select().join(DBUser).where(
                (DBClass.name == class_name) &
                (DBUser.username == faculty_username)
            ).get()
            return selected_class.id
        except DBClass.DoesNotExist:
            raise DatabaseException('{} has no class named {}'
                                    .format(faculty_username, class_name))

    def _user_id_from_username(self, username):
        try:
            return DBUser.get(DBUser.username == username).id
        except DBUser.DoesNotExist:
            raise DatabaseException('No user with the username {}'
                                    .format(username))

    def _get_faculty_id(self, faculty_username):
        try:
            faculty = DBUser.select().join(DBFacultyUser).where(
                (DBUser.username == faculty_username)
            ).get()
            return faculty.id
        except DBUser.DoesNotExist:
            raise DatabaseException('No faculty with the username {}'
                                    .format(faculty_username))

    def _student_id_from_username(self, student_username):
        try:
            student = DBUser.select().join(DBStudentUser).where(
                (DBUser.username == student_username)
            ).get()
            return student.id
        except DBUser.DoesNotExist:
            raise DatabaseException('No student with the username {}'
                                    .format(student_username))

    def _student_id_from_email(self, email_address):
        try:
            lower_email = pw.fn.LOWER(DBUser.email_address)
            student = DBUser.select().join(DBStudentUser).where(
                (lower_email == email_address.lower())
            ).get()
            return student.id
        except DBUser.DoesNotExist:
            raise DatabaseException('No student with the email address {}'
                                    .format(email_address))


db = Database()
