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


from gkeeprobot.dectorators import polling
import glob
import sys


@polling
def check_emails(subject_contains, body_contains):
    for file in glob.glob('/email/*.txt'):
        if check_email_contains(file, subject_contains, body_contains):
            return True
    return False


def check_email_contains(filename, subject_contains, body_contains):
    with open(filename) as f:
        from_line = f.readline()
        subject_line = f.readline()
        body = f.read()

        if subject_contains not in subject_line:
            return False

        if body_contains not in body:
            return False

        return True


print(check_emails(sys.argv[1], sys.argv[2]))
