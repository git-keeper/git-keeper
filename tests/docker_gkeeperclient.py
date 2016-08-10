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

from tests.docker_command import DockerCommand
import os


def start_docker_gitkeepclient(temp_client_home_dir, debug_output = False):

    this_file_dir = os.path.dirname(os.path.realpath(__file__))
    parent_dir = os.path.abspath(os.path.join(this_file_dir, os.pardir))

    # make sure the containers are built
    build_exit_code = DockerCommand("build", output=debug_output)\
        .add("-t git-keeper-client")\
        .add(this_file_dir + "/git-keeper-client")\
        .run()

    if build_exit_code != 0:
        raise RuntimeError("Non-zero exit code on docker build.")

    run_exit_code = DockerCommand("run", output=debug_output)\
        .add("-d")\
        .add("-P")\
        .add("--name=git-keeper-client")\
        .add("--net=git-keeper")\
        .add("--ip=172.18.0.15")\
        .add("--hostname gkclient")\
        .add("--link git-keeper-server:gkserver")\
        .add("-v " + temp_client_home_dir + ":/home")\
        .add("-v " + parent_dir + "/git-keeper-core:/git-keeper-core")\
        .add("-v " + parent_dir + "/git-keeper-client:/git-keeper-client")\
        .add("git-keeper-client")\
        .run()

    if run_exit_code != 0:
        raise RuntimeError("Non-zero exit code when starting server.")

    core_install_exit_code = DockerCommand('exec', output=debug_output)\
        .add('-i')\
        .add('git-keeper-client bash -c "cd /git-keeper-core && python3 setup.py install"')\
        .run()

    if core_install_exit_code != 0:
        raise RuntimeError("Non-zero exit code when installing git-keeper-core")

    client_install_exit_code = DockerCommand('exec', output=debug_output)\
        .add('-i')\
        .add('git-keeper-client bash -c "cd /git-keeper-client && python3 setup.py install"')\
        .run()

    if client_install_exit_code != 0:
        raise RuntimeError("Non-zero exit code when installing git-keeper-client")


def stop_docker_gkeepclient(debug_output = False):

    # Stop client and remove its container
    stop_exit_code = DockerCommand("stop", output=debug_output)\
        .add("git-keeper-client").run()

    rm_exit_code = DockerCommand("rm", output=debug_output)\
        .add("-v").add("git-keeper-client").run()

    if stop_exit_code != 0:
        raise RuntimeError("Non-zero exit code when stopping server")

    if rm_exit_code != 0:
        raise RuntimeError("Non-zero exit code when removing server container")


def run_client_command(cmd, *args, debug_output=False):

    the_args = " ".join(args)

    full_cmd = 'bash -c "cd /home/prof && ' + cmd + ' ' + the_args + '"'

    DockerCommand("exec", output=debug_output)\
        .add("--user prof")\
        .add("git-keeper-client")\
        .add(full_cmd)\
        .run(print_command=True)

