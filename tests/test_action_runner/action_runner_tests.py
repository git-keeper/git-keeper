"""

Need to OS walk through the various folders, open their test folders, and run their action.py
Collect their output to print from here.

"""

from gkeepcore.shell_command import run_command
import os


def run_test(test_dir, expected_output):


    print('\n\n')
    print(os.getcwd())
    new_path = os.path.join('test_assignments', test_dir, 'tests')
    print (new_path)
    os.chdir(new_path)
    output = run_command('python action.py {0}'.format('../submission')) # the
    # format here is just to pass a parameter!

    print(output+' len = ' +str(len(output)))
    print(expected_output+' len = ' +str(len(expected_output)))



    assert output == expected_output
    print('passed!')
    os.chdir('../../../../')
#    print(os.listdir(os.getcwd()))




def test_files_exist():
    run_test('files_exist/required_files_exist', 'All tests passed!\n')
    run_test('files_exist/required_files_do_not_exist', 'There was an error:'
                                                        ' test_text.txt does'
                                                        ' not exist.\n')

test_files_exist()