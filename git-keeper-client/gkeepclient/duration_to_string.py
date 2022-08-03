# Copyright 2022 Nathan Sommer and Ben Coleman
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


def duration_to_string(seconds):
    """
    Given a number of seconds, return a string of the form 4d3h10m5s

    :return: string representing the duration
    """

    seconds = int(seconds)
    minutes = None
    hours = None
    days = None

    if seconds >= 60:
        minutes = seconds // 60
        seconds = seconds % 60
    if minutes is not None and minutes >= 60:
        hours = minutes // 60
        minutes = minutes % 60
    if hours is not None and hours >= 24:
        days = hours // 24
        hours = hours % 24

    string = ''

    if days is not None:
        string += '{}d'.format(days)
    if hours is not None:
        string += '{}h'.format(hours)
    if minutes is not None:
        string += '{}m'.format(minutes)

    string += '{}s'.format(seconds)

    return string
