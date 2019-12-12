import pytest

from gkeepserver.database import Database, DatabaseException


@pytest.fixture
def db():
    db = Database()
    db.connect(':memory:')
    db.initialize()
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


def test_insert_class(db):
    db.insert_user('faculty1@school.edu', 'faculty', 'one', 'faculty')
    assert not db.class_exists('class', 'faculty1')
    db.insert_class('class', 'faculty1')
    assert db.class_exists('class', 'faculty1')

    with pytest.raises(DatabaseException):
        db.insert_class('class', 'faculty1')

    # ensure a second faculty member can create a class with the same name
    db.insert_user('faculty2@school.edu', 'faculty', 'two', 'faculty')
    db.insert_class('class', 'faculty2')
    assert db.class_exists('class', 'faculty2')


def test_add_students_to_class(db):
