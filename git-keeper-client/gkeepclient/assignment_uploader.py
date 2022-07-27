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

"""Provides the AssignmentUploader class for uploading assignments."""

import os

from gkeepclient.server_interface import server_interface
from gkeepcore.upload_directory import UploadDirectory


class AssignmentUploader:
    """
    Provides functionality for uploading specific parts of an assignment to
    the server.
    """
    def __init__(self, upload_dir: UploadDirectory):
        """
        Constructor.

        Assumes server_interface is already connected to the server.

        :param upload_dir: UploadDirectory object representing the local
         assignment directory to be uploaded.
        """

        self._upload_dir = upload_dir
        self._target_path = server_interface.create_new_upload_dir()

    def get_target_path(self):
        """
        Getter for the target path, which is a directory on the server to
        upload to.

        :return: the target path
        """
        return self._target_path

    def upload_base_code(self):
        """Upload the base_code directory to the server."""
        target = os.path.join(self._target_path, 'base_code')
        server_interface.copy_directory(self._upload_dir.base_code_path,
                                        target)

    def upload_email_txt(self):
        """Upload email.txt to the server."""
        target = os.path.join(self._target_path, 'email.txt')
        server_interface.copy_file(self._upload_dir.email_path, target)

    def upload_tests(self):
        """Upload the tests directory to the server."""
        target = os.path.join(self._target_path, 'tests')
        server_interface.copy_directory(self._upload_dir.tests_path, target)

    def upload_config(self):
        """
        Upload the assignment.cfg if it is present in the assignment.
        If not create a default empty file.
        """
        target = os.path.join(self._target_path, 'assignment.cfg')
        if os.path.exists(self._upload_dir.config_path):
            server_interface.copy_file(self._upload_dir.config_path, target)
        else:
            server_interface.create_empty_file(target)
