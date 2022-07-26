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


from gkeepcore.system_commands import mkdir, touch


def new_assignment(assignment_path):
    mkdir(assignment_path)
    mkdir('{}/base_code'.format(assignment_path))
    touch('{}/email.txt'.format(assignment_path))
    mkdir('{}/tests'.format(assignment_path))
    touch('{}/tests/action.sh'.format(assignment_path))

    template = '''# All values are optional
# See https://github.com/git-keeper/git-keeper/blob/develop/docs/faculty/assignment-workflow.md 
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
