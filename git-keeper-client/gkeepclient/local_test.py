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

import os
import sys
from datetime import datetime
from tempfile import TemporaryDirectory
from textwrap import fill

from gkeepcore.action_scripts import get_action_script_and_interpreter
from gkeepcore.assignment_config import AssignmentConfig, TestEnv, \
    verify_docker_installed, verify_docker_image
from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.path_utils import path_to_assignment_name
from gkeepcore.shell_command import run_command, CommandExitCodeError
from gkeepcore.student import Student
from gkeepcore.system_commands import cp, rm, mv, mkdir
from gkeepcore.temp_paths import TempPaths


def local_test(assignment_path, solution_path, cleanup):
    """
    Run an assignment's tests locally on a solution.

    The directory in which tests are run may or may optionally be cleaned up
    or left alone for later inspection.

    If the assignment uses Docker, Docker must be installed and running
    locally. If the assignment uses Firejail, it will NOT use Firejail locally.

    :param assignment_path: path to the assignment directory
    :param solution_path: path to a solution for the assignment
    :param cleanup: if True, the directory in which tests are run will be
     deleted after testing
    :return:
    """

    assignment_path = os.path.abspath(assignment_path)
    solution_path = os.path.abspath(solution_path)

    temp_path = ''

    exit_code = 0

    try:
        tests_path = os.path.join(assignment_path, 'tests')

        if not os.path.isdir(tests_path):
            raise GkeepException('No directory "tests" in {}'
                                 .format(assignment_path))

        action_script, action_script_interpreter = \
            get_action_script_and_interpreter(tests_path)

        if action_script is None:
            raise GkeepException('No action script found in {}'
                                 .format(tests_path))

        assignment_name = path_to_assignment_name(assignment_path)

        local_testing_path = os.path.join(assignment_path, 'local_testing')

        if not os.path.isdir(local_testing_path):
            mkdir(local_testing_path)

        timestamp = datetime.now().isoformat().replace(':', '-')

        temp_path = os.path.join(local_testing_path, timestamp)

        mkdir(temp_path)

        paths = TempPaths(temp_path, assignment_name)

        assignment_cfg_path = os.path.join(assignment_path, 'assignment.cfg')
        assignment_cfg = AssignmentConfig(assignment_cfg_path,
                                          TestEnv.HOST)

        print('Tests path:')
        print(tests_path)
        print('Solution path:')
        print(solution_path)
        print(fill('Copies of these directories will be created in this '
                   'testing directory:').strip())
        print(temp_path)
        print()

        if assignment_cfg.env == TestEnv.FIREJAIL:
            print(fill('The configured testing environment is firejail but '
                       'tests will be run locally without firejail, and '
                       'configured timeout and memory limits will not be '
                       'enforced. Be sure to try the tests on the server '
                       'before publishing.'))
            assignment_cfg.env = TestEnv.HOST
        elif assignment_cfg.env == TestEnv.HOST:
            print(fill('Tests will be run directly locally and configured '
                       'timeout and memory limits will not be enforced. Be '
                       'sure to try the tests on the server before '
                       'publishing.'))
        elif assignment_cfg.env == TestEnv.DOCKER:
            verify_docker_installed(location='locally')
            verify_docker_image(assignment_cfg.image)

        setup_temp_dir(solution_path, tests_path, paths, assignment_cfg)

        cmd = make_action_command(paths, assignment_cfg, assignment_name)

        print('Running tests...')

        try:
            body = run_command(cmd)
        except CommandExitCodeError as e:
            # Exit code 124 is raised on a timeout
            if e.exit_code == 124:
                body = (fill('Tests timed out. Either the submitted code '
                             'took too long to run or there is an issue '
                             'with the tests themselves.').strip())
            else:
                raise e

        print('Success!')
        print()
        print('----------------------- BEGIN RESULTS ------------------------')
        print(body)
        print('------------------------ END RESULTS -------------------------')

    except Exception as e:
        print()
        print('Error running tests:')
        print(e)
        exit_code = 1
    finally:
        if cleanup and os.path.isdir(temp_path):
            print()
            print('Removing {}'.format(temp_path))
            rm(temp_path, recursive=True)
        elif not cleanup:
            print()
            print('If you need to inspect any output files, see {}'
                  .format(temp_path))
            print()
            print(fill('If you would like to clean up testing directories in '
                       'the future, use --cleanup').strip())

    if exit_code != 0:
        sys.exit(exit_code)


def setup_temp_dir(solution_path, tests_path, paths: TempPaths,
                   assignment_cfg: AssignmentConfig):
    """
    Copy the solution and tests into a temporary directory and write
    run_action.sh

    :param solution_path: path to the solution
    :param tests_path: path to the tests
    :param paths: TempPaths object representing the paths to and in the
     temporary directory
    :param assignment_cfg: AssignmentConfig object for the assignment
    """

    cp(solution_path, paths.submission_path, recursive=True)
    cp(tests_path, paths.temp_path, recursive=True)

    if assignment_cfg.env == TestEnv.DOCKER:
        write_run_action_sh(paths.run_action_sh_path, tests_path,
                            assignment_cfg)
    else:
        write_run_action_sh(paths.run_action_sh_path, tests_path,
                            assignment_cfg, paths.temp_path)


