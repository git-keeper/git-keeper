from gkeepcore.action_runner import ActionRunner

# These files must exist in the student's repository
file_which_should_exist = ['test_text.txt', 'test_text2.txt']
optional_files = ['test_optional.txt', 'test_optional2.txt']


dest = '/Users/Vajpeyi/Documents/git-keeper/tests/test_action_runner' \
    '/test_assignments/copy_files/TEMP_FILE'

runner = ActionRunner()
runner.copy_files(file_which_should_exist, optional_files, dest)
runner.run(success_message='All tests passed!')