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

import os
from gkeepcore.shell_command import run_command, CommandError


def remove_users():
    # remove everyone but vagrant, ubuntu, and keeper
    expected = ['keeper', 'vagrant', 'ubuntu']

    for user in os.listdir('/home'):
        if user not in expected:
            try:
                run_command('sudo pkill -9 -u {}'.format(user))
            except CommandError:
                pass

            run_command('sudo userdel -r {}'.format(user))


remove_users()
