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

"""
Tests for UploadDirectory

Tests that no exceptions are thrown when a valid assignment upload directory
exists, and that the proper exceptions are thrown when individual items do not
exist.

Required structure:

    assignment_directory/
        base_code/
        email.txt
        tests/
            action.sh
"""

import os

import pytest

from gkeepcore.upload_directory import UploadDirectory, UploadDirectoryError

test_path_prefix = os.path.join('tests', 'test_files', 'upload_directory')


def assert_does_not_exist_exception(path):
    with pytest.raises(UploadDirectoryError) as e:
        upload_dir = UploadDirectory(path)

    assert str(e.value) == '{0} does not exist'.format(path)


def test_everything_exists():
    path = os.path.join(test_path_prefix, 'everything_exists')
    upload_dir = UploadDirectory(path)

    assert upload_dir.path == path
    assert upload_dir.assignment_name == 'everything_exists'


def test_does_not_exist():
    path = 'bad_path'

    with pytest.raises(UploadDirectoryError) as e:
        upload_dir = UploadDirectory(path)

    assert str(e.value) == '{0} does not exist'.format(path)


def test_email_does_not_exist():
    path = os.path.join(test_path_prefix, 'no_email')
    assert_does_not_exist_exception(os.path.join(path, 'email.txt'))


def test_base_code_does_not_exist():
    path = os.path.join(test_path_prefix, 'no_base_code')
    assert_does_not_exist_exception(os.path.join(path, 'base_code'))


def test_tests_does_not_exist():
    path = os.path.join(test_path_prefix, 'no_tests')
    assert_does_not_exist_exception(os.path.join(path, 'tests'))


def test_action_sh_does_not_exist():
    path = os.path.join(test_path_prefix, 'no_action_sh')
    assert_does_not_exist_exception(os.path.join(path, 'tests', 'action.sh'))
