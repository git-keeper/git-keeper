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
Provides decorators for client action functions which take care of common
setup operations and error checking.
"""


from functools import wraps

from gkeepclient.client_configuration import config
from gkeepclient.server_interface import server_interface
from gkeepcore.gkeep_exception import GkeepException


def config_parsed(func):
    """
    Function decorator. The wrapper calls config.parse() if the configuration
    is not already parsed before calling the original function

    :param func: function to decorate
    :return: the new wrapped function
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        Call config.parse() if the configuration is not already parsed, and
        then call the original function.

        :param args: positional arguments to pass on to the wrapped function
        :param kwargs: keyword arguments to pass on to the original function
        """
        if not config.is_parsed():
            config.parse()

        return func(*args, **kwargs)

    return wrapper


def server_interface_connected(func):
    """
    Function decorator. The wrapper calls server_interface.connect() if the
    interface is not already connected, and then calls the original function

    :param func: function to decorate
    :return: the new wrapped function
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        Call server_interface.connect() interface is not already connected, and
        then call the original function.

        :param args: positional arguments to pass on to the wrapped function
        :param kwargs: keyword arguments to pass on to the original function
        """
        if not server_interface.is_connected():
            server_interface.connect()

        return func(*args, **kwargs)

    return wrapper


def class_exists(func):
    """
    Function decorator for functions that have a class name as the first
    parameter. Checks to make sure the class exists on the server before
    calling the original function. Raises a GkeepException if it does not.

    Assumes server_interface is connected.

    :param func: function to decorate
    :return: the new wrapped function
    """

    @wraps(func)
    def wrapper(class_name: str, *args, **kwargs):
        """
        Raise a GkeepException if the class does not exist on the server.

        :param class_name: name of the class
        :param args: positional arguments to pass on to the wrapped function
        :param kwargs: keyword arguments to pass on to the original function
        """

        if class_name not in server_interface.get_info().class_list():
            raise GkeepException('Class {0} does not exist'.format(class_name))

        return func(class_name, *args, **kwargs)

    return wrapper


def class_is_open(func):
    """
    Function decorator for functions that have a class name as the first
    parameter. Checks to make sure the class is open before calling the
    original function. Raises a GkeepException if the class is closed.

    Assumes server_interface is connected and the class exists.

    :param func: function to decorate
    :return: the new wrapped function
    """

    @wraps(func)
    def wrapper(class_name: str, *args, **kwargs):
        """
        Raise a GkeepException if the class is closed.

        :param class_name: name of the class
        :param args: positional arguments to pass on to the wrapped function
        :param kwargs: keyword arguments to pass on to the original function
        """

        if not server_interface.is_open(class_name):
            raise GkeepException('Class {0} is closed'.format(class_name))

        return func(class_name, *args, **kwargs)

    return wrapper


def class_does_not_exist(func):
    """
    Function decorator for functions that have a class name as the first
    parameter. Checks to make sure the class does not exist on the server
    before calling the original function. Raises a GkeepException if it does.

    Assumes server_interface is connected.

    :param func: function to decorate
    :return: the new wrapped function
    """

    @wraps(func)
    def wrapper(class_name: str, *args, **kwargs):
        """
        Raise a GkeepException if the class exists on the server.

        :param class_name: name of the class
        :param args: positional arguments to pass on to the wrapped function
        :param kwargs: keyword arguments to pass on to the original function
        """
        if class_name in server_interface.get_info().class_list():
            raise GkeepException('Class {0} already exists'.format(class_name))

        return func(class_name, *args, **kwargs)

    return wrapper


def assignment_exists(func):
    """
    Function decorator for functions that have a class name as the first
    parameter and an assignment name as the second. Checks to make sure the
    assignment exists in the class on the server before calling the original
    function. Raises a GkeepException if it does not.

    Assumes server_interface is connected.

    :param func: function to decorate
    :return: the new wrapped function
    """

    @wraps(func)
    def wrapper(class_name: str, assignment_name: str, *args, **kwargs):
        """
        Raise a GkeepException if the assignment does not exist in the class
        on the server.

        :param class_name: name of the class
        :param assignment_name: name of the assignment
        :param args: positional arguments to pass on to the wrapped function
        :param kwargs: keyword arguments to pass on to the original function
        """

        assignments = server_interface.get_info().assignment_list(class_name)

        if assignment_name not in assignments:
            error = ('Assignment {0} does not exist in class {1}'
                     .format(assignment_name, class_name))
            raise GkeepException(error)

        return func(class_name, assignment_name, *args, **kwargs)

    return wrapper


def assignment_does_not_exist(func):
    """
    Function decorator for functions that have a class name as the first
    parameter and an assignment name as the second. Checks to make sure the
    assignment does not exist in the class on the server before calling the
    original function. Raises a GkeepException if it does.

    Assumes server_interface is connected.

    :param func: function to decorate
    :return: the new wrapped function
    """

    @wraps(func)
    def wrapper(class_name: str, assignment_name: str, *args, **kwargs):
        """
        Raise a GkeepException if the assignment exists in the class on the
        server.

        :param class_name: name of the class
        :param assignment_name: name of the assignment
        :param args: positional arguments to pass on to the wrapped function
        :param kwargs: keyword arguments to pass on to the original function
        """

        assignments = server_interface.get_info().assignment_list(class_name)

        if assignment_name in assignments:
            error = ('Assignment {0} already exists in class {1}'
                     .format(assignment_name, class_name))
            raise GkeepException(error)

        return func(class_name, assignment_name, *args, **kwargs)

    return wrapper


def assignment_published(func):
    """
    Function decorator for functions that have a class name as the first
    parameter and an assignment name as the second. The wrapper raises a
    GkeepException if the assignment is not published on the server before
    calling the original function.

    :param func: function to decorate
    :return: the new wrapped function
    """

    @wraps(func)
    def wrapper(class_name: str, assignment_name: str, *args, **kwargs):
        """
        Raise a GkeepException if the assignment is not published on the
        server.

        :param class_name: name of the class
        :param assignment_name: name of the assignment
        :param args: positional arguments to pass on to the wrapped function
        :param kwargs: keyword arguments to pass on to the original function
        """

        if not server_interface.get_info().is_published(class_name,
                                                        assignment_name):
            error = ('Assignment {0} in class {1} is not published'
                     .format(assignment_name, class_name))
            raise GkeepException(error)

        return func(class_name, assignment_name, *args, **kwargs)

    return wrapper


def assignment_not_published(func):
    """
    Function decorator for functions that have a class name as the first
    parameter and an assignment name as the second. The wrapper raises a
    GkeepException if the assignment is published on the server before
    calling the original function.

    :param func: function to decorate
    :return: the new wrapped function
    """

    @wraps(func)
    def wrapper(class_name: str, assignment_name: str, *args, **kwargs):
        """
        Raise a GkeepException if the assignment is published on the server,
        then call the original function.

        :param class_name: name of the class
        :param assignment_name: name of the assignment
        :param args: positional arguments to pass on to the wrapped function
        :param kwargs: keyword arguments to pass on to the original function
        """

        if server_interface.get_info().is_published(class_name,
                                                    assignment_name):
            error = ('Assignment {0} in class {1} is already published'
                     .format(assignment_name, class_name))
            raise GkeepException(error)

        return func(class_name, assignment_name, *args, **kwargs)

    return wrapper


def assignment_not_disabled(func):
    """
    Function decorator for functions that have a class name as the first
    parameter and an assignment name as the second. The wrapper raises a
    GkeepException if the assignment is disabled on the server before
    calling the original function.

    :param func: function to decorate
    :return: the new wrapped function
    """

    @wraps(func)
    def wrapper(class_name: str, assignment_name: str, *args, **kwargs):
        """
        Raise a GkeepException if the assignment is disabled on the server,
        then call the original function.

        :param class_name: name of the class
        :param assignment_name: name of the assignment
        :param args: positional arguments to pass on to the wrapped function
        :param kwargs: keyword arguments to pass on to the original function
        """

        if server_interface.get_info().is_disabled(class_name,
                                                   assignment_name):
            error = ('Assignment {0} in class {1} is disabled'
                     .format(assignment_name, class_name))
            raise GkeepException(error)

        return func(class_name, assignment_name, *args, **kwargs)

    return wrapper
