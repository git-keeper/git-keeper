#!/usr/bin/python3

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

from gkeepcore.shell_command import run_command_in_directory, run_command


print('create class')
run_command_in_directory('cs1', 'gkeep add cs1 cs1.csv')
print('upload assignment')
run_command_in_directory('cs1', 'gkeep upload cs1 assignment')
print('publish assignment')
run_command_in_directory('cs1', 'gkeep publish cs1 assignment')
print('copy ssh keys')
pw = run_command('ssh -t keeper@gkserver "grep asswo /email/potterh1.txt" | cut -f2 -d" "', stderr=None)
run_command('./set-keys potterh gkserver ' + pw)


#run_command('ssh -t keeper@gkserver "grep asswo | cut -f2 -d\" \" | xargs ./set-keys potterh gkserver"')
print('clone repo')
run_command('git clone potterh@gkserver:/home/potterh/prof/cs1/assignment.git')
print('copy solution')
run_command('cp 50names.py assignment')
print('commit')
run_command_in_directory('assignment', 'git commit -am \'done\'')
print('push')
run_command_in_directory('assignment', 'git push')
