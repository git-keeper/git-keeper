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
Provides a function for generating a random password.
"""

import random
import string


def generate_password(length=8):
    """
    Generate a password.

    The password will consist of ASCII letters and numeric digits.

    :param length: optional password character length, defaults to 8
    :return: the password
    """

    # pool of characters to draw from
    characters = string.ascii_letters + string.digits

    # select random characters from the characters string
    # using SystemRandom() is more cryptographically secure
    character_list = [random.SystemRandom().choice(characters)
                      for _ in range(length)]

    # join the characters back into a string
    password = ''.join(character_list)

    return password
