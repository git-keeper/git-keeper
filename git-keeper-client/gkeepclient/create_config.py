# Copyright 2017 Thuy Dinh
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
Provides the function for creating a new client.cfg file.
"""

import os

from gkeepclient.text_ui import confirmation
from gkeepcore.system_commands import mkdir


def create_config():
    """
    Prompt the user for configuration parameters and creates client.cfg
    """
    dirpath = os.path.expanduser("~/.config/git-keeper/")
    filepath = os.path.join(dirpath, "client.cfg")
    if not check_config_file(dirpath, filepath):
        return
    print("Configuring gkeep")
    host_name = input("Server hostname: ")
    username = input("Username: ")
    ssh_port = input("Server SSH port (press enter for port 22): ")
    submissions_path = \
        input("Submissions fetch path (optional, press enter to skip): ")
    templates_path = \
        input("Assignment templates path (optional, press enter to skip): ")
    file_text = ("[server]\n" +
                 "host = {}\n" +
                 "username = {}\n").format(host_name, username)
    if ssh_port != '':
        file_text += ("# optional\n" +
                      "ssh_port = {}\n").format(ssh_port)
    file_text += "\n"
    file_text += ("# optional section\n" +
                  "[local]\n")
    if submissions_path != '':
        file_text += "submissions_path = {}\n".format(submissions_path)
    if templates_path != '':
        file_text += "templates_path = {}".format(templates_path)

    print("The following will be written to {}: ".format(filepath))
    print(file_text)
    if confirmation("Would you like to proceed?"):
        with open(filepath, 'w') as config_file:
            config_file.write(file_text)
    else:
        print("No file was written.")


def check_config_file(dirpath, filepath):
    """
    Check if client.cfg exist

    :param dirpath: path to the directory containing client.cfg
    :param filepath: path to client.cfg
    :return: True if we should proceed with writing client.cfg, False otherwise
    """
    if not os.path.isdir(dirpath):
        mkdir(dirpath)
    if os.path.isfile(filepath):
        return confirmation("client.cfg already exists. "
                            "Do you want to overwrite?")
    else:
        return True
