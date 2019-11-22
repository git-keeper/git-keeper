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

"""Tests for functions in gkeepcore.valid_names"""

import pytest

from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.valid_names import validate_assignment_name, \
    validate_class_name, validate_username


def test_validate_assignment_name():
    valid_names = [
        'assignment',
        'assignment_one',
        'assignment_123',
        '1_assignment',
        'assignment-one',
    ]

    for name in valid_names:
        validate_assignment_name(name)

    invalid_names = [
        'all',
        ' assignment',
        'assignment ',
        'assignment one',
        '.assignment',
        'assignment.one',
        'assignmént',
    ]

    for name in invalid_names:
        with pytest.raises(GkeepException):
            validate_assignment_name(name)


def test_validate_class_name():
    valid_names = [
        'class',
        'class_one',
        'class_123',
        '1_class',
        'class-one',
    ]

    for name in valid_names:
        validate_class_name(name)

    invalid_names = [
        ' class',
        'class ',
        'class one',
        '.class',
        'class.one',
        'assignmént',
    ]

    for name in invalid_names:
        with pytest.raises(GkeepException):
            validate_class_name(name)


def test_validate_username():
    valid_names = [
        'a',
        'abc',
        'abc1',
        'abc123',
        'abc.def.ghi',
        'abcdefghijklmnopqrstuvwxyzabcdef',
    ]

    for name in valid_names:
        validate_username(name)

    invalid_names = [
        '1',
        '1a',
        '.a',
        'user/name',
        'usernamé',
        'abcdefghijklmnopqrstuvwxyzabcdefg',
    ]

    for name in invalid_names:
        with pytest.raises(GkeepException):
            validate_username(name)
