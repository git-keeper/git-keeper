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

"""Provides a function for publishing an assignment on the server."""

import sys

from gkeepclient.client_function_decorators import server_interface_connected,\
    config_parsed, class_exists, assignment_exists, assignment_not_published
from gkeepclient.server_response_poller import communicate_event


@config_parsed
@server_interface_connected
@class_exists
@assignment_exists
@assignment_not_published
def publish_assignment(class_name: str, assignment_name: str):
    """
    Publish an assignment on the server.

    The server will send emails to all students with clone URLs.

    :param class_name: name of the class the assignment belongs to
    :param assignment_name: name of the assignment
    """

    print('Publishing assignment', assignment_name, 'in class', class_name)

    payload = '{0} {1}'.format(class_name, assignment_name)

    communicate_event('PUBLISH', payload,
                      success_message='Assignment successfully published',
                      error_message='Error publishing assignment:',
                      timeout_message='Server response timeout. '
                                      'Publish status unknown.')


if __name__ == '__main__':
    publish_assignment(sys.argv[1], sys.argv[2])
