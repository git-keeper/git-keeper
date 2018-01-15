from gkeepcore.action_runner import ActionRunner
from gkeepcore.shell_command import run_command
import os
import sys


# These files must exist in the student's repository
file_which_should_exist = ['test_text.txt', 'test_text2.txt']


runner = ActionRunner()
runner.files_exist(file_which_should_exist, error='Error: {0} does not exist.')

# Run all the actions. If there are no errors, print the success message.
# Otherwise the errors will be printed
runner.run(success_message='All tests passed!')