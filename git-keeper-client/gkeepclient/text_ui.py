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


def confirmation(prompt: str, default=None):
    if default == 'y':
        y_or_n = '(Y/n)'
    elif default == 'n':
        y_or_n = '(y/N)'
    else:
        y_or_n = '(y/n)'

    prompt = '{0} {1} '.format(prompt, y_or_n)

    while True:
        user_input = input(prompt)

        if len(user_input) > 0:
            first_char = user_input.lower()[0]
        else:
            first_char = default

        if first_char == 'y':
            return True
        elif first_char == 'n':
            return False

        print('Please enter y or n')
