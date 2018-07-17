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

from gkeeprobot.control.ServerControl import ServerControl

"""Provides keywords for robotframework to wait for an expected state on the
server."""

control = ServerControl()


class ServerWaitKeywords:
    def wait_for_gkeepd(self):
        result = control.run_vm_python_script('keeper', 'server_is_running.py')
        assert result == 'True'

    def wait_for_email(self, to_user, contains):
        result = control.run_vm_python_script('keeper', 'email_to.py',
                                              to_user, contains)
        assert result == 'True'

    def wait_for_user(self, username):
        result = control.run_vm_python_script('keeper', 'user_exists.py',
                                              username)
        assert result == 'True'
