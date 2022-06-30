import pytest

from gkeepcore.assignment import Assignment
from gkeepcore.student import Student
from gkeepserver.database import Database, DatabaseException
from gkeepserver.faculty import Faculty


@pytest.fixture
def db() -> Database:
    db = Database()
    db.connect(':memory:')
    return db


def test_connect_and_initialize(db):
    pass


def test_insert_student(db):
    student1 = Student('one', 'student', 'student1', 'student1@school.edu')
    student2 = Student('two', 'student', 'student2', 'student2@school.edu')

    assert db.insert_student(student1) == student1
    assert db.insert_student(student2) == student2

    assert db.username_exists('student1')
    assert db.username_exists('student2')
    assert not db.username_exists('student3')

    assert db.email_exists('student1@school.edu')
    assert db.email_exists('student2@school.edu')
    assert not db.email_exists('student3@school.edu')

    with pytest.raises(DatabaseException):
        db.insert_student(student1)


def test_insert_faculty(db):
    faculty1 = Faculty('one', 'faculty', 'faculty1', 'faculty1@school.edu',
                       False)
    faculty2 = Faculty('two', 'faculty', 'faculty2', 'faculty2@school.edu',
                       True)

    assert db.insert_faculty(faculty1) == faculty1
    assert db.insert_faculty(faculty2) == faculty2

    assert db.username_exists('faculty1')
    assert db.username_exists('faculty2')
    assert not db.username_exists('faculty3')

    assert db.email_exists('faculty1@school.edu')
    assert db.email_exists('faculty2@school.edu')
    assert not db.email_exists('faculty3@school.edu')

    assert db.get_faculty_by_username('faculty1') == faculty1
    assert db.get_faculty_by_username('faculty2') == faculty2
    with pytest.raises(DatabaseException):
        db.get_faculty_by_username('faculty3')

    assert db.get_faculty_by_email('faculty1@school.edu') == faculty1
    assert db.get_faculty_by_email('faculty2@school.edu') == faculty2
    with pytest.raises(DatabaseException):
        db.get_faculty_by_email('faculty3@school.edu')

    with pytest.raises(DatabaseException):
        db.insert_faculty(faculty1)


def test_duplicate_email_usernames(db):
    student0 = db.insert_student(Student('last', 'first', 'user',
                                         'user@schoolzero.edu'))
    student1 = db.insert_student(Student('last', 'first', 'user',
                                         'user@schoolone.edu'))
    student2 = db.insert_student(Student('last', 'first', 'user',
                                         'user@schooltwo.edu'))

    faculty3 = db.insert_faculty(Faculty('last', 'first', 'user',
                                         'user@schoolthree.edu', False))
    faculty4 = db.insert_faculty(Faculty('last', 'first', 'user',
                                         'user@schoolfour.edu', False))
    faculty5 = db.insert_faculty(Faculty('last', 'first', 'user',
                                         'user@schoolfive.edu', False))

    for username in ('user', 'user1', 'user2', 'user3', 'user4', 'user5'):
        assert db.username_exists(username)

    assert student0.username == 'user'
    assert student1.username == 'user1'
    assert student2.username == 'user2'
    assert faculty3.username == 'user3'
    assert faculty4.username == 'user4'
    assert faculty5.username == 'user5'

    assert db.get_username_from_email('user@schoolzero.edu') == 'user'
    assert db.get_username_from_email('user@schoolone.edu') == 'user1'
    assert db.get_username_from_email('user@schoolfour.edu') == 'user4'

    assert db.get_email_from_username('user') == 'user@schoolzero.edu'
    assert db.get_email_from_username('user2') == 'user@schooltwo.edu'
    assert db.get_email_from_username('user3') == 'user@schoolthree.edu'


