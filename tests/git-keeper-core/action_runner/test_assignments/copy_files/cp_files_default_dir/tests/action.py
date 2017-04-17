from gkeepcore.action_runner import ActionRunner
from gkeepcore.shell_command import run_command
import os
import sys


# These files must exist in the student's repository
file_which_should_exist = ['test_text.txt', 'test_text2.txt']


# submission_dir = sys.argv #to get the submission dir of student
#
#
# # Error messages for timeouts or exceeding memory limits
# timeout_error = 'Testing took too long. Maybe you have an infinte loop?'
# memlimit_error = 'Your submission used too much memory.'

# Create a new ActionRunner to which we will add actions
runner = ActionRunner()

# Add an action to check that the student files exist. If any do not exist, an
# error_message will be printed with the name of the file substituted for {0}
runner.files_exist(file_which_should_exist, error='{0} does not exist.')

# Run all the actions. If there are no errors, print the success message.
# Otherwise the errors will be printed
runner.run(success_message='All tests passed!')