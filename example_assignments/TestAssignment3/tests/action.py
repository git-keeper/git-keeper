from gkeepcore.action_runner import ActionRunner


# These files must exist in the student's repository
student_files = ['string_student.h', 'string_student.c']

# Error messages for timeouts or exceeding memory limits
timeout_error = 'Testing took too long. Maybe you have an infinte loop?'
memlimit_error = 'Your submission used too much memory.'

# Create a new ActionRunner to which we will add actions
runner = ActionRunner(timeout=10, timeout_error=timeout_error,
                      memlimit=1024, memlimit_error=memlimit_error)

# Add an action to check that the student files exist. If any do not exist, an
# error_message will be printed with the name of the file substituted for {0}
runner.files_exist(student_files, error='{0} does not exist.')

# Action to copy the student's files into the test directory
runner.copy_files(student_files)

# Actino to build everything
runner.run_command('make', error_message='Your code does not compile '
                                         'correctly with my tests:\n\n{0}')

# For these tests, any output is bad output, so if we match any characters in
# the output it's an error_message.
bad_output = '.+'

# Action to run the test program. If the pattern in bad_output matches the
# output, print error_message with the output substituted for {0}
runner.run_command('./string_tests', bad_output=bad_output,
                   error_message='There were errors:\n\n{0}')

# Run all the actions. If there are no errors, print the success message.
# Otherwise the errors will be printed
runner.run(success_message='All tests passed!')