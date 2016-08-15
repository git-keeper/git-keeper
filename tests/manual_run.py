
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

"""
This script will bring up a git-keeper server and a client machine.

The server:
- is configured to create a prof account
- traps email locally to the tmp_email* folder as individual files

The client:
- has a prof account with ssh keys already copies to the server

The folder command_line contains:
- sshclient: connect to the client machine as prof.
- sshserver: connect to the server machine as keeper.


From the client keys are established so you can ssh to
- prof@gkserver
- keeper@gkserver

For convienence, the prof@gkserver password is displayed.  On the client,
the prof password is 'prof'

"""

from tests.testing_environment import TestingEnvironment

testing_env = TestingEnvironment()

input("\n\nServer running.  Hit return to stop it.")

testing_env.take_down()
