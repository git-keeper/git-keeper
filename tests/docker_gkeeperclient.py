
from tests.docker_command import DockerCommand
import os


def start_docker_gitkeepclient(debug_output = False):

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
        .add("-v " + this_file_dir + "/client_files/ssh:/home/prof/.ssh")\
        .add("-v " + this_file_dir + "/client_files/config:/home/prof/.config")\
        .add("-v " + this_file_dir + "/client_files/gitconfig:/home/prof/.gitconfig")\
        .add("-v " + this_file_dir + "/client_files/test_assign:/home/prof/test_assign")\
        .add("-v " + parent_dir + "/git-keeper-core:/home/prof/git-keeper-core")\
        .add("-v " + parent_dir + "/git-keeper-client:/home/prof/git-keeper-client")\
        .add("git-keeper-client")\
        .run()

    if run_exit_code != 0:
        raise RuntimeError("Non-zero exit code when starting server.")

    core_install_exit_code = DockerCommand('exec', output=debug_output)\
        .add('-i')\
        .add('git-keeper-client bash -c "cd /home/prof/git-keeper-core && python3 setup.py install"')\
        .run()

    if core_install_exit_code != 0:
        raise RuntimeError("Non-zero exit code when installing git-keeper-core")

    client_install_exit_code = DockerCommand('exec', output=debug_output)\
        .add('-i')\
        .add('git-keeper-client bash -c "cd /home/prof/git-keeper-client && python3 setup.py install"')\
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

