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


from functools import wraps

from gkeepclient.client_configuration import config
from gkeepclient.server_interface import server_interface
from gkeepcore.gkeep_exception import GkeepException


def config_parsed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not config.is_parsed():
            config.parse()

        func(*args, **kwargs)

    return wrapper


def server_interface_connected(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not server_interface.is_connected():
            server_interface.connect()

        func(*args, **kwargs)

    return wrapper


def class_exists(func):
    @wraps(func)
    def wrapper(class_name: str, *args, **kwargs):
        if not server_interface.class_exists(class_name):
            raise GkeepException('Class {0} does not exist'.format(class_name))

        func(class_name, *args, **kwargs)

    return wrapper


def class_does_not_exist(func):
    @wraps(func)
    def wrapper(class_name: str, *args, **kwargs):
        if server_interface.class_exists(class_name):
            raise GkeepException('Class {0} already exists'.format(class_name))

        func(class_name, *args, **kwargs)

    return wrapper


def assignment_exists(func):
    @wraps(func)
    def wrapper(class_name: str, assignment_name: str, *args, **kwargs):
        if not server_interface.assignment_exists(class_name, assignment_name):
            error = ('Assignment {0} does not exist in class {1}'
                     .format(class_name, assignment_name))
            raise GkeepException(error)

        func(class_name, assignment_name, *args, **kwargs)

    return wrapper


def assignment_does_not_exist(func):
    @wraps(func)
    def wrapper(class_name: str, assignment_name: str, *args, **kwargs):
        if server_interface.assignment_exists(class_name, assignment_name):
            error = ('Assignment {0} already exists in class {1}'
                     .format(class_name, assignment_name))
            raise GkeepException(error)

        func(class_name, assignment_name, *args, **kwargs)

    return wrapper


def assignment_published(func):
    @wraps(func)
    def wrapper(class_name: str, assignment_name: str, *args, **kwargs):
        if not server_interface.assignment_published(class_name,
                                                     assignment_name):
            error = ('Assignment {0} in class {1} is not published'
                     .format(class_name, assignment_name))
            raise GkeepException(error)

        func(class_name, assignment_name, *args, **kwargs)

    return wrapper


def assignment_not_published(func):
    @wraps(func)
    def wrapper(class_name: str, assignment_name: str, *args, **kwargs):
        if server_interface.assignment_published(class_name, assignment_name):
            error = ('Assignment {0} in class {1} is already published'
                     .format(class_name, assignment_name))
            raise GkeepException(error)

        func(class_name, assignment_name, *args, **kwargs)

    return wrapper


