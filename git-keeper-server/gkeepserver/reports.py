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


import contextlib
import os
from tempfile import TemporaryDirectory
from time import time

from gkeepcore.git_commands import git_clone, git_push
from gkeepcore.system_commands import sudo_chown, mv, rm
from gkeepserver.assignments import AssignmentDirectory
from gkeepserver.server_configuration import config


@contextlib.contextmanager
def reports_clone(assignment_dir: AssignmentDirectory):
    """
    Provides a context manager to use when making changes to a reports
    repository. A clone of the repository is made in a temporary directory,
    and the path to the clone is yielded to the caller. The caller is
    responsible for adding and committing changes within this clone. Afterwords
    the clone is moved into the assignment directory, ownership is changed to
    be the faculty user, the changes in the clone are pushed to the bare
    reports repo, and then the clone is deleted.

    :param assignment_dir: AssignmentDirectory object associated with the
     assignment directory that contains the reports repository
    """

    with TemporaryDirectory() as temp_path:
        temp_reports_clone_path = os.path.join(temp_path, 'reports')
        git_clone(assignment_dir.reports_repo_path, temp_path)

        yield temp_reports_clone_path

        reports_clone_path = os.path.join(assignment_dir.path,
                                          'reports_clone_{}'.format(time()))
        mv(temp_reports_clone_path, reports_clone_path, sudo=True)

    sudo_chown(reports_clone_path, assignment_dir.faculty_username,
               config.keeper_group, recursive=True)
    git_push(reports_clone_path, sudo=True,
             user=assignment_dir.faculty_username)
    rm(reports_clone_path, recursive=True, sudo=True)
