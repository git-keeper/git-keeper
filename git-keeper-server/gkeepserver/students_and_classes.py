# Copyright 2016 Nathan Sommer and Ben Coleman
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
import os

from gkeepcore.local_csv_files import LocalCSVReader
from gkeepcore.path_utils import user_home_dir, faculty_classes_dir_path, \
    class_student_csv_path
from gkeepcore.student import students_from_csv


def get_faculty_class_names(faculty_username: str) -> list:
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


def get_class_students(faculty_username: str, class_name: str):
    home_dir = user_home_dir(faculty_username)

    reader = LocalCSVReader(class_student_csv_path(class_name, home_dir))

    students = students_from_csv(reader)

    return students


