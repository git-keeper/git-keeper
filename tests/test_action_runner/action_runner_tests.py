"""

Need to OS walk through the various folders, open their test folders, and run their action.py
Collect their output to print from here.

"""

from gkeepcore.shell_command import run_command
import os


def run_test(test_dir, expected_output):

    os.chdir(os.path.join('test_assignments', test_dir, 'tests'))
    output = run_command('python action.py {0}'.format('../submission')) # the
    # format here is just to pass a parameter!
    assert output == expected_output


def test_files_exist():
    run_test('files_exist/required_files_exist', 'All tests passed!\n')
   # run_test('files_exist/required_files_do_not_exist', 'file.txt does not
   # exist')

test_files_exist()