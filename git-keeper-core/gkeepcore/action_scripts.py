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


"""
Provides a function for determining what script to call and what interpreter
to use to run an assignment's tests.
"""

import os
from collections import OrderedDict


# Any of these script names can be used for the entry point of an assignment's
# tests. If more than one of these files exist, the one that appears first in
# this ordered dictionary will be used. Each script name maps to the name of
# the interpreter to use to call the script.
interpreters_by_script_name = OrderedDict([
    ('action.sh', 'bash'),
    ('action.py', 'python3'),
])


def get_action_script_and_interpreter(directory_path: str):
    """
    Given the path to an assignment's tests directory, determine which script
    will be called when running tests and what interpreter to use to call it.

    :param directory_path:
    :return: a tuple containing the name of the action script and the
     interpreter that is used to run it. Returns (None, None) if no valid
     action script was found.
    """

    if not os.path.isdir(directory_path):
        return None, None

    script_name = None
    interpreter = None

    scripts_found = set()

    for item in os.listdir(directory_path):
        full_path = os.path.join(directory_path, item)

        if os.path.isfile(full_path) and item in interpreters_by_script_name:
            scripts_found.add(item)

    for s, i in interpreters_by_script_name.items():
        if s in scripts_found:
            script_name = s
            interpreter = i
            break

    return script_name, interpreter
