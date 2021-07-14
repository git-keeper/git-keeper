This is a working draft of an interface for a class `ActionRunner` which can run a sequence of actions to test a student submission.

## Constructor

The `ActionRunner` constructor has no required parameters. It has the following optional parameters:

* `timeout` (default `10`): Testing will run for at most `timeout` number of seconds, at which time it will kill the tests and print an error message.
* `timeout_message` (default `'Testing your submission took too long. Maybe you have an infinite loop?'`): The error message to print when there is a timeout.
* `memlimit` (default `1024`): Testing will use at most `memlimit` megabytes of memory, at which time it will kill the tests and print an error message.
* `memlimit_message` (default `'Testing your submission used too much memory.`'): The error message to print when testing uses too much memory.
* `working_dir` (defaults to the current working directory): The path to the directory in which to run the tests.
* `submission_dir` (defaults to `sys.argv[1]`): The path to the directory containing the student's submission.

## Action Methods

These methods add actions to the `ActionRunner`'s internal list of actions. The actions will not be run immediately, but they will be run in the order in which they are added.

* `files_exist(required_files, optional_files=None, error_message='Error: {0} does not exist.', warning_message='Warning: {0} does not exist.')`: Check that files exist in `submission_dir`
    * `required_files`: An iterable containing filenames relative to `submission_dir` which must exist. If any do not exist, an error message is printed and all action halts.
    * `optional_files`: An optional iterable containing filenames relative to `submission_dir` for which a warning will be printed if any of the files do not exist. Action will not halt.
    * `error_message`: The error message to print if a required file does not exist. Must contain `{}` or `{0}` so that the filename can be inserted with `error_message.format(filename)`.
    * `warning_message`: The warning message to print if an optional file does not exist. Must contain `{}` or `{0}` so that the filename can be inserted with `error_message.format(filename)`.
* `copy_files(filenames, dest=None)`: Copy files from `submission_dir`
    * `filenames`: An iterable containing relative paths to the filenames to copy from `submission_dir`
    * `dest`: The directory to copy into. This will be `working_dir` if not provided. If provided it will be treated as a relative path to `working_dir` which will be created if it does not already exist.
* `copy_dirs(directories, dest=None)`: Copy directories from `submission_dir`
    * `directories`: An iterable containing relative paths to the directories to copy from `submission_dir`
    * `dest`: The directory to copy into. This will be `working_dir` if not provided. If provided it will be treated as a relative path to `working_dir` which will be created if it does not already exist.
* `run_command(command, output=True, error_is_fatal=True, error_message='Error running tests:\n\n{0}')`: Run a shell command
    * `command`: The command to run as a list or a string
    * `output`: If True, print the output of the command. If False, do nothing with the output. If it is a string, treat it as a filename relative to `working_dir` and write the output to that file
    * `bad_output_pattern`: A regular expression suitable for Python's `re` module. If the pattern matches, treat it the same as if the command exited with a non-zero status
    * `error_is_fatal`: If True and the command returns a non-zero exit code, halt all actions
    * `error_message`: The error message to print if the command returns a non-zero exit code. If the command contains a formatting specifier (`{}` or `{0}`) then the output of the command will be inserted into the message.
* `diff(filename1, filename2, output=False, different_is_fatal=True, different_message='', same_message='', directory=None)`: Determine if the contents of 2 files are different or the same
    * `filename1`: Relative path of the first file
    * `filename2`: Relative path of the second file
    * `output`: Throws the output away if false, prints it if True, writes it to a file if it is a string
    * `different_is_fatal`: If True, all actions will halt if the files are different
    * `different_message`: Message to print if the files' contents are different
    * `same_message`: Message to print if the files' contents are the same
* `search(pattern, filename, dir=None)`: Try to match a regular expression against the contents of a file
    * `pattern`: A regular expression suitable for use with the Python's `re` module
    * `filename`: The relative path of the file in which to search
    * `dir`: The path of the directory where the file resides. Uses `working_dir` if not provided.
    * TODO: optional parameters to define behavior on a match or mismatch

## Run Method

After calling one or more action methods, call `run()` to actually run all the actions.

* `run(success_message='All tests passed!')`
    * `success_message`: The message to print if all actions have been run with no errors