# Copyright 2018 Nathan Sommer and Ben Coleman
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


from gkeeprobot.dectorators import polling
import glob
import sys


@polling
def email(to, subject_contains=None, body_contains=None):
    for file in glob.glob('/email/{}_*.txt'.format(to)):
        if check_email_contains(file, subject_contains=subject_contains, body_contains=body_contains):
            return True
    return False

def check_email_contains(filename, subject_contains=None, body_contains=None):
    with open(filename) as f:
        from_line = f.readline()
        subject_line = f.readline()
        body = f.read()

        if subject_contains is not None and subject_contains not in subject_line:
            return False

        if body_contains is not None and body_contains not in body:
            return False

        return True


print(email(sys.argv[1], subject_contains=sys.argv[2], body_contains=sys.argv[3]))
