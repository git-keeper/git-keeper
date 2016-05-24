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
Provides the functions needed to read from and write to local log files using
LogFileReader and LogFileWriter.

"""


import os
from shlex import quote

from gkeepcore.log_file import LogFileException
from gkeepcore.subprocess_commands import run_command, CommandError


def byte_count_function(file_path: str) -> int:
    """
    Retrieve the number of bytes in a local file

    :param file_path: path to the file
    :return: number of bytes in the file

    """

    try:
        byte_count = os.path.getsize(file_path)
    except OSError as e:
        raise LogFileException(e)

    return byte_count


def read_bytes_function(file_path: str, seek_position: int) -> bytes:
    """
    Retrieve data as bytes from the a file from seek_position to the end

    :param file_path: path to the file
    :param seek_position: position from which to start reading in the file
    :return: string containing new text from the file
    """

    try:
        with open(file_path, 'rb') as f:
            f.seek(seek_position)
            data_bytes = f.read()
    except OSError as e:
        raise LogFileException(e)

    return data_bytes


def log_append_function(file_path: str, item_type: str, text: str):
    # keep the log line to 4KB or less to maintain write atomicity
    max_length = 4096

    time_length = 15
    type_length = len(item_type.encode())
    text_length = len(text.encode())
    spacing_length = 2

    total_length = time_length + type_length + text_length + spacing_length

    if total_length > max_length:
        diff = total_length - max_length
        text = text[:len(text) - diff - 3] + '...'

    quoted_path = quote(file_path)

    # Uses GNU date to get a precise time from the command line.
    # Won't work on OS X.
    cmd = ('echo "$(date +%s.%N | '
           'cut -c 1-15) {0} {1}" >> {2}'.format(item_type, text, quoted_path))

    try:
        run_command(cmd)
    except CommandError as e:
        # bad news if we can't append to a log
        print('LOGGING ERROR: {0}'.format(e))
