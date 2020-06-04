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


"""Provides utility functions used by EventHandler classes."""

from gkeepcore.log_file import log_append_command
from gkeepcore.path_utils import user_home_dir, gkeepd_to_faculty_log_path, \
    user_gitkeeper_path
from gkeepcore.shell_command import run_command


def log_gkeepd_to_faculty(faculty_username: str, event_type: str,
                          payload: str):
    """
    Append to the log that gkeepd uses to communicate with a faculty client.

    :param faculty_username: username of the faculty
    :param event_type: type of the event
    :param payload: event information
    """

    gitkeeper_path = user_gitkeeper_path(faculty_username)
    log_path = gkeepd_to_faculty_log_path(gitkeeper_path)

    command = log_append_command(log_path, event_type, payload)
    run_command(command)
