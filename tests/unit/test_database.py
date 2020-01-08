import pytest

from gkeepcore.student import Student
from gkeepserver.database import Database, DatabaseException
from gkeepserver.faculty import Faculty


@pytest.fixture
def db():
    db = Database()
    db.connect(':memory:')
    return db


def test_connect_and_initialize(db):
    pass


def test_insert_student(db):
    assert not db.email_exists('student1@school.edu')

    db.insert_user('student1@school.edu', 'student', 'one', 'student')
    assert db.email_exists('student1@school.edu')
    assert db.username_exists('student1')

    db.insert_user('student1@another.edu', 'student', 'one', 'student')
    assert db.email_exists('student1@another.edu')
    assert db.username_exists('student11')

    db.insert_user('student1@yetanother.edu', 'student', 'one', 'student')
    assert db.email_exists('student1@yetanother.edu')
    assert db.username_exists('student12')

    db.insert_user('1student@yetanother.edu', 'student', 'one', 'student')
    assert db.email_exists('1student@yetanother.edu')
    assert db.username_exists('a1student')


def test_insert_faculty(db):
    db.insert_user('faculty1@school.edu', 'faculty', 'one', 'faculty')
    assert db.email_exists('faculty1@school.edu')
    assert db.username_exists('faculty1')

    db.insert_user('faculty1@another.edu', 'faculty', 'one', 'faculty')
    assert db.email_exists('faculty1@another.edu')
    assert db.username_exists('faculty11')

    db.insert_user('faculty1@yetanother.edu', 'faculty', 'one', 'faculty')
    assert db.email_exists('faculty1@yetanother.edu')
    assert db.username_exists('faculty12')

    faculty = db.get_faculty_by_username('faculty1')
    assert faculty == Faculty('one', 'faculty', 'faculty1',
                              'faculty1@school.edu', False)

    db.set_admin('faculty1')

    with pytest.raises(DatabaseException):
        db.set_admin('faculty1')

    assert db.is_admin('faculty1')

    faculty = db.get_faculty_by_username('faculty1')
    assert faculty == Faculty('one', 'faculty', 'faculty1',
                              'faculty1@school.edu', True)

    all_faculty = db.get_all_faculty()

    assert (Faculty('one', 'faculty', 'faculty1', 'faculty1@school.edu', True)
            in all_faculty)

    db.remove_admin('faculty1')

    assert not db.is_admin('faculty1')

    faculty = db.get_faculty_by_username('faculty1')
    assert faculty == Faculty('one', 'faculty', 'faculty1',
                              'faculty1@school.edu', False)

    with pytest.raises(DatabaseException):
        db.remove_admin('faculty1')


def test_insert_class(db):
    db.insert_user('faculty1@school.edu', 'faculty', 'one', 'faculty')
    assert not db.class_exists('class', 'faculty1')
    db.insert_class('class', 'faculty1')
    assert db.class_exists('class', 'faculty1')
    assert db.class_is_open('class', 'faculty1')

    with pytest.raises(DatabaseException):
        db.insert_class('class', 'faculty1')

    # ensure a second faculty member can create a class with the same name
    db.insert_user('faculty2@school.edu', 'faculty', 'two', 'faculty')
    db.insert_class('class', 'faculty2')
    assert db.class_exists('class', 'faculty2')

    db.close_class('class', 'faculty1')
    assert not db.class_is_open('class', 'faculty1')


def test_class_students(db):
    db.insert_user('faculty1@school.edu', 'faculty', 'one', 'faculty')
    db.insert_class('class', 'faculty1')

    db.insert_user('student1@school.edu', 'student', 'one', 'student')
    db.insert_user('student2@school.edu', 'student', 'two', 'student')

    db.add_student_to_class('class', 'student1', 'faculty1')
    db.add_student_to_class('class', 'student2', 'faculty1')

    with pytest.raises(DatabaseException):
        db.add_student_to_class('class', 'student1', 'faculty1')

    expected_students = [
        Student('one', 'student', 'student1', 'student1@school.edu'),
        Student('two', 'student', 'student2', 'student2@school.edu'),
    ]

    students = db.get_class_students('class', 'faculty1')

    assert len(students) == 2

    for student in expected_students:
        assert student in students


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
