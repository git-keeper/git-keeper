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


"""Tests for gkeepcore.path_utils functions."""


from gkeepcore.path_utils import path_to_list, user_from_log_path


def test_path_to_list():
    # full path to file
    path_list = path_to_list('/home/student/git-keeper-student.log')
    assert ['home', 'student', 'git-keeper-student.log'] == path_list

    # relative path to directory
    path_list = path_to_list('relative/directory/path/')
    assert ['relative', 'directory', 'path'] == path_list


def test_extract_username_from_log_path():
    # valid student log path
    path = '/home/student/git-keeper-student.log'
    assert 'student' == user_from_log_path(path)

    # not a valid user log path, should return None
    path = '/home/student/git-keeper.log'
    assert user_from_log_path(path) is None

    # valid faculty relative path
    path = 'faculty/git-keeper-faculty.log'
    assert 'faculty' == user_from_log_path(path)
