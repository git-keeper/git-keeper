# Copyright 2022 Nathan Sommer and Ben Coleman
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


from gkeepcore.system_commands import mkdir, touch, cp
from gkeepcore.gkeep_exception import GkeepException
from gkeepclient.client_configuration import config
import os


def new_assignment(assignment_path, assignment_template=None):
    """
    Create the files and folders for a new assignment

    :param assignment_path: path where the assignment should be created
    :param assignment_template: the base files to use to create the assignment
    """

    if os.path.exists(assignment_path):
        raise GkeepException('Directory already exists: {}'.format(assignment_path))

    if assignment_template is None:
        if os.path.exists(os.path.join(config.templates_path, 'default')):
            new_assignment_from_template(assignment_path, 'default')
        else:
            new_default_assignment(assignment_path)
    else:
        new_assignment_from_template(assignment_path, assignment_template)


def new_default_assignment(assignment_path):
    """
    Create a directory containing the required files and directories:
      base_code, email.txt, tests, action.sh, and assignment.cfg
    """
    mkdir(assignment_path)
    mkdir('{}/base_code'.format(assignment_path))
    touch('{}/email.txt'.format(assignment_path))
    mkdir('{}/tests'.format(assignment_path))
    touch('{}/tests/action.sh'.format(assignment_path))
    touch('{}/assignment.cfg'.format(assignment_path))


def new_assignment_from_template(assignment_path, assignment_template):
    """
    Create an assignment from a template
    """
    templates_path = os.path.join(config.templates_path, assignment_template)
    if not os.path.exists(templates_path):
        raise GkeepException('Unknown template: {}'.format(templates_path))
    cp(templates_path, assignment_path, recursive=True)
