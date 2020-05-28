# Copyright 2020 Nathan Sommer and Ben Coleman
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
Tests for get_action_script_and_interpreter() from gkeepcore.action_scripts.
"""


from gkeepcore.action_scripts import get_action_script_and_interpreter


def test_action_sh_only(tmp_path):
    action_sh_path = tmp_path / 'action.sh'
    action_sh_path.touch()

    script_name, interpreter = get_action_script_and_interpreter(tmp_path)

    assert script_name == 'action.sh'
    assert interpreter == 'bash'


def test_action_py_only(tmp_path):
    action_sh_path = tmp_path / 'action.py'
    action_sh_path.touch()

    script_name, interpreter = get_action_script_and_interpreter(tmp_path)

    assert script_name == 'action.py'
    assert interpreter == 'python3'


def test_both_action_sh_and_action_py(tmp_path):
    action_sh_path = tmp_path / 'action.sh'
    action_sh_path.touch()

    action_py_path = tmp_path / 'action.py'
    action_py_path.touch()

    script_name, interpreter = get_action_script_and_interpreter(tmp_path)

    assert script_name == 'action.sh'
    assert interpreter == 'bash'
