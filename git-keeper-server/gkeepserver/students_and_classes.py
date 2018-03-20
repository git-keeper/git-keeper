# Copyright 2016, 2018 Nathan Sommer and Ben Coleman
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


"""Provides functionality related to students and classes on the server."""


import os

from gkeepcore.local_csv_files import LocalCSVReader
from gkeepcore.path_utils import user_home_dir, faculty_classes_dir_path, \
    class_student_csv_path, faculty_class_status_path
from gkeepcore.student import students_from_csv, Student


def get_faculty_class_names(faculty_username: str) -> list:
    """
    Get a list of the names of all the classes owned by the faculty member.

    :param faculty_username: username of the faculty
    :return: list of class names
    """

    home_dir = user_home_dir(faculty_username)

    classes_path = faculty_classes_dir_path(home_dir)

    if not os.path.isdir(classes_path):
        return []

    class_names = []

    items = os.listdir(classes_path)

    for item in items:
        item_path = os.path.join(classes_path, item)

        if os.path.isdir(item_path):
            class_name = item

            if os.path.isfile(class_student_csv_path(class_name, home_dir)):
                class_names.append(class_name)

    return class_names


def get_class_student(faculty_username: str, class_name: str,
                      student_username: str) -> Student:
    """
    Get a Student object for a student in a class.

    Returns None if the student does not exist.

    :param faculty_username: username of the faculty
    :param class_name: name of the class
    :param student_username: username of the student
    :return: list of Student objects
    """

    home_dir = user_home_dir(faculty_username)

    for student in get_class_students(faculty_username, class_name):
        if student.username == student_username:
            return student


def get_class_students(faculty_username: str, class_name: str) -> list:
    """
    Get a list of Student objects representing all the students in a class.

    :param faculty_username: username of the faculty
    :param class_name: name of the class
    :return: list of Student objects
    """

    home_dir = user_home_dir(faculty_username)

    reader = LocalCSVReader(class_student_csv_path(class_name, home_dir))

    students = students_from_csv(reader)

    return students


def get_class_status(faculty_username: str, class_name: str) -> str:
    """
    Get the status of a class.

    :param faculty_username: username of the faculty member who owns the
     class
    :param class_name: name of the class
    :return: status of the class
    """

    home_dir = user_home_dir(faculty_username)
    status_path = faculty_class_status_path(class_name, home_dir)

    with open(status_path) as f:
        return f.read().strip()
