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


"""Tests for class Student from gkeepcore.student"""


from gkeepcore.student import Student


def test_from_csv_row():
    row = ['Last', 'First', 'username@school.edu']

    student = Student.from_csv_row(row)

    assert student.first_name == 'First'
    assert student.last_name == 'Last'
    assert student.username == 'username'
    assert student.email_address == 'username@school.edu'


def test_from_csv_row_with_spaces():
    row = [' Last   ', ' First ', '   username@school.edu  ']

    student = Student.from_csv_row(row)

    assert student.first_name == 'First'
    assert student.last_name == 'Last'
    assert student.username == 'username'
    assert student.email_address == 'username@school.edu'


def test_get_last_first_username():
    row = ['Doe', 'Jane', 'jdoe@school.edu']

    student = Student.from_csv_row(row)

    assert student.get_last_first_username() == 'doe_jane_jdoe'


def test_get_last_first_username_normalization():
    row = ['Müller', 'José', 'jmuller@school.edu']

    student = Student.from_csv_row(row)

    assert student.get_last_first_username() == 'muller_jose_jmuller'
