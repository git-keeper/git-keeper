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
def email(to, contains):
    for file in glob.glob('/email/{}_*.txt'.format(to)):
        with open(file) as f:
            if contains in f.read():
                return True
    return False


print(email(sys.argv[1], sys.argv[2]))
