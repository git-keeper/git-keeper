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
import os


def new_assignment(assignment_path, assignment_template=None):
    """
    Create the files and folders for a new assignment

    :param assignment_path: path where the assignment should be created
    :param assignment_template: the base files to use to create the assignment
    """

    if assignment_template is None:
        new_default_assignment(assignment_path)
    else:
        new_assignment_from_template(assignment_path, assignment_template)


def new_default_assignment(assignment_path):
    mkdir(assignment_path)
    mkdir('{}/base_code'.format(assignment_path))
    touch('{}/email.txt'.format(assignment_path))
    mkdir('{}/tests'.format(assignment_path))
    touch('{}/tests/action.sh'.format(assignment_path))

    template = '''# All values are optional
# See https://git-keeper.readthedocs.io/en/latest/
[tests]
# env: filejail
# timeout: 60
# memory_limit: 512

[email]
# use_html: false
# announcement_subject: [{class_name}] New assignment: {assignment_name}
# results_subject: [{class_name}] {assignment_name} test results
'''
    with open('{}/assignment.cfg'.format(assignment_path), 'w') as f:
        f.write(template)


def new_assignment_from_template(assignment_path, assignment_template):
    template_path = os.path.expanduser('~/.config/git-keeper/templates/{}'.format(assignment_template))
    if not os.path.exists(template_path):
        raise GkeepException('Unknown template: {}'.format(template_path))
    cp(template_path, assignment_path, recursive=True)