def make_action_command(paths: TempPaths, assignment_cfg: AssignmentConfig,
                        assignment_name):
    """
    Build the command to run the tests based on the environment type.

    :param paths: TempPaths object representing the paths to the items in
     the temporary testing environment
    :param assignment_cfg: AssignmentConfig object for the assignment
    :param assignment_name: name of the assignment
    :return: the command to run the tests
    """

    if assignment_cfg.env == TestEnv.DOCKER:
        # Run a docker pull on the image here so that the output
        # is not captured in the results.  If the container image already
        # exists locally, this will return quickly
        pull_cmd = ['docker', 'pull', assignment_cfg.image]
        run_command(pull_cmd)
        cmd = make_docker_command(paths, assignment_cfg, assignment_name)
    elif assignment_cfg.env == TestEnv.HOST:
        cmd = make_host_command(paths)
    else:
        raise GkeepException('Unknown test env type {}'
                             .format(assignment_cfg.env))

    return cmd


def make_docker_command(paths: TempPaths, assignment_cfg: AssignmentConfig,
                        assignment_name):
    """
    Create the docker command used to run docker tests.

    :param paths: TempPaths object representing the paths to the items in
     the temporary testing environment
    :param assignment_cfg: AssignmentConfig object for the assignment
    :param assignment_name: name of the assignment
    :return: the docker command to run the tests
    """

    student = Student('LastName', 'FirstName', 'username',
                      'student@school.edu')

    return ['docker', 'run', '--pull', 'never', '-v',
            '{}:/git-keeper-tester'.format(paths.temp_path),
            assignment_cfg.image, 'bash',
            '/git-keeper-tester/run_action.sh',
            os.path.join('/git-keeper-tester/', assignment_name),
            student.username, student.email_address, student.last_name,
            student.first_name]


def make_host_command(paths: TempPaths):
    """
    Create the command used to run tests directly on the local host.

    :param paths: TempPaths object representing the paths to the items in
     the temporary testing environment
    :return: the command to run tests direclty on the local host
    """
    student = Student('LastName', 'FirstName', 'username',
                      'student@school.edu')

    return ['bash',
            paths.run_action_sh_path, paths.submission_path,
            student.username, student.email_address,
            student.last_name, student.first_name]


def write_run_action_sh(dest_path: str, tests_path: str,
                        assignment_config: AssignmentConfig, run_path=None):
    """
    Write run_action.sh before testing.

    The contents of the script depend on the type of action script used in the
    uploaded assignment.

    :param dest_path: directory in which to place run_action.sh
    :param tests_path: path to a directory containing the tests
    :param assignment_config: assignment.cfg data
    :param run_path: the path containing the tests folder, or None in which
     case dest_path will be used
    """
    temp_dir = TemporaryDirectory()
    temp_dir_path = temp_dir.name

    temp_run_action_sh_path = os.path.join(temp_dir_path, 'run_action.sh')

    if run_path is None:
        cd_command = ''
    else:
        cd_command = 'cd {}/tests'.format(run_path)

    if assignment_config.env == TestEnv.DOCKER:
        template = '''#!/bin/bash
{cd_command}
GLOBAL_TIMEOUT={global_timeout}
GLOBAL_MEM_LIMIT_MB={global_memory_limit}
GLOBAL_MEM_LIMIT_KB=$(($GLOBAL_MEM_LIMIT_MB * 1024))
ulimit -v $GLOBAL_MEM_LIMIT_KB
trap 'kill -INT -$pid' INT
timeout $GLOBAL_TIMEOUT {interpreter} {script_name} "$@" &
pid=$!
wait $pid
'''
    else:
        template = '''#!/bin/bash
{cd_command}
trap 'kill -INT -$pid' INT
{interpreter} {script_name} "$@" &
pid=$!
wait $pid
'''

    if assignment_config.timeout is not None:
        global_timeout = assignment_config.timeout
    else:
        if assignment_config.env == TestEnv.DOCKER:
            print(fill('There is no timeout specified in assignment.cfg, '
                       'using a timeout of 60 seconds. Consider setting a '
                       'timeout for this assignment.').strip())
            print()
        global_timeout = 60

    if assignment_config.memory_limit is not None:
        global_memory_limit = assignment_config.memory_limit
    else:
        if assignment_config.env == TestEnv.DOCKER:
            print(fill('There is no memory limit specified in assignment.cfg, '
                       'using a memory limit of 4 GB. Consider setting a '
                       'memory limit for this assignment.').strip())
        print()
        global_memory_limit = 4096

    script_name, interpreter = get_action_script_and_interpreter(tests_path)

    if script_name is None or interpreter is None:
        raise GkeepException('No valid action script found')

    run_action_sh_contents = \
        template.format(cd_command=cd_command,
                        global_timeout=global_timeout,
                        global_memory_limit=global_memory_limit,
                        interpreter=interpreter,
                        script_name=script_name)

    with open(temp_run_action_sh_path, 'w') as f:
        f.write(run_action_sh_contents)

    mv(temp_run_action_sh_path, dest_path)
