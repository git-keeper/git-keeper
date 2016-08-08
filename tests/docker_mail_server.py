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


def start_docker_mail_server(email_save_dir, debug_output = False):
    """
    Start the git-keeper mail server in a Docker container.  This will rebuild
    the image for the container if necessary, and start the container.  The
    server listens on port 25 and saves all email to files rather than
    sending the files (1.txt, 2.txt, etc.).

    This function will raise a RuntimeError if a non-zero return value
    occurs when running any step of the process.

    :param email_save_dir: a folder where email will be saved.
    :param debug_output: whether to produce debugging out to stdout.
    :return: None
    """

    this_file_dir = os.path.dirname(os.path.realpath(__file__))
    parent_dir = os.path.abspath(os.path.join(this_file_dir, os.pardir))

    # make sure the containers are built
    build_exit_code = DockerCommand("build", output=debug_output)\
        .add("-t git-keeper-mailer")\
        .add(this_file_dir + "/git-keeper-mailer")\
        .run()

    if build_exit_code != 0:
        raise RuntimeError("Non-zero exit code on docker build.")

    # Bring the mail server up
    # -d  - detach the container (run as deamon)
    # -P  - publish all ports (in our case, just 25)
    # --name=... a name so we don't have to refer to the container ID
    #--net=..., --ip=... --hostname=... fix the network info
    #     (dependent on the docker network command, above
    #     See: http://stackoverflow.com/questions/27937185/assign-static-ip-to-docker-container
    # -v ... - mount a volume so we can see the mail from outside the container
    run_exit_code = DockerCommand("run", output=debug_output)\
        .add("-d")\
        .add("-P")\
        .add("--privileged")\
        .add("--name=git-keeper-mailer")\
        .add("--net=git-keeper")\
        .add("--ip=172.18.0.25")\
        .add("--hostname=gkmailer")\
        .add("-v " + email_save_dir + ":/email")\
        .add("git-keeper-mailer")\
        .run()

    if run_exit_code != 0:
        raise RuntimeError("Non-zero exit code when starting server.")


def stop_docker_mail_server(debug_output = False):
    """
    Stop the container and remove it.

    This function will raise a RuntimeError if any step returns a
    non-zero value (but all steps will still be attempted).

    :param debug_output: whether to send debug output to the screen.
    :return: None
    """

    # Stop server and remove its container
    stop_exit_code = DockerCommand("stop", output=debug_output)\
        .add("git-keeper-mailer").run()

    rm_exit_code = DockerCommand("rm", output=debug_output)\
        .add("-v").add("git-keeper-mailer").run()

    if stop_exit_code != 0:
        raise RuntimeError("Non-zero exit code when stopping mailer")

    if rm_exit_code != 0:
        raise RuntimeError("Non-zero exit code when removing mailer container")
