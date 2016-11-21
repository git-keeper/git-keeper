from actionRunner import ActionRunner

# Possible interface for an assignment testing framework

# This example is for a C assignment where the student must have the files
# triangle.h and triangle.c in their repository. Those files are copied to the
# test directory and their files are built against my tests with make. My tests
# produce no output if all tests passed.

# These files must exist in the student's repository
student_files = ['triangle.h', 'triangle.c']

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
runner.run_command('make', error='Your code does not compile correctly with my tests:\n\n{0}')

# For these tests, any output is bad output, so if we match any characters in
# the output it's an error_message.
bad_output = '.+'

# Action to run the test program. If the pattern in bad_output matches the
# output, print error_message with the output substituted for {0}
runner.run_command('./triangle_tests', bad_output=bad_output,
                   error='There were errors:\n\n{0}')

# Run all the actions. If there are no errors, print the success message.
# Otherwise the errors will be printed
runner.run(success='All tests passed!')