from gkeepcore.action_runner import ActionRunner

dest = '/Users/Vajpeyi/Documents/git-keeper/tests/test_action_runner' \
    '/test_assignments/copy_files/TEMP_FILE'
file_which_should_exist = ['test_text.txt', 'test_text2.txt']
runner = ActionRunner()
runner.copy_files(file_which_should_exist, dest=dest)

runner.run(success_message='All tests passed!')


