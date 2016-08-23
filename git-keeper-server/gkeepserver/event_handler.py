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


"""Provides an abstract base class for event handlers."""


import abc

from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.log_file import LogEvent
from gkeepcore.path_utils import user_from_log_path
from gkeepserver.handler_utils import log_gkeepd_to_faculty


class HandlerException(GkeepException):
    """Raised if anything goes wrong with the handler."""
    pass


class EventHandler(metaclass=abc.ABCMeta):
    """Base class for objects which handle logged events.

    The constructor takes in the information from the log and calls
    _parse_payload().

    It is the responsibility of classes which inherit from EventHandler to
    implement _parse_payload() and handle().

    Subclasses should also implement __repr__ for debugging.

    _parse_payload() should simply extract any needed information from the
    log data and store the information in private attributes. If there are
    any syntax errors in the log information it must raise a
    HandlerException. It should verify syntax but it should *not* check
    semantics.

    handle() should verify that the information is valid and then do what is
    necessary to handle the event.

    handle() will be called in the main thread, while _parse_payload will be
    called in the log event parsing thread.

    The event type is not a parameter for the constructor, because each event
    type has its own EventHandler subclass.

    """

    def __init__(self, log_path: str, log_event: LogEvent):
        """
        Store the information from the log and call _parse_payload()

        :param log_path: path to the log file that the information came from
        :param log_event: LogEvent object representing the event
        """
        self._log_path = log_path
        self._log_event = log_event
        self._timestamp = log_event.timestamp
        self._event_type = log_event.event_type
        self._payload = log_event.payload

        self._parse_log_path()
        self._parse_payload()

    @abc.abstractmethod
    def _parse_payload(self):
        """Parse the payload."""

    @abc.abstractmethod
    def handle(self):
        """Handle the event in an appropriate way."""

    def _parse_log_path(self):
        """
        Extract the faculty username from the log file path.

        Raises:
             HandlerException

        Initializes attributes:
            _faculty_username
        """

        self._faculty_username = user_from_log_path(self._log_path)

        if self._faculty_username is None:
            raise HandlerException('Malformed log path: {0}'
                                   .format(self._log_path))

    def _report_success(self, payload=''):
        # Report success to the faculty through a log

        event_type = self._event_type + '_SUCCESS'

        log_gkeepd_to_faculty(self._faculty_username, event_type, payload)

    def _report_error(self, payload=''):
        # Report error to the faculty through a log

        event_type = self._event_type + '_ERROR'

        log_gkeepd_to_faculty(self._faculty_username, event_type, payload)

    def _report_warning(self, payload=''):
        # Report error to the faculty through a log

        event_type = self._event_type + '_WARNING'

        log_gkeepd_to_faculty(self._faculty_username, event_type, payload)
