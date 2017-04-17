from gkeepcore.action_runner import ActionRunner


# These files must exist in the student's repository
file_which_should_exist = ['test_text.txt', 'test_text2.txt']
optional_files = ['test_optional.txt', 'test_optional2.txt']


runner = ActionRunner()
runner.files_exist(file_which_should_exist, optional_files, error='{0} does '
                                                                 'not exist.')
runner.run(success_message='All tests passed!')