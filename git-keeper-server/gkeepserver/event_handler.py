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


import abc

from gkeepcore.gkeep_exception import GkeepException


class HandlerException(GkeepException):
    """Raised if anything goes wrong with the handler."""
    pass


class EventHandler(metaclass=abc.ABCMeta):
    """Base class for objects which handle logged events.

    The constructor takes in the information from the log and calls _parse().

    It is the responsibility of classes which inherit from EventHandler to
    implement _parse() and handle().

    Subclasses should also implement __repr__ for debugging.

    _parse() should simply extract any needed information from the log data and
    store the information in private attributes. If there are any syntax errors
    in the log information it must raise a HandlerException. It should verify
    syntax but it should *not* check semantics.

    handle() should verify that the information is valid and then do what is
    necessary to handle the event.

    handle() will be called in the main thread, while _parse will be called in
    the log event parsing thread.

    The event type is not a parameter for the constructor, because each event
    type has its own EventHandler subclass.

    """

    def __init__(self, log_path: str, timestamp: float, payload: str):
        """
        Store the information from the log and call _parse()

        :param log_path: path to the log file that the information came from
        :param timestamp: the time the event was logged, in seconds from the
                          epoch as a float
        :param payload: the rest of the text from the logged event
        """
        self._log_path = log_path
        self._timestamp = timestamp
        self._payload = payload

        self._parse()

    @abc.abstractmethod
    def _parse(self):
        """Parse the log path and payload."""

    @abc.abstractmethod
    def handle(self):
        """Handle the event in an appropriate way."""
