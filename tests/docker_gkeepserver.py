
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


def start_docker_gkeepserver(server_home_dir, debug_output = False):
    """
    Start the git-keeper server in a Docker container.  This will rebuild
    the image for the container, create a docker network for the container,
    start the container, install git-keeper-core and git-keeper-server, and
    the start the server.

    This function will raise a RuntimeError if a non-zero return value
    occurs when running any step of the process.

    :param server_home_dir: a folder that contains the contents of /home on
     the server.  This is useful for setting up ssh keys and config files.
    :param debug_output: whether to produce debugging out to stdout.
    :return: None
    """

    this_file_dir = os.path.dirname(os.path.realpath(__file__))
    parent_dir = os.path.abspath(os.path.join(this_file_dir, os.pardir))


    # make sure the containers are built
    build_exit_code = DockerCommand("build", output=debug_output)\
        .add("-t git-keeper-server")\
        .add(this_file_dir + "/git-keeper-server")\
        .run()

    if build_exit_code != 0:
        raise RuntimeError("Non-zero exit code on docker build.")

    # make sure the network has been created
    # If the network was already created this will produce an error message,
    # but it won't hurt anything if it does.  No exit code check.
    DockerCommand("network", output=debug_output)\
        .add("create")\
        .add("--subnet=172.18.0.0/16")\
        .add("git-keeper")\
        .run()

    # Bring the server up
    # -d  - detach the container (run as deamon)
    # -P  - publish all ports (in our case, just 22)
    # --privileged necessary for docker in docker See https://github.com/jpetazzo/dind
    # --name=... a name so we don't have to refer to the container ID
    #--net=..., --ip=... --hostname=... fix the network info (dependent on the docker network
    #     command, above
    #     See: http://stackoverflow.com/questions/27937185/assign-static-ip-to-docker-container
    # -v .../server_files - mount various docker volumes
    #     ssh - RSA key, authorized_keys, and known_hosts
    #     config - configuration file for server
    # -v .../git-keeper-core and git-keeper-server
    run_exit_code = DockerCommand("run", output=debug_output)\
        .add("-d")\
        .add("-P")\
        .add("--privileged")\
        .add("--name=git-keeper-server")\
        .add("--net=git-keeper")\
        .add("--ip=172.18.0.42")\
        .add("--hostname=gkserver")\
        .add("--link git-keeper-mailer:gkmailer")\
        .add("-v " + server_home_dir + ":/home")\
        .add("-v " + parent_dir + "/git-keeper-core:/git-keeper-core")\
        .add("-v " + parent_dir + "/git-keeper-server:/git-keeper-server")\
        .add("git-keeper-server")\
        .run()

    if run_exit_code != 0:
        raise RuntimeError("Non-zero exit code when starting server.")

    core_install_exit_code = DockerCommand('exec', output=debug_output)\
        .add('-i')\
        .add('git-keeper-server bash -c "cd /git-keeper-core && python3 setup.py install"')\
        .run()

    if core_install_exit_code != 0:
        raise RuntimeError("Non-zero exit code when installing git-keeper-core")

    server_install_exit_code = DockerCommand('exec', output=debug_output)\
        .add('-i')\
        .add('git-keeper-server bash -c "cd /git-keeper-server && python3 setup.py install"')\
        .run()

    if server_install_exit_code != 0:
        raise RuntimeError("Non-zero exit code when installing git-keeper-server")

    # Start the server
    # The exit code will be 0 because the docker command succeeds.  This does not
    # mean the server came up successfully.  FIXME is there anything we can do
    # to see the status?
    DockerCommand("exec", output=debug_output)\
        .add("-d")\
        .add("git-keeper-server")\
        .add("gkeepd")\
        .run()


def stop_docker_gkeepserver(debug_output = False):
    """
    Stop the container and remove it.  Afterward remove the git-keeper
    network from docker.

    This function will raise a RuntimeError if any step returns a
    non-zero value (but all steps will still be attempted).

    :param debug_output: whether to send debug output to the screen.
    :return: None
    """

    # Stop server and remove its container
    stop_exit_code = DockerCommand("stop", output=debug_output)\
        .add("git-keeper-server").run()

    rm_exit_code = DockerCommand("rm", output=debug_output)\
        .add("-v").add("git-keeper-server").run()

    # Remove the network
    network_rm_exit_code = DockerCommand("network", output=debug_output)\
        .add("rm").add("git-keeper").run()

    if stop_exit_code != 0:
        raise RuntimeError("Non-zero exit code when stopping server")

    if rm_exit_code != 0:
        raise RuntimeError("Non-zero exit code when removing server container")

    if network_rm_exit_code != 0:
        raise RuntimeError("Non-zero exit code when removing git-keeper network")
