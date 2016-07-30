#!/usr/bin/env python3

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

"""Provides a function for deleting an assignment on the server."""

import sys

from gkeepclient.client_configuration import config, ClientConfigurationError
from gkeepclient.server_interface import server_interface, ServerInterfaceError
from gkeepclient.server_response_poller import ServerResponsePoller,\
    ServerResponseType
from gkeepcore.gkeep_exception import GkeepException


class DeleteAssignmentError(GkeepException):
    """Raised if there are any errors deleting the assignment."""
    pass


def delete_assignment(class_name: str, assignment_name: str,
                      response_timeout=20):
    """
    Delete an assignment on the server.

    Raises DeleteAssignmentError if anything goes wrong.

    :param class_name: name of the class the assignment belongs to
    :param assignment_name: name of the assignment
    :param response_timeout: seconds to wait for server response
    """

    # parse the configuration file
    try:
        config.parse()
    except ClientConfigurationError as e:
        error = 'Configuration error:\n{0}'.format(str(e))
        raise DeleteAssignmentError(error)

    # connect to the server
    try:
        server_interface.connect()
    except ServerInterfaceError as e:
        error = 'Error connecting to the server:\n{0}'.format(str(e))
        raise DeleteAssignmentError(error)

    # check to make sure the assignment path exists
    if not server_interface.assignment_exists(class_name, assignment_name):
        error = ('Assignment {0} does not exist in class {1}'
                 .format(assignment_name, class_name))
        raise DeleteAssignmentError(error)

    print('Deleting assignment', assignment_name, 'in class', class_name)

    poller = ServerResponsePoller('DELETE', response_timeout)

    payload = '{0} {1}'.format(class_name, assignment_name)

    # log the event
    try:
        server_interface.log_event('DELETE', payload)
    except ServerInterfaceError as e:
        error = 'Error logging event: {0}'.format(str(e))
        raise DeleteAssignmentError(error)

    try:
        for response in poller.response_generator():
            if response.response_type == ServerResponseType.SUCCESS:
                print('Assignment successfully deleted')
            elif response.response_type == ServerResponseType.ERROR:
                print('Error deleting response:')
                print(response.message)
            elif response.response_type == ServerResponseType.WARNING:
                print(response.message)
            elif response.response_type == ServerResponseType.TIMEOUT:
                print('Server response timeout. Delete status unknown.')
    except ServerInterfaceError as e:
        error = 'Server communication error: {0}'.format(e)
        raise DeleteAssignmentError(error)

if __name__ == '__main__':
    delete_assignment(sys.argv[1], sys.argv[2])
