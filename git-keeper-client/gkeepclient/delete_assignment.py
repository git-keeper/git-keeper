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

from gkeepclient.client_function_decorators import config_parsed, \
    server_interface_connected, class_exists, assignment_exists
from gkeepclient.server_response_poller import communicate_event
from gkeepcore.gkeep_exception import GkeepException


class DeleteAssignmentError(GkeepException):
    """Raised if there are any errors deleting the assignment."""
    pass


@config_parsed
@server_interface_connected
@class_exists
@assignment_exists
def delete_assignment(class_name: str, assignment_name: str,
                      response_timeout=20):
    """
    Delete an assignment on the server.

    Raises DeleteAssignmentError if anything goes wrong.

    :param class_name: name of the class the assignment belongs to
    :param assignment_name: name of the assignment
    :param response_timeout: seconds to wait for server response
    """

    print('Deleting assignment', assignment_name, 'in class', class_name)

    payload = '{0} {1}'.format(class_name, assignment_name)

    communicate_event('DELETE', payload, response_timeout=response_timeout,
                      success_message='Assignment deleted successfully',
                      error_message='Error deleting response:',
                      timeout_message='Server response timeout. '
                                      'Delete status unknown')


if __name__ == '__main__':
    delete_assignment(sys.argv[1], sys.argv[2])
