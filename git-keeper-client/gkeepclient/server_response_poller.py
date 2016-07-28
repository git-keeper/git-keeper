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


class ServerResponsePollerError(Exception):
    pass


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
                sleep(0.5)
                if time() > poll_start_time + self._timeout:
                    yield ServerResponse(ServerResponseType.TIMEOUT)
                    return

            for line in self._reader.get_new_lines():
                if self._success_type in line:
                    yield ServerResponse(ServerResponseType.SUCCESS)
                    return
                if self._error_type in line:
                    yield ServerResponse(ServerResponseType.ERROR, line)
                    return
                if self._warning_type in line:
                    yield ServerResponse(ServerResponseType.WARNING, line)
