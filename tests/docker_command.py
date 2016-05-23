
from subprocess import Popen, PIPE, CalledProcessError, DEVNULL, STDOUT
import os


class DockerCommand:
    """
    This class allows users to build and execute docker commands.  The class encapsulates
    automatic functionality to prepare the environment to communicate with the docker
    daemon (equivalent to eval "$(docker-machine env)") if it is not already done.

    Building a command is based on a "telescoping constructor" where each add returns
    the object.  Once built, a command may be executed multiple times.

    Argument syntax is a complex topic.
    (see http://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap12.html)
    This class does not attempt regulate how arguments are organized.  The add method
    allows any string:

    Single switches:
        .add('-d')
    Multiple switches:
        .add('-d -P')

    Output of stdout and stderr is off by default but may be enabled using an optional
    parameter on the constructor.
    """

    _config = False

    def __init__(self, command, output=False):
        """
        Construct a starting point to build the command.  If this is the first command
        to be executed, this will initialize the environment to communicate with the
        docker daemon.

        :param command: the base command within docker (string)
        :param output: (optional) whether to output stdout/stderr to the console (Boolean)
        """

        # Run the environment configuration if it has not been run
        # for any DockerCommand objects.
        if not DockerCommand._config:
            DockerCommand._do_config()
            DockerCommand._config = True

        self._command = command
        self._output = output
        self._arguments = ""

    @staticmethod
    def _do_config():
        """
        Configure the runtime environment to recognize the docker daemon.  This must be
        called before any Docker commands are run.

        NOTE: this assumes a OSX or Windows install because it uses docker-machine.  I
        have no idea how to do it in a linux environment.  :(

        :return None:
        """
        command = 'docker-machine env'
        with Popen(command, shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True) as proc:
            env_values, std_error = proc.communicate()

            for line in env_values.split('\n'):
                line = line.strip()
                if line == '' or line.startswith('#'):
                    continue

                # each line is of the form "export KEY=VALUE", so isolate the key/value
                pair = line.split()[1]
                [key, value] = pair.split('=')

                # in the shell we surround the value with quotes.  for os.putenv we don't
                value = value.strip('"')

                os.putenv(key, value)

            # This has to succeed or we cannot continue
            if proc.returncode != 0:
                raise CalledProcessError(proc.returncode, command)

    def add(self, value):
        """
        Add a parameter or parameters to the command.

        :param value: a string representing the parameters.
        :return: self
        """
        self._arguments += " " + value

        return self

    def run(self):
        """
        Execute the command.  If the command is somehow malformed, this method will
        raise a subprocess exception.

        :return: the exit code of the command
        """
        full_command = 'docker ' + self._command + self._arguments

        # If we are producing output, create a single pipe to both stdout and stderr
        if self._output:
            with Popen(full_command, shell=True, stdout=PIPE, stderr=STDOUT, universal_newlines=True) as proc:
                # This loop will terminate when the command returns
                for line in proc.stdout:
                    print(line.strip())

            return proc.returncode
        else:
            with Popen(full_command, shell=True, stdout=DEVNULL, stderr=DEVNULL) as proc:
                return proc.wait()
