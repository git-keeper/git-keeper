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
    run_test('files_exist/required_files_do_not_exist', 'Error:'
                                                        ' test_text.txt does'
                                                        ' not exist.\n')
    run_test('files_exist/optional_files_exist', 'All tests passed!\n')
    run_test('files_exist/optional_files_do_not_exist', 'Warning: '
                                                   'test_optional2.txt does '
                                                   'not exist.\nAll tests passed!\n')
     ### error being printed for this is kindof weird


def test_copy_files():
     # I SHOULD CHECK IF THE FILES ARE COPIED
    run_test('copy_files/cp_req_files_exist', 'All tests passed!\n')
    run_test('copy_files/cp_req_files_dont_exist', 'All tests passed!\n')
    run_test('copy_files/cp_opt_files_exist', 'All tests passed!\n')
    run_test('copy_files/cp_opt_files_dont_exist', 'Warning: '
                                                   'test_optional2.txt does '
                                                   'not exist.\nAll tests passed!\n')
    ### error being printed for this is kindof weird



def run_tests():
    print('\n Test Files Exist\n')
    test_files_exist()
    print('\n Test Copy Files\n')
    test_copy_files()

run_tests()