def test_get_all_faculty(db):
    faculty1 = Faculty('one', 'faculty', 'faculty1', 'faculty1@school.edu',
                       False)
    faculty2 = Faculty('two', 'faculty', 'faculty2', 'faculty2@school.edu',
                       True)

    db.insert_faculty(faculty1)
    db.insert_faculty(faculty2)

    all_faculty = db.get_all_faculty()

    assert len(all_faculty) == 2

    assert (Faculty('one', 'faculty', 'faculty1', 'faculty1@school.edu', False)
            in all_faculty)
    assert (Faculty('two', 'faculty', 'faculty2', 'faculty2@school.edu', True)
            in all_faculty)


def test_get_username_from_email_raises(db):
    with pytest.raises(DatabaseException):
        db.get_username_from_email('email@school.edu')


def test_get_email_from_username(db):
    with pytest.raises(DatabaseException):
        db.get_email_from_username('username')


def test_admin(db):
    faculty1 = Faculty('last1', 'first1', 'faculty1', 'faculty1@school.edu',
                       True)
    faculty2 = Faculty('last2', 'first2', 'faculty2', 'faculty2@school.edu',
                       False)

    faculty1 = db.insert_faculty(faculty1)
    faculty2 = db.insert_faculty(faculty2)

    assert db.is_admin(faculty1.username)
    assert not db.is_admin(faculty2.username)

    # trying to remove admin when the user is not an admin should raise
    with pytest.raises(DatabaseException):
        db.remove_admin(faculty2.username)

    db.set_admin(faculty2.username)

    assert db.is_admin(faculty1.username)
    assert db.is_admin(faculty2.username)

    db.remove_admin(faculty1.username)

    assert not db.is_admin(faculty1.username)
    assert db.is_admin(faculty2.username)

    with pytest.raises(DatabaseException):
        db.remove_admin(faculty1.username)

    # trying to remove the only admin user should raise
    with pytest.raises(DatabaseException):
        db.remove_admin(faculty2.username)


def test_classes(db):
    db.insert_faculty(Faculty('one', 'faculty', 'faculty1',
                              'faculty1@school.edu', False))
    assert not db.class_exists('class', 'faculty1')
    db.insert_class('class', 'faculty1')
    assert db.class_exists('class', 'faculty1')
    assert db.class_is_open('class', 'faculty1')

    with pytest.raises(DatabaseException):
        db.insert_class('class', 'faculty1')

    # ensure a second faculty member can create a class with the same name
    db.insert_faculty(Faculty('two', 'faculty', 'faculty2',
                              'faculty2@school.edu', False))
    db.insert_class('class', 'faculty2')
    assert db.class_exists('class', 'faculty2')

    db.insert_class('class2', 'faculty1')
    assert db.class_exists('class2', 'faculty1')

    expected_classes = ['class', 'class2']

    assert sorted(db.get_faculty_class_names('faculty1')) == expected_classes

    db.close_class('class', 'faculty1')
    assert not db.class_is_open('class', 'faculty1')
    assert db.class_is_open('class2', 'faculty1')


def test_class_students(db):
    student1 = Student('one', 'student', 'student1', 'student1@school.edu')
    student2 = Student('two', 'student', 'student2', 'student2@school.edu')

    db.insert_faculty(Faculty('one', 'faculty', 'faculty1',
                              'faculty1@school.edu', False))
    db.insert_class('class', 'faculty1')

    db.insert_student(student1)
    db.insert_student(student2)

    db.add_student_to_class('class', student1, 'faculty1')
    db.add_student_to_class('class', student2, 'faculty1')

    with pytest.raises(DatabaseException):
        db.add_student_to_class('class', student1, 'faculty1')

    assert (db.get_class_student_by_username('student1', 'class', 'faculty1')
            == student1)
    assert (db.get_class_student_by_username('student2', 'class', 'faculty1')
            == student2)
    with pytest.raises(DatabaseException):
        db.get_class_student_by_username('student3', 'class', 'faculty1')

    expected_students = [
        Student('one', 'student', 'student1', 'student1@school.edu'),
        Student('two', 'student', 'student2', 'student2@school.edu'),
    ]

    students = db.get_class_students('class', 'faculty1')
    assert len(students) == 2
    for student in expected_students:
        assert student in students

    db.deactivate_student_in_class('class', 'student1@school.edu', 'faculty1')
    assert not db.student_in_class('student1@school.edu', 'class', 'faculty1')
    assert db.student_inactive_in_class('student1@school.edu', 'class',
                                        'faculty1')

    students = db.get_class_students('class', 'faculty1')
    assert students == [Student('two', 'student', 'student2',
                                'student2@school.edu')]

    db.activate_student_in_class('class', 'student1@school.edu', 'faculty1')
    assert db.student_in_class('student1@school.edu', 'class', 'faculty1')
    assert not db.student_inactive_in_class('student1@school.edu', 'class',
                                            'faculty1')

    students = db.get_class_students('class', 'faculty1')
    assert len(students) == 2
    for student in expected_students:
        assert student in students

    with pytest.raises(DatabaseException):
        db.add_student_to_class('asdf', student1, 'asdf')


