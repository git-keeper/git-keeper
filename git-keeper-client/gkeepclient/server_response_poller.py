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
Provides functionality for polling the server log for responses to an
action.
"""

from enum import Enum
from time import sleep, time

from gkeepclient.server_interface import server_interface
from gkeepclient.server_log_file_reader import ServerLogFileReader
from gkeepcore.gkeep_exception import GkeepException


class ServerResponseType(Enum):
    """
    Enum used to indicate the type of the server response.
    """
    SUCCESS = 0
    ERROR = 1
    WARNING = 2
    TIMEOUT = 3


class ServerResponse:
    """
    ServerResponse objects are yielded from the ServerResponsePoller's
    response generator.
    """
    def __init__(self, response_type: ServerResponseType, message=''):
        self.response_type = response_type
        self.message = message


class ServerResponseWarning(GkeepException):
    """Exception to be raised on a warning from the server."""
    pass


class ServerResponseError(GkeepException):
    """Exception to be raised on an error from the server."""
    pass


class ServerResponsePoller:
    """
    Allows polling a server log file watching for certain types of response
    events.

    For example, if you issue a PUBLISH request, the server will respond with
    either PUBLISH_SUCCESS, PUBLISH_ERROR, or PUBLISH_WARNING messages.

    Create a ServerResponsePoller object *before* issuing a request so you are
    sure not to miss a response, then iterate over a call to
    response_generator() after issuing the request.
    """
    def __init__(self, event_type: str, timeout):
        """
        Constructor

        :param event_type: type of the request
        :param timeout: number of seconds to wait before yielding a timeout
        """
        self._event_type = event_type
        self._success_type = event_type + '_SUCCESS'
        self._error_type = event_type + '_ERROR'
        self._warning_type = event_type + '_WARNING'

        self._timeout = timeout

        gkeepd_log_path = server_interface.gkeepd_to_me_log_path()
        self._reader = ServerLogFileReader(gkeepd_log_path)

    def response_generator(self):
        """
        Yield responses until success, error, or timeout.

        Numerous warnings may be yielded.

        :return: an iterator over server responses
        """
        poll_start_time = time()

        # poll for the server's response
        while True:
            while not self._reader.has_new_lines():
                sleep(0.1)
                if time() > poll_start_time + self._timeout:
                    yield ServerResponse(ServerResponseType.TIMEOUT)
                    return

            for event in self._reader.get_new_events():
                if event.event_type == self._success_type:
                    yield ServerResponse(ServerResponseType.SUCCESS,
                                         event.payload)
                    return
                if event.event_type == self._error_type:
                    yield ServerResponse(ServerResponseType.ERROR,
                                         event.payload)
                    return
                if event.event_type == self._warning_type:
                    yield ServerResponse(ServerResponseType.WARNING,
                                         event.payload)


def communicate_event(event_type: str, payload: str, response_timeout=20,
                      success_message=None, error_message=None,
                      warning_message=None, timeout_message=None):
    """
    Log an event on the server to initiate server action and wait for server's
    response.

    Prints success_message if the action was successful. Raises a
    GkeepException with an error or warning message if something went wrong.

    :param event_type: type of the event logged
    :param payload: payload of the event
    :param response_timeout: seconds to wait before reporting a timeout
    :param success_message: message to print if the server handled the
     event successfully
    :param error_message: prefix to add to the server's error response message
    :param warning_message: prefix to add to the server's warning response
     message
    :param timeout_message: error message for a timeout
    """

    poller = ServerResponsePoller(event_type, response_timeout)

    server_interface.log_event(event_type, payload)

    for response in poller.response_generator():
        if response.response_type == ServerResponseType.SUCCESS:
            if success_message is not None:
                print(success_message)
        elif response.response_type == ServerResponseType.ERROR:
            message = (error_message or '') + response.message
            raise ServerResponseError(message)
        elif response.response_type == ServerResponseType.WARNING:
            message = (warning_message or '') + response.message
            raise ServerResponseWarning(message)
        elif response.response_type == ServerResponseType.TIMEOUT:
            if timeout_message is not None:
                raise GkeepException(timeout_message)