def test_change_student_name(db):
    student1 = Student('one', 'student', 'student1', 'student1@school.edu')
    student2 = Student('two', 'student', 'student2', 'student2@school.edu')

    db.insert_faculty(Faculty('one', 'faculty', 'faculty1',
                              'faculty1@school.edu', False))
    db.insert_class('class', 'faculty1')

    db.insert_student(student1)
    db.insert_student(student2)

    db.add_student_to_class('class', student1, 'faculty1')
    db.add_student_to_class('class', student2, 'faculty1')

    student2.first_name = 'new_first'
    student2.last_name = 'new_last'

    db.change_student_name(student2, 'class', 'faculty1')

    changed_student = db.get_class_student_by_username(student2.username,
                                                       'class', 'faculty1')
    unchanged_student = db.get_class_student_by_username(student1.username,
                                                         'class', 'faculty1')

    assert changed_student.first_name == 'new_first'
    assert changed_student.last_name == 'new_last'

    assert unchanged_student.first_name == 'student'
    assert unchanged_student.last_name == 'one'


def test_byte_counts(db):
    byte_counts = {
        'first/path': 100,
        'second/path': 200,
    }

    db.update_byte_counts(byte_counts)

    assert db.get_byte_count('first/path') == 100
    assert db.get_byte_count('second/path') == 200

    with pytest.raises(DatabaseException):
        db.get_byte_count('third/path')

    assert (set(db.get_byte_counts()) ==
            {('first/path', 100), ('second/path', 200)})

    byte_counts['second/path'] = 300

    db.update_byte_counts(byte_counts)

    assert db.get_byte_count('first/path') == 100
    assert db.get_byte_count('second/path') == 300

    db.delete_byte_count('first/path')

    assert db.get_byte_count('second/path') == 300

    with pytest.raises(DatabaseException):
        db.get_byte_count('first/path')


def test_assignment(db):
    faculty1 = Faculty('last1', 'first1', 'faculty1', 'faculty1@school.edu',
                       True)
    faculty2 = Faculty('last2', 'first2', 'faculty2', 'faculty2@school.edu',
                       False)

    db.insert_faculty(faculty1)
    db.insert_faculty(faculty2)

    db.insert_class('class1', 'faculty1')
    db.insert_class('class2', 'faculty1')

    db.insert_class('class1', 'faculty2')
    db.insert_class('class2', 'faculty2')

    assignments = [
        ('class1', 'assignment1', 'faculty1'),
        ('class1', 'assignment2', 'faculty1'),
        ('class2', 'assignment1', 'faculty1'),
        ('class2', 'assignment2', 'faculty1'),
        ('class1', 'assignment1', 'faculty2'),
        ('class1', 'assignment2', 'faculty2'),
        ('class2', 'assignment1', 'faculty2'),
        ('class2', 'assignment2', 'faculty2'),
    ]

    for class_name, assignment_name, faculty_username in assignments:
        db.insert_assignment(class_name, assignment_name, faculty_username)

    published = {}

    for assignment in assignments:
        published[assignment] = False

    for class_name, assignment_name, faculty_username in assignments:
        expected = published[(class_name, assignment_name, faculty_username)]
        actual = db.is_published(class_name, assignment_name, faculty_username)
        assert actual == expected

    db.set_published('class1', 'assignment2', 'faculty1')
    published[('class1', 'assignment2', 'faculty1')] = True

    db.set_published('class2', 'assignment1', 'faculty2')
    published[('class2', 'assignment1', 'faculty2')] = True

    for class_name, assignment_name, faculty_username in assignments:
        expected = published[(class_name, assignment_name, faculty_username)]
        actual = db.is_published(class_name, assignment_name, faculty_username)
        assert actual == expected

    with pytest.raises(DatabaseException):
        db.insert_assignment('class1', 'assignment1', 'faculty1')

    with pytest.raises(DatabaseException):
        db.remove_assignment('class1', 'assignment1', 'faculty3')

    db.remove_assignment('class1', 'assignment2', 'faculty1')

    with pytest.raises(DatabaseException):
        db.is_published('class1', 'assignment2', 'faculty1')

    with pytest.raises(DatabaseException):
        db.set_published('asdf', 'asdf', 'asdf')


def test_disable_assignment(db):
    faculty = Faculty('last', 'first', 'faculty', 'faculty@school.edu',
                       False)
    db.insert_faculty(faculty)
    db.insert_class('class', 'faculty')

    db.insert_assignment('class', 'assgn1', 'faculty')
    db.insert_assignment('class', 'assgn2', 'faculty')
    db.insert_assignment('class', 'assgn3', 'faculty')

    assert not db.is_disabled('class', 'assgn1', 'faculty')
    assert not db.is_disabled('class', 'assgn2', 'faculty')
    assert not db.is_disabled('class', 'assgn3', 'faculty')

    db.set_published('class', 'assgn2', 'faculty')

    with pytest.raises(DatabaseException):
        db.disable_assignment('class', 'assgn1', 'faculty')

    db.disable_assignment('class', 'assgn2', 'faculty')

    assert not db.is_disabled('class', 'assgn1', 'faculty')
    assert db.is_disabled('class', 'assgn2', 'faculty')
    assert not db.is_disabled('class', 'assgn3', 'faculty')

    with pytest.raises(DatabaseException):
        db.insert_assignment('class', 'assgn2', 'faculty')


def test_get_class_assignments(db):
    faculty = Faculty('last', 'first', 'faculty', 'faculty@school.edu',
                       False)
    db.insert_faculty(faculty)
    db.insert_class('class', 'faculty')

    db.insert_assignment('class', 'assgn1', 'faculty')
    db.insert_assignment('class', 'assgn2', 'faculty')
    db.insert_assignment('class', 'assgn3', 'faculty')

    db.set_published('class', 'assgn2', 'faculty')
    db.set_published('class', 'assgn3', 'faculty')
    db.disable_assignment('class', 'assgn3', 'faculty')

    all_assignments = db.get_class_assignments('class', 'faculty',
                                               include_disabled=True)

    assert len(all_assignments) == 3

    assgn1 = Assignment('assgn1', 'class', 'faculty', False, False)
    assgn2 = Assignment('assgn2', 'class', 'faculty', True, False)
    assgn3 = Assignment('assgn3', 'class', 'faculty', True, True)

    for assignment in (assgn1, assgn2, assgn3):
        assert assignment in all_assignments

    enabled_assignments = db.get_class_assignments('class', 'faculty')

    assert len(enabled_assignments) == 2

    assgn1 = Assignment('assgn1', 'class', 'faculty', False, False)
    assgn2 = Assignment('assgn2', 'class', 'faculty', True, False)

    for assignment in (assgn1, assgn2):
        assert assignment in enabled_assignments

